import org.apache.spark.sql.api.java.UDF3;

public class ThalesCrdpRevealIntegerByColumnWithUserUdf implements UDF3<Integer, String, String, Integer> {
    private static final long serialVersionUID = 1L;

    @Override
    public Integer call(Integer value, String columnName, String revealUser) throws Exception {
        return ThalesSparkNumericUdfSupport.revealIntegerByColumnWithUser(value, columnName, revealUser);
    }
}
