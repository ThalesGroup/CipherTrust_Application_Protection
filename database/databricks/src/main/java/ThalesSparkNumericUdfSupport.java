import java.math.BigDecimal;

public final class ThalesSparkNumericUdfSupport {

    private ThalesSparkNumericUdfSupport() {
    }

    public static Integer protectIntegerByColumn(Integer value, String columnName) throws Exception {
        if (value == null) {
            return null;
        }
        return Integer.valueOf(
                ThalesDataBricksCRDPFPE.thales_crdp_udf(String.valueOf(value), "protect", "nbr", columnName));
    }

    public static Integer revealIntegerByColumnWithUser(Integer value, String columnName, String revealUser) throws Exception {
        if (value == null) {
            return null;
        }
        return Integer.valueOf(
                ThalesDataBricksCRDPFPE.thales_crdp_udf(String.valueOf(value), "reveal", "nbr", columnName, revealUser));
    }

    public static Long protectLongByColumn(Long value, String columnName) throws Exception {
        if (value == null) {
            return null;
        }
        return Long.valueOf(
                ThalesDataBricksCRDPFPE.thales_crdp_udf(String.valueOf(value), "protect", "nbr", columnName));
    }

    public static Long revealLongByColumnWithUser(Long value, String columnName, String revealUser) throws Exception {
        if (value == null) {
            return null;
        }
        return Long.valueOf(
                ThalesDataBricksCRDPFPE.thales_crdp_udf(String.valueOf(value), "reveal", "nbr", columnName, revealUser));
    }

    public static BigDecimal protectDecimalByColumn(BigDecimal value, String columnName) throws Exception {
        if (value == null) {
            return null;
        }
        return new BigDecimal(
                ThalesDataBricksCRDPFPE.thales_crdp_udf(value.toPlainString(), "protect", "nbr", columnName));
    }

    public static BigDecimal revealDecimalByColumnWithUser(BigDecimal value, String columnName, String revealUser) throws Exception {
        if (value == null) {
            return null;
        }
        return new BigDecimal(
                ThalesDataBricksCRDPFPE.thales_crdp_udf(value.toPlainString(), "reveal", "nbr", columnName, revealUser));
    }
}
