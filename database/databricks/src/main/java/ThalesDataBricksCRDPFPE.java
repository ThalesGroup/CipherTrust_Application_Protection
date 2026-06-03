import java.util.List;

public class ThalesDataBricksCRDPFPE {

    /*
     * Keeps the original scalar UDF signature, but now delegates to the bulk
     * service so the same profile-resolution and per-column bulk logic is reused.
     */
    private static final ThalesDataBricksCRDPBulkService BULK_SERVICE = new ThalesDataBricksCRDPBulkService();
    private static final ThalesLogger LOG = ThalesLogger.get(ThalesDataBricksCRDPFPE.class);

    public static void main(String[] args) throws Exception {
        //String request = "M9wo";
        String request = "can you protectg this ";

        LOG.info("crdp_scalar_demo_start", "mode", "protect", "datatype", "char", "column", "email");
        LOG.info("crdp_scalar_demo_result", "variant", "column-aware");
        thales_crdp_udf(request, "protect", "char", "email");
        LOG.info("crdp_scalar_demo_result", "variant", "legacy");
        thales_crdp_udf(request, "protect", "char");
    }

    public static String thales_crdp_udf(String databricksInputData, String mode, String dataType) throws Exception {
        return thales_crdp_udf(databricksInputData, mode, dataType, null);
    }

    public static String thales_crdp_udf(
            String databricksInputData,
            String mode,
            String dataType,
            String columnName) throws Exception {
        return BULK_SERVICE.transformValue(databricksInputData, mode, columnName, dataType);
    }

    public static String thales_crdp_udf(
            String databricksInputData,
            String mode,
            String dataType,
            String columnName,
            String revealUser) throws Exception {
        return BULK_SERVICE.transformValue(databricksInputData, mode, columnName, dataType, revealUser);
    }

    public static String thales_crdp_reveal_udf_with_external_header(
            String databricksInputData,
            String externalHeaderValue,
            String dataType,
            String columnName,
            String revealUser) throws Exception {
        return BULK_SERVICE.revealValue(databricksInputData, externalHeaderValue, dataType, columnName, revealUser);
    }

    public static String thales_crdp_reveal_udf_with_external_header(
            String databricksInputData,
            String externalHeaderValue,
            String dataType,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        List<String> results = BULK_SERVICE.revealValues(
                java.util.Collections.singletonList(databricksInputData),
                java.util.Collections.singletonList(externalHeaderValue),
                objectName,
                dataType,
                columnName,
                revealUser);
        return results.isEmpty() ? databricksInputData : results.get(0);
    }

    public static ThalesDataBricksCRDPBulkService.ProtectResult thales_crdp_protect_udf_with_external_header(
            String databricksInputData,
            String dataType,
            String columnName) throws Exception {
        return BULK_SERVICE.protectValueWithExternalHeader(databricksInputData, dataType, columnName);
    }

    public static ThalesDataBricksCRDPBulkService.ProtectResult thales_crdp_protect_udf_with_external_header(
            String databricksInputData,
            String dataType,
            String objectName,
            String columnName) throws Exception {
        List<ThalesDataBricksCRDPBulkService.ProtectResult> results = BULK_SERVICE.protectValuesWithExternalHeaders(
                java.util.Collections.singletonList(databricksInputData),
                objectName,
                dataType,
                columnName);
        return results.isEmpty() ? new ThalesDataBricksCRDPBulkService.ProtectResult(databricksInputData, null) : results.get(0);
    }

    public static List<String> thales_crdp_udf_bulk(
            List<String> databricksInputData,
            String mode,
            String dataType,
            String columnName) throws Exception {
        return BULK_SERVICE.transformValues(databricksInputData, mode, columnName, dataType);
    }

    public static List<String> thales_crdp_udf_bulk(
            List<String> databricksInputData,
            String mode,
            String dataType,
            String columnName,
            String revealUser) throws Exception {
        return BULK_SERVICE.transformValues(databricksInputData, mode, columnName, dataType, revealUser);
    }

    public static String thales_crdp_udf(
            String databricksInputData,
            String mode,
            String dataType,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return BULK_SERVICE.transformValue(databricksInputData, mode, objectName, columnName, dataType, revealUser);
    }

    public static List<String> thales_crdp_udf_bulk(
            List<String> databricksInputData,
            String mode,
            String dataType,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return BULK_SERVICE.transformValues(databricksInputData, mode, objectName, columnName, dataType, revealUser);
    }

    public static List<String> thales_crdp_protect_udf_bulk(
            List<String> databricksInputData,
            String dataType,
            String objectName,
            String columnName) throws Exception {
        return BULK_SERVICE.protectValues(databricksInputData, objectName, dataType, columnName);
    }

    public static List<ThalesDataBricksCRDPBulkService.ProtectResult> thales_crdp_protect_udf_bulk_with_external_headers(
            List<String> databricksInputData,
            String dataType,
            String objectName,
            String columnName) throws Exception {
        return BULK_SERVICE.protectValuesWithExternalHeaders(databricksInputData, objectName, dataType, columnName);
    }

    public static List<String> thales_crdp_reveal_udf_bulk_with_external_headers(
            List<String> databricksInputData,
            List<String> externalHeaderValues,
            String dataType,
            String columnName,
            String revealUser) throws Exception {
        return BULK_SERVICE.revealValues(databricksInputData, externalHeaderValues, dataType, columnName, revealUser);
    }

    public static List<String> thales_crdp_reveal_udf_bulk_with_external_headers(
            List<String> databricksInputData,
            List<String> externalHeaderValues,
            String dataType,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return BULK_SERVICE.revealValues(databricksInputData, externalHeaderValues, objectName, dataType, columnName, revealUser);
    }
}
