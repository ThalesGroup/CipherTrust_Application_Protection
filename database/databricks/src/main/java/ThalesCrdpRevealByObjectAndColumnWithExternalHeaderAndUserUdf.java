import org.apache.spark.sql.api.java.UDF6;

public class ThalesCrdpRevealByObjectAndColumnWithExternalHeaderAndUserUdf
        implements UDF6<String, String, String, String, String, String, String> {
    private static final long serialVersionUID = 1L;

    @Override
    public String call(
            String value,
            String externalHeaderValue,
            String dataType,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        return ThalesDataBricksCRDPFPE.thales_crdp_reveal_udf_with_external_header(
                value,
                externalHeaderValue,
                dataType,
                objectName,
                columnName,
                revealUser);
    }
}
