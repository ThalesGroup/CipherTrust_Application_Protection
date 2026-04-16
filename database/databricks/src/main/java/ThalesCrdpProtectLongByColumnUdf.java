import org.apache.spark.sql.api.java.UDF2;

public class ThalesCrdpProtectLongByColumnUdf implements UDF2<Long, String, Long> {
    private static final long serialVersionUID = 1L;

    @Override
    public Long call(Long value, String columnName) throws Exception {
        return ThalesSparkNumericUdfSupport.protectLongByColumn(value, columnName);
    }
}
