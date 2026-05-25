import java.util.List;

import org.apache.spark.sql.api.java.UDF5;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public class ThalesCrdpRevealBulkByObjectAndColumnWithUserUdf
        implements UDF5<Seq<String>, String, String, String, String, List<String>> {
    private static final long serialVersionUID = 1L;

    @Override
    public List<String> call(
            Seq<String> values,
            String dataType,
            String objectName,
            String columnName,
            String revealUser) throws Exception {
        if (values == null) {
            return null;
        }
        List<String> data = JavaConverters.seqAsJavaListConverter(values).asJava();
        return ThalesDataBricksCRDPFPE.thales_crdp_udf_bulk(data, "reveal", dataType, objectName, columnName, revealUser);
    }
}
