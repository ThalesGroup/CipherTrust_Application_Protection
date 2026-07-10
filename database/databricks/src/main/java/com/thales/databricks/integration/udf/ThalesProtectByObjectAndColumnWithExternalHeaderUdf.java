package com.thales.databricks.integration.udf;

import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.api.java.UDF4;

import com.thales.databricks.integration.service.JavaCrdpService;
import com.thales.databricks.integration.service.ProtectResult;

public final class ThalesProtectByObjectAndColumnWithExternalHeaderUdf
        implements UDF4<String, String, String, String, Row> {

    @Override
    public Row call(String value, String datatype, String objectName, String columnName) throws Exception {
        ProtectResult result = JavaCrdpService.getInstance()
                .protectValueWithExternalHeader(value, datatype, objectName, columnName);
        return RowFactory.create(result.getProtectedValue(), result.getExternalHeader());
    }
}
