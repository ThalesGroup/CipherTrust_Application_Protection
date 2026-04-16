import org.apache.spark.sql.api.java.UDF3;

public class ThalesCrdpRevealWithUserUdf implements UDF3<String, String, String, String> {
    private static final long serialVersionUID = 1L;

    @Override
    public String call(String value, String dataType, String revealUser) throws Exception {
        return ThalesDataBricksCRDPFPE.thales_crdp_udf(value, "reveal", dataType, null, revealUser);
    }
}
