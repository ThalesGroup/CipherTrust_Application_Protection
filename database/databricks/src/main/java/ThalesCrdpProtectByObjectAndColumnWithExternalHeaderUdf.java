import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.api.java.UDF4;

public class ThalesCrdpProtectByObjectAndColumnWithExternalHeaderUdf implements UDF4<String, String, String, String, Row> {
    private static final long serialVersionUID = 1L;

    @Override
    public Row call(String value, String dataType, String objectName, String columnName) throws Exception {
        ThalesDataBricksCRDPBulkService.ProtectResult result =
                ThalesDataBricksCRDPFPE.thales_crdp_protect_udf_with_external_header(value, dataType, objectName, columnName);
        return RowFactory.create(result.getProtectedValue(), result.getExternalHeader());
    }
}
