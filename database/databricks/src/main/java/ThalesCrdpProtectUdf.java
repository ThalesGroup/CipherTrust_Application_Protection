import org.apache.spark.sql.api.java.UDF2;

public class ThalesCrdpProtectUdf implements UDF2<String, String, String> {
    private static final long serialVersionUID = 1L;

    @Override
    public String call(String value, String dataType) throws Exception {
        return ThalesDataBricksCRDPFPE.thales_crdp_udf(value, "protect", dataType);
    }
}
