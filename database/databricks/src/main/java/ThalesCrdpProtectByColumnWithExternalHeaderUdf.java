import org.apache.spark.sql.Row;
import org.apache.spark.sql.api.java.UDF3;
import org.apache.spark.sql.catalyst.expressions.GenericRowWithSchema;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.Metadata;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;

public class ThalesCrdpProtectByColumnWithExternalHeaderUdf implements UDF3<String, String, String, Row> {
    private static final long serialVersionUID = 1L;
    private static final StructType RESULT_SCHEMA = new StructType(new StructField[] {
            new StructField("protected_value", DataTypes.StringType, true, Metadata.empty()),
            new StructField("external_header", DataTypes.StringType, true, Metadata.empty())
    });

    @Override
    public Row call(String value, String dataType, String columnName) throws Exception {
        ThalesDataBricksCRDPBulkService.ProtectResult result =
                ThalesDataBricksCRDPFPE.thales_crdp_protect_udf_with_external_header(value, dataType, columnName);
        return new GenericRowWithSchema(
                new Object[] { result.getProtectedValue(), result.getExternalHeader() },
                RESULT_SCHEMA);
    }
}
