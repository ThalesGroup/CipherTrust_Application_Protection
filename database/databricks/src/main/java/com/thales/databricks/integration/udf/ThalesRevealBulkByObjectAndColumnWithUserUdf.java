package com.thales.databricks.integration.udf;

import java.util.List;

import org.apache.spark.sql.api.java.UDF5;

import com.thales.databricks.integration.service.JavaCrdpService;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public final class ThalesRevealBulkByObjectAndColumnWithUserUdf
        implements UDF5<Seq<String>, String, String, String, String, List<String>> {

    @Override
    public List<String> call(
            Seq<String> protectedValues,
            String datatype,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return JavaCrdpService.getInstance().revealValues(
                JavaConverters.seqAsJavaList(protectedValues),
                datatype,
                objectName,
                columnName,
                revealUser);
    }
}
