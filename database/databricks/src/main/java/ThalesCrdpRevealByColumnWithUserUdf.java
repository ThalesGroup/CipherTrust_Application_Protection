import org.apache.spark.sql.api.java.UDF4;

public class ThalesCrdpRevealByColumnWithUserUdf implements UDF4<String, String, String, String, String> {
    private static final long serialVersionUID = 1L;

    @Override
    public String call(String value, String dataType, String columnName, String revealUser) throws Exception {
        return ThalesDataBricksCRDPFPE.thales_crdp_udf(value, "reveal", dataType, columnName, revealUser);
    }
}
