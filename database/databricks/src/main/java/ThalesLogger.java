import java.io.PrintWriter;
import java.io.StringWriter;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

public final class ThalesLogger {

    public enum Level {
        ERROR,
        WARN,
        INFO,
        DEBUG;

        static Level parse(String value) {
            if (value == null || value.trim().isEmpty()) {
                return INFO;
            }
            try {
                return Level.valueOf(value.trim().toUpperCase(Locale.ROOT));
            } catch (IllegalArgumentException ex) {
                return INFO;
            }
        }
    }

    private final String component;
    private final Level minimumLevel;
    private final String format;
    private final boolean includeStacktrace;
    private final String loggerName;

    private ThalesLogger(
            String component,
            Level minimumLevel,
            String format,
            boolean includeStacktrace,
            String loggerName) {
        this.component = component;
        this.minimumLevel = minimumLevel;
        this.format = format == null ? "kv" : format.trim().toLowerCase(Locale.ROOT);
        this.includeStacktrace = includeStacktrace;
        this.loggerName = loggerName;
    }

    public static ThalesLogger get(Class<?> owner) {
        return get(ThalesDataBricksUdfConfig.load(), owner);
    }

    public static ThalesLogger get(ThalesDataBricksUdfConfig config, Class<?> owner) {
        String loggerName = owner == null ? "UnknownClass" : owner.getSimpleName();
        return new ThalesLogger(
                config.getAppLogComponent(),
                config.getAppLogLevel(),
                config.getAppLogFormat(),
                config.isAppLogIncludeStacktrace(),
                loggerName);
    }

    public void debug(String event, String... keyValues) {
        log(Level.DEBUG, event, null, keyValues);
    }

    public void info(String event, String... keyValues) {
        log(Level.INFO, event, null, keyValues);
    }

    public void warn(String event, String... keyValues) {
        log(Level.WARN, event, null, keyValues);
    }

    public void warn(String event, Throwable error, String... keyValues) {
        log(Level.WARN, event, error, keyValues);
    }

    public void error(String event, Throwable error, String... keyValues) {
        log(Level.ERROR, event, error, keyValues);
    }

    private void log(Level level, String event, Throwable error, String... keyValues) {
        if (!isEnabled(level)) {
            return;
        }

        Map<String, String> fields = new LinkedHashMap<>();
        fields.put("level", level.name());
        fields.put("component", component);
        fields.put("logger", loggerName);
        fields.put("event", defaultValue(event, "log"));
        fields.put("ts", Instant.now().toString());

        if (keyValues != null) {
            for (int i = 0; i + 1 < keyValues.length; i += 2) {
                putIfPresent(fields, keyValues[i], keyValues[i + 1]);
            }
        }

        if (error != null) {
            fields.put("exception", error.getClass().getSimpleName());
            putIfPresent(fields, "error_message", safeValue(error.getMessage()));
        }

        String rendered = "json".equals(format)
                ? toJsonLine(fields)
                : toKeyValueLine(fields);

        if (level == Level.ERROR) {
            System.err.println(rendered);
            if (includeStacktrace && error != null) {
                System.err.println(stackTrace(error));
            }
            return;
        }

        System.out.println(rendered);
        if (includeStacktrace && error != null) {
            System.out.println(stackTrace(error));
        }
    }

    private boolean isEnabled(Level level) {
        return level.ordinal() <= minimumLevel.ordinal();
    }

    private static void putIfPresent(Map<String, String> fields, String key, String value) {
        if (key == null || key.trim().isEmpty()) {
            return;
        }
        if (value == null || value.trim().isEmpty()) {
            return;
        }
        fields.put(key.trim(), safeValue(value));
    }

    private static String toKeyValueLine(Map<String, String> fields) {
        StringBuilder sb = new StringBuilder("[THALES-UDF]");
        for (Map.Entry<String, String> entry : fields.entrySet()) {
            sb.append(' ')
                    .append(entry.getKey())
                    .append('=')
                    .append(quoteIfNeeded(entry.getValue()));
        }
        return sb.toString();
    }

    private static String toJsonLine(Map<String, String> fields) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, String> entry : fields.entrySet()) {
            if (!first) {
                sb.append(',');
            }
            first = false;
            sb.append('"')
                    .append(escapeJson(entry.getKey()))
                    .append("\":\"")
                    .append(escapeJson(entry.getValue()))
                    .append('"');
        }
        sb.append('}');
        return sb.toString();
    }

    private static String quoteIfNeeded(String value) {
        if (value == null) {
            return "\"\"";
        }
        if (value.indexOf(' ') >= 0 || value.indexOf('=') >= 0 || value.indexOf('"') >= 0) {
            return "\"" + value.replace("\"", "'") + "\"";
        }
        return value;
    }

    private static String stackTrace(Throwable error) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        error.printStackTrace(pw);
        pw.flush();
        return sw.toString();
    }

    private static String escapeJson(String value) {
        return value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\r", "\\r")
                .replace("\n", "\\n")
                .replace("\t", "\\t");
    }

    private static String safeValue(String value) {
        if (value == null) {
            return null;
        }
        return value.replace('\r', ' ').replace('\n', ' ').trim();
    }

    private static String defaultValue(String value, String fallback) {
        return value == null || value.trim().isEmpty() ? fallback : value.trim();
    }
}
