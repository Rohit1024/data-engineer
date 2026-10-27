"""Lesson 0017. Verify threshold state remains scoped to key and window."""
from typing import Tuple

import apache_beam as beam
from apache_beam.coders import VarIntCoder
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.testing.test_stream import TestStream
from apache_beam.testing.util import assert_that, equal_to
from apache_beam.transforms import window
from apache_beam.transforms.timeutil import TimeDomain
from apache_beam.transforms.userstate import ReadModifyWriteStateSpec, TimerSpec, on_timer


class Threshold(beam.DoFn):
    TOTAL = ReadModifyWriteStateSpec("total", VarIntCoder())
    SENT = ReadModifyWriteStateSpec("sent", VarIntCoder())
    EXPIRE = TimerSpec("expire", TimeDomain.WATERMARK)

    def process(self, item, window=beam.DoFn.WindowParam,
                total=beam.DoFn.StateParam(TOTAL),
                sent=beam.DoFn.StateParam(SENT),
                timer=beam.DoFn.TimerParam(EXPIRE)):
        key, cents = item
        updated = (total.read() or 0) + cents
        total.write(updated)
        timer.set(window.end)
        if updated >= 100000 and not sent.read():
            sent.write(1)
            yield key, updated

    @on_timer(EXPIRE)
    def expire(self, total=beam.DoFn.StateParam(TOTAL),
               sent=beam.DoFn.StateParam(SENT)):
        total.clear()
        sent.clear()


events = (TestStream()
          .advance_watermark_to(0)
          .add_elements([
              window.TimestampedValue(("m1", 60000), 1),
              window.TimestampedValue(("m1", 50000), 2),
              window.TimestampedValue(("m1", 10000), 3),
              window.TimestampedValue(("m2", 100001), 4),
              window.TimestampedValue(("m1", 100002), 3601),
          ])
          .advance_watermark_to(7201)
          .advance_watermark_to_infinity())
options = PipelineOptions()
options.view_as(StandardOptions).streaming = True
with beam.Pipeline(options=options) as pipeline:
    alerts = (pipeline
              | events
              | beam.Map(lambda item: item).with_output_types(Tuple[str, int])
              | beam.WindowInto(window.FixedWindows(3600), allowed_lateness=0)
              | beam.ParDo(Threshold()))
    def alert_identity(item, window=beam.DoFn.WindowParam):
        key, observed_cents = item
        assert observed_cents >= 100000
        return key, int(window.start)

    identities = alerts | "Alert identity" >> beam.Map(alert_identity)
    assert_that(identities, equal_to([
        ("m1", 0), ("m2", 0), ("m1", 3600),
    ]))
