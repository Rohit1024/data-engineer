"""Lesson 0014. Run with the pinned local Beam environment in the lesson."""
import apache_beam as beam
from apache_beam.testing.util import assert_that, equal_to

with beam.Pipeline() as pipeline:
    totals = (
        pipeline
        | "Orders" >> beam.Create([("m1", 2500), ("m1", 4200), ("m2", 1000)])
        | "Positive amounts" >> beam.Filter(lambda item: item[1] >= 0)
        | "Sum cents" >> beam.CombinePerKey(sum)
    )
    assert_that(totals, equal_to([("m1", 6700), ("m2", 1000)]))
