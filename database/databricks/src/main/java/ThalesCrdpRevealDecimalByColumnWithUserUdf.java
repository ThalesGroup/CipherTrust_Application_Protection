import java.math.BigDecimal;

import org.apache.spark.sql.api.java.UDF3;

public class ThalesCrdpRevealDecimalByColumnWithUserUdf implements UDF3<BigDecimal, String, String, BigDecimal> {
    private static final long serialVersionUID = 1L;

    @Override
    public BigDecimal call(BigDecimal value, String columnName, String revealUser) throws Exception {
        return ThalesSparkNumericUdfSupport.revealDecimalByColumnWithUser(value, columnName, revealUser);
    }
}
