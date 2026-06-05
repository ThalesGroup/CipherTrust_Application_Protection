import java.util.ArrayList;
import java.util.List;

import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.api.java.UDF4;

import scala.collection.JavaConverters;
import scala.collection.Seq;

public class ThalesCrdpProtectBulkByObjectAndColumnWithExternalHeaderUdf
        implements UDF4<Seq<String>, String, String, String, List<Row>> {
    private static final long serialVersionUID = 1L;

    @Override
    public List<Row> call(
            Seq<String> values,
            String dataType,
            String objectName,
            String columnName) throws Exception {
        if (values == null) {
            return null;
        }
        List<String> data = JavaConverters.seqAsJavaListConverter(values).asJava();
        List<ThalesDataBricksCRDPBulkService.ProtectResult> results =
                ThalesDataBricksCRDPFPE.thales_crdp_protect_udf_bulk_with_external_headers(
                        data,
                        dataType,
                        objectName,
                        columnName);

        List<Row> rows = new ArrayList<>(results.size());
        for (ThalesDataBricksCRDPBulkService.ProtectResult result : results) {
            rows.add(RowFactory.create(result.getProtectedValue(), result.getExternalHeader()));
        }
        return rows;
    }
}
