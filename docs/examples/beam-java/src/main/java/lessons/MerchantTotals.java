package lessons;

import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.testing.PAssert;
import org.apache.beam.sdk.transforms.Create;
import org.apache.beam.sdk.transforms.Sum;
import org.apache.beam.sdk.values.KV;
import org.apache.beam.sdk.values.PCollection;

public final class MerchantTotals {
  public static void main(String[] args) {
    Pipeline pipeline = Pipeline.create();
    PCollection<KV<String, Long>> totals = pipeline
        .apply(Create.of(KV.of("m1", 2500L), KV.of("m1", 4200L), KV.of("m2", 1000L)))
        .apply(Sum.longsPerKey());
    PAssert.that(totals).containsInAnyOrder(KV.of("m1", 6700L), KV.of("m2", 1000L));
    pipeline.run().waitUntilFinish();
  }
}
