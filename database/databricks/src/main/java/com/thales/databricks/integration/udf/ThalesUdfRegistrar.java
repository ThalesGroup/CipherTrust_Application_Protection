package com.thales.databricks.integration.udf;

import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.Metadata;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;

public final class ThalesUdfRegistrar {

    private ThalesUdfRegistrar() {
    }

    public static void registerMinimalSurface(SparkSession spark) {
        StructType externalProtectSchema = new StructType(new StructField[] {
                new StructField("protected_value", DataTypes.StringType, true, Metadata.empty()),
                new StructField("external_header", DataTypes.StringType, true, Metadata.empty())
        });

        spark.udf().registerJava(
                "thales_protect_by_object_and_column",
                ThalesProtectByObjectAndColumnUdf.class.getName(),
                DataTypes.StringType);
        spark.udf().registerJava(
                "thales_reveal_by_object_and_column_with_user",
                ThalesRevealByObjectAndColumnWithUserUdf.class.getName(),
                DataTypes.StringType);
        spark.udf().registerJava(
                "thales_protect_by_object_and_column_with_external_header",
                ThalesProtectByObjectAndColumnWithExternalHeaderUdf.class.getName(),
                externalProtectSchema);
        spark.udf().registerJava(
                "thales_reveal_by_object_and_column_with_external_header_and_user",
                ThalesRevealByObjectAndColumnWithExternalHeaderAndUserUdf.class.getName(),
                DataTypes.StringType);
        spark.udf().registerJava(
                "thales_protect_bulk_by_object_and_column",
                ThalesProtectBulkByObjectAndColumnUdf.class.getName(),
                DataTypes.createArrayType(DataTypes.StringType));
        spark.udf().registerJava(
                "thales_reveal_bulk_by_object_and_column_with_user",
                ThalesRevealBulkByObjectAndColumnWithUserUdf.class.getName(),
                DataTypes.createArrayType(DataTypes.StringType));
        spark.udf().registerJava(
                "thales_protect_bulk_by_object_and_column_with_external_header",
                ThalesProtectBulkByObjectAndColumnWithExternalHeaderUdf.class.getName(),
                DataTypes.createArrayType(externalProtectSchema));
        spark.udf().registerJava(
                "thales_reveal_bulk_by_object_and_column_with_external_header_and_user",
                ThalesRevealBulkByObjectAndColumnWithExternalHeaderAndUserUdf.class.getName(),
                DataTypes.createArrayType(DataTypes.StringType));
    }
}
