package com.thales.databricks.integration.udf;

import java.util.List;

import org.apache.spark.sql.api.java.UDF6;

import com.thales.databricks.integration.service.JavaCrdpService;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public final class ThalesRevealBulkByObjectAndColumnWithExternalHeaderAndUserUdf
        implements UDF6<Seq<String>, Seq<String>, String, String, String, String, List<String>> {

    @Override
    public List<String> call(
            Seq<String> protectedValues,
            Seq<String> externalHeaders,
            String datatype,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return JavaCrdpService.getInstance().revealValuesWithExternalHeaders(
                JavaConverters.seqAsJavaList(protectedValues),
                datatype,
                objectName,
                columnName,
                revealUser,
                JavaConverters.seqAsJavaList(externalHeaders));
    }
}
