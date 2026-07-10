package com.thales.databricks.integration.udf;

import org.apache.spark.sql.api.java.UDF4;

import com.thales.databricks.integration.service.JavaCrdpService;

public final class ThalesProtectByObjectAndColumnUdf implements UDF4<String, String, String, String, String> {

    @Override
    public String call(String value, String datatype, String objectName, String columnName) throws Exception {
        return JavaCrdpService.getInstance().protectValue(value, datatype, objectName, columnName);
    }
}
