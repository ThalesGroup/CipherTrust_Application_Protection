package com.thales.databricks.integration.udf;

import java.util.List;

import org.apache.spark.sql.api.java.UDF4;

import com.thales.databricks.integration.service.JavaCrdpService;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public final class ThalesProtectBulkByObjectAndColumnUdf
        implements UDF4<Seq<String>, String, String, String, List<String>> {

    @Override
    public List<String> call(Seq<String> values, String datatype, String objectName, String columnName) throws Exception {
        return JavaCrdpService.getInstance().protectValues(
                JavaConverters.seqAsJavaList(values),
                datatype,
                objectName,
                columnName);
    }
}
