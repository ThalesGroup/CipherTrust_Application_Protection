package com.thales.databricks.integration.udf;

import org.apache.spark.sql.api.java.UDF6;

import com.thales.databricks.integration.service.JavaCrdpService;

public final class ThalesRevealByObjectAndColumnWithExternalHeaderAndUserUdf
        implements UDF6<String, String, String, String, String, String, String> {

    @Override
    public String call(
            String protectedValue,
            String externalHeader,
            String datatype,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return JavaCrdpService.getInstance().revealValueWithExternalHeader(
                protectedValue,
                externalHeader,
                datatype,
                objectName,
                columnName,
                revealUser);
    }
}
