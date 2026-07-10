package com.thales.databricks.integration.udf;

import java.util.ArrayList;
import java.util.List;

import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.api.java.UDF4;

import com.thales.databricks.integration.service.JavaCrdpService;
import com.thales.databricks.integration.service.ProtectResult;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public final class ThalesProtectBulkByObjectAndColumnWithExternalHeaderUdf
        implements UDF4<Seq<String>, String, String, String, List<Row>> {

    @Override
    public List<Row> call(Seq<String> values, String datatype, String objectName, String columnName) throws Exception {
        List<ProtectResult> results = JavaCrdpService.getInstance().protectValuesWithExternalHeaders(
                JavaConverters.seqAsJavaList(values),
                datatype,
                objectName,
                columnName);
        List<Row> rows = new ArrayList<>(results.size());
        for (ProtectResult result : results) {
            rows.add(RowFactory.create(result.getProtectedValue(), result.getExternalHeader()));
        }
        return rows;
    }
}
