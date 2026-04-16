import java.util.List;

import org.apache.spark.sql.api.java.UDF3;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public class ThalesCrdpRevealBulkWithUserUdf implements UDF3<Seq<String>, String, String, List<String>> {
    private static final long serialVersionUID = 1L;

    @Override
    public List<String> call(Seq<String> values, String dataType, String revealUser) throws Exception {
        if (values == null) {
            return null;
        }
        List<String> data = JavaConverters.seqAsJavaListConverter(values).asJava();
        return new ThalesDataBricksCRDPBulkService().revealValues(data, dataType, null, revealUser);
    }
}