import org.apache.spark.sql.api.java.UDF3;

public class ThalesCrdpRevealLongByColumnWithUserUdf implements UDF3<Long, String, String, Long> {
    private static final long serialVersionUID = 1L;

    @Override
    public Long call(Long value, String columnName, String revealUser) throws Exception {
        return ThalesSparkNumericUdfSupport.revealLongByColumnWithUser(value, columnName, revealUser);
    }
}
