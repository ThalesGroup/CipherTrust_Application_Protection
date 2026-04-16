import java.util.List;

import org.apache.spark.sql.api.java.UDF1;

import scala.collection.JavaConverters;
import scala.collection.Seq;

/*
 * Example Spark UDF adapter that accepts an array/Seq of numeric strings and
 * protects them in bulk. When this class is registered with Spark, Spark will
 * execute it on worker executors for the partitions being processed.
 */
public class ThalesBulkProtectNbrUdf implements UDF1<Seq<String>, List<String>> {
    private static final long serialVersionUID = 1L;

    @Override
    public List<String> call(Seq<String> inputBatch) throws Exception {
        if (inputBatch == null) {
            return null;
        }

        List<String> data = JavaConverters.seqAsJavaListConverter(inputBatch).asJava();
        return ThalesDataBricksCRDPFPE.thales_crdp_udf_bulk(data, "protect", "nbr", null);
    }
}
