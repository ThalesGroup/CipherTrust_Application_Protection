import org.apache.spark.sql.api.java.UDF5;

public class ThalesCrdpRevealByObjectAndColumnWithUserUdf implements UDF5<String, String, String, String, String, String> {
    private static final long serialVersionUID = 1L;

    @Override
    public String call(String value, String dataType, String objectName, String columnName, String revealUser) throws Exception {
        return ThalesDataBricksCRDPFPE.thales_crdp_udf(value, "reveal", dataType, objectName, columnName, revealUser);
    }
}
