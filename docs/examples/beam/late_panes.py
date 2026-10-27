"""Lesson 0016. Explicitly test retained late data and window expiration."""
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.testing.test_stream import TestStream
from apache_beam.testing.util import assert_that, equal_to
from apache_beam.transforms import trigger, window

events = (
    TestStream()
    .advance_watermark_to(0)
    .add_elements([window.TimestampedValue(("m1", 10), 1)])
    .advance_watermark_to(60)
    .add_elements([window.TimestampedValue(("m1", 20), 2)])
    .advance_watermark_to(121)
    .add_elements([window.TimestampedValue(("m1", 99), 3)])
    .advance_watermark_to_infinity()
)
options = PipelineOptions()
options.view_as(StandardOptions).streaming = True
with beam.Pipeline(options=options) as pipeline:
    totals = (
        pipeline
        | events
        | beam.WindowInto(
            window.FixedWindows(60),
            trigger=trigger.AfterWatermark(late=trigger.AfterCount(1)),
            allowed_lateness=60,
            accumulation_mode=trigger.AccumulationMode.ACCUMULATING,
        )
        | beam.CombinePerKey(sum)
    )
    assert_that(totals, equal_to([("m1", 10), ("m1", 30)]))
