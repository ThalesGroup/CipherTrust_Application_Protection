import java.util.List;

public class ThalesDataBricksCRDPFPE {

    /*
     * Keeps the original scalar UDF signature, but now delegates to the bulk
     * service so the same profile-resolution and per-column bulk logic is reused.
     */
    private static final ThalesDataBricksCRDPBulkService BULK_SERVICE = new ThalesDataBricksCRDPBulkService();

    public static void main(String[] args) throws Exception {
        //String request = "M9wo";
        String request = "can you protectg this ";
        
        System.out.println("input data = " + request);
        System.out.println("results = " + thales_crdp_udf(request, "protect", "char", "email"));
        System.out.println("results = " + thales_crdp_udf(request, "protect", "char"));
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
}
