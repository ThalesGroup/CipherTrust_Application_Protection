import org.apache.spark.sql.api.java.UDF4;

public class ThalesCrdpProtectByObjectAndColumnUdf implements UDF4<String, String, String, String, String> {
    private static final long serialVersionUID = 1L;

    @Override
    public String call(String value, String dataType, String objectName, String columnName) throws Exception {
        return ThalesDataBricksCRDPFPE.thales_crdp_udf(value, "protect", dataType, objectName, columnName, null);
    }
}
