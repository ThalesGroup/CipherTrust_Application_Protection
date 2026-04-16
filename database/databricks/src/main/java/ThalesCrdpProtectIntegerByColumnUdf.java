import org.apache.spark.sql.api.java.UDF2;

public class ThalesCrdpProtectIntegerByColumnUdf implements UDF2<Integer, String, Integer> {
    private static final long serialVersionUID = 1L;

    @Override
    public Integer call(Integer value, String columnName) throws Exception {
        return ThalesSparkNumericUdfSupport.protectIntegerByColumn(value, columnName);
    }
}
