import java.math.BigDecimal;

import org.apache.spark.sql.api.java.UDF2;

public class ThalesCrdpProtectDecimalByColumnUdf implements UDF2<BigDecimal, String, BigDecimal> {
    private static final long serialVersionUID = 1L;

    @Override
    public BigDecimal call(BigDecimal value, String columnName) throws Exception {
        return ThalesSparkNumericUdfSupport.protectDecimalByColumn(value, columnName);
    }
}
