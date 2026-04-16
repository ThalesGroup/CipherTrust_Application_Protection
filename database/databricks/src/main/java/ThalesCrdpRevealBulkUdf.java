import java.util.List;

import org.apache.spark.sql.api.java.UDF2;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public class ThalesCrdpRevealBulkUdf implements UDF2<Seq<String>, String, List<String>> {
    private static final long serialVersionUID = 1L;

    @Override
    public List<String> call(Seq<String> values, String dataType) throws Exception {
        if (values == null) {
            return null;
        }
        List<String> data = JavaConverters.seqAsJavaListConverter(values).asJava();
        return new ThalesDataBricksCRDPBulkService().revealValues(data, dataType);
    }
}