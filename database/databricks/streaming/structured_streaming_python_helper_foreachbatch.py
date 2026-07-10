# Databricks Structured Streaming examples for the current Python helper path.
#
# The helper API is batch-oriented, so the clean streaming fit is `foreachBatch`
# where each micro-batch is treated as a normal Spark DataFrame.
#
# Demo note:
# these examples use `availableNow=True` so they process the currently available
# source rows and then stop. That is much easier to validate with small demo
# tables than an always-on streaming query.

from thales_databricks_integration import (
    IntegrationConfig,
    protect_dataframe,
    reveal_dataframe,
)


CATALOG = "my_catalog"
SCHEMA = "my_schema"

PLAINTEXT_SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.plaintext_plaintext"
PROTECTED_INTERNAL_TARGET = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal_stream_helper"
PROTECTED_EXTERNAL_TARGET = f"{CATALOG}.{SCHEMA}.plaintext_protected_external_stream_helper"
REVEALED_INTERNAL_TARGET = f"{CATALOG}.{SCHEMA}.plaintext_revealed_internal_stream_helper"

INTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_internal"
EXTERNAL_OBJECT = f"{CATALOG}.{SCHEMA}.plaintext_protected_external"

INTERNAL_CHECKPOINT = (
    f"/Volumes/{CATALOG}/{SCHEMA}/volume_for_checkpoints/plaintext_protected_internal_stream_helper"
)
EXTERNAL_CHECKPOINT = (
    f"/Volumes/{CATALOG}/{SCHEMA}/volume_for_checkpoints/plaintext_protected_external_stream_helper"
)
REVEAL_CHECKPOINT = (
    f"/Volumes/{CATALOG}/{SCHEMA}/volume_for_checkpoints/plaintext_revealed_internal_stream_helper"
)


config = IntegrationConfig.from_runtime()
helper_options = {
    "api_version": "v2",
    "transport_mode": "real",
}


def write_internal_protect_batch(batch_df, batch_id):
    if batch_df.rdd.isEmpty():
        return
    protected_df = protect_dataframe(
        df=batch_df,
        object_name=INTERNAL_OBJECT,
        config=config,
        options=helper_options,
    )
    (
        protected_df.write.format("delta")
        .mode("append")
        .saveAsTable(PROTECTED_INTERNAL_TARGET)
    )


def write_external_protect_batch(batch_df, batch_id):
    if batch_df.rdd.isEmpty():
        return
    protected_df = protect_dataframe(
        df=batch_df,
        object_name=EXTERNAL_OBJECT,
        config=config,
        options=helper_options,
    )
    (
        protected_df.write.format("delta")
        .mode("append")
        .saveAsTable(PROTECTED_EXTERNAL_TARGET)
    )


def write_internal_reveal_batch(batch_df, batch_id):
    if batch_df.rdd.isEmpty():
        return
    revealed_df = reveal_dataframe(
        df=batch_df,
        object_name=INTERNAL_OBJECT,
        config=config,
        options=helper_options,
    )
    (
        revealed_df.write.format("delta")
        .mode("append")
        .saveAsTable(REVEALED_INTERNAL_TARGET)
    )


plaintext_stream = spark.readStream.table(PLAINTEXT_SOURCE_TABLE)

internal_protect_query = (
    plaintext_stream.writeStream.foreachBatch(write_internal_protect_batch)
    .trigger(availableNow=True)
    .outputMode("append")
    .option("checkpointLocation", INTERNAL_CHECKPOINT)
    .start()
)

external_protect_query = (
    plaintext_stream.writeStream.foreachBatch(write_external_protect_batch)
    .trigger(availableNow=True)
    .outputMode("append")
    .option("checkpointLocation", EXTERNAL_CHECKPOINT)
    .start()
)


# Optional governed reveal pattern:
# read already-protected internal rows as a stream and reveal inside
# `foreachBatch`. For production governance, many teams will still prefer
# downstream reads from a secured UC view instead.
#
# protected_internal_stream = spark.readStream.table(PROTECTED_INTERNAL_TARGET)
# internal_reveal_query = (
#     protected_internal_stream.writeStream
#     .foreachBatch(write_internal_reveal_batch)
#     .trigger(availableNow=True)
#     .outputMode("append")
#     .option("checkpointLocation", REVEAL_CHECKPOINT)
#     .start()
# )
#
# To stop:
# internal_protect_query.stop()
# external_protect_query.stop()
# internal_reveal_query.stop()
