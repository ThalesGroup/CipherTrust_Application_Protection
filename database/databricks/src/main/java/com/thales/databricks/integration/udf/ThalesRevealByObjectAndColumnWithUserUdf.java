package com.thales.databricks.integration.udf;

import org.apache.spark.sql.api.java.UDF5;

import com.thales.databricks.integration.service.JavaCrdpService;

public final class ThalesRevealByObjectAndColumnWithUserUdf
        implements UDF5<String, String, String, String, String, String> {

    @Override
    public String call(
            String protectedValue,
            String datatype,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return JavaCrdpService.getInstance().revealValue(
                protectedValue,
                datatype,
                objectName,
                columnName,
                revealUser);
    }
}
