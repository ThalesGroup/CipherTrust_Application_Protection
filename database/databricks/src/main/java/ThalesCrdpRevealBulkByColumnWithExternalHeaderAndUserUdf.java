import java.util.List;

import org.apache.spark.sql.api.java.UDF5;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public class ThalesCrdpRevealBulkByColumnWithExternalHeaderAndUserUdf
        implements UDF5<Seq<String>, Seq<String>, String, String, String, List<String>> {
    private static final long serialVersionUID = 1L;

    @Override
    public List<String> call(
            Seq<String> values,
            Seq<String> externalHeaderValues,
            String dataType,
            String columnName,
            String revealUser) throws Exception {
        if (values == null) {
            return null;
        }
        List<String> data = JavaConverters.seqAsJavaListConverter(values).asJava();
        List<String> headers = externalHeaderValues == null
                ? null
                : JavaConverters.seqAsJavaListConverter(externalHeaderValues).asJava();
        return ThalesDataBricksCRDPFPE.thales_crdp_reveal_udf_bulk_with_external_headers(
                data,
                headers,
                dataType,
                columnName,
                revealUser);
    }
}
