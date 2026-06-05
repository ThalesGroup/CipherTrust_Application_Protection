import java.util.List;

import org.apache.spark.sql.api.java.UDF4;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public class ThalesCrdpProtectBulkByObjectAndColumnUdf
        implements UDF4<Seq<String>, String, String, String, List<String>> {
    private static final long serialVersionUID = 1L;

    @Override
    public List<String> call(
            Seq<String> values,
            String dataType,
            String objectName,
            String columnName) throws Exception {
        if (values == null) {
            return null;
        }
        List<String> data = JavaConverters.seqAsJavaListConverter(values).asJava();
        return ThalesDataBricksCRDPFPE.thales_crdp_protect_udf_bulk(data, dataType, objectName, columnName);
    }
}
