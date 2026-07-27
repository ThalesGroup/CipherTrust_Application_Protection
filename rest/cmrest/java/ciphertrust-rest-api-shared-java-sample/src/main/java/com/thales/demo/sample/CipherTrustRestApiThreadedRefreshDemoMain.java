package com.thales.demo.sample;

import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public final class CipherTrustRestApiThreadedRefreshDemoMain {
    private CipherTrustRestApiThreadedRefreshDemoMain() {
    }

    public static void main(String[] args) throws Exception {
        Config config = Config.fromArgs(args);

        HttpClient client = CipherTrustRestSupport.buildHttpClient(config.insecureTls(), config.timeoutSeconds());
        CipherTrustRestSupport.ClientConfig clientConfig =
                new CipherTrustRestSupport.ClientConfig(
                        config.baseUrl(),
                        config.username(),
                        config.password(),
                        config.basicAuth(),
                        List.of("myapp", "cli"),
                        config.timeoutSeconds(),
                        config.debug(),
                        config.maxBusinessRequestsPerToken(),
                        config.refreshSkewSecondsOverride());

        CipherTrustRestSupport.AuthTokenProvider authProvider =
                new CipherTrustRestSupport.AuthTokenProvider(client, clientConfig);

        printConfiguration(config);

        try (ExecutorService executor = Executors.newFixedThreadPool(config.threads())) {
            List<Future<WorkerResult>> futures = new ArrayList<>();
            for (int workerId = 1; workerId <= config.threads(); workerId++) {
                int currentWorkerId = workerId;
                futures.add(executor.submit(new Worker(
                        currentWorkerId,
                        client,
                        clientConfig,
                        authProvider,
                        config)));
            }

            int successCount = 0;
            int failureCount = 0;
            for (Future<WorkerResult> future : futures) {
                try {
                    WorkerResult result = future.get();
                    if (result.success()) {
                        successCount++;
                    } else {
                        failureCount++;
                    }
                } catch (ExecutionException ex) {
                    failureCount++;
                    Throwable cause = ex.getCause() == null ? ex : ex.getCause();
                    System.out.println("Worker failure: " + cause.getMessage());
                }
            }

            System.out.println();
            System.out.println("Threaded demo complete.");
            System.out.println("Workers succeeded: " + successCount);
            System.out.println("Workers failed   : " + failureCount);
            System.out.println("Expected behavior with shared token provider:");
            System.out.println("- one worker may trigger refresh when token enters the refresh window");
            System.out.println("- nearby workers should then reuse the refreshed token rather than all refreshing independently");
            System.out.println("- in-flight requests keep using the token they started with");
            System.out.println("- a 401 or token-expiry-style response still gets one refresh-and-retry attempt");
        }
    }

    private static void printConfiguration(Config config) {
        System.out.println("Threaded refresh demo configuration:");
        System.out.println("Start time                    : " + Instant.now());
        System.out.println("Threads                       : " + config.threads());
        System.out.println("Iterations per thread         : " + config.iterationsPerThread());
        System.out.println("Sleep before decrypt (sec)    : " + config.sleepSecondsBeforeDecrypt());
        System.out.println("Sleep between iterations (sec): " + config.sleepSecondsBetweenIterations());
        System.out.println("maxBusinessRequestsPerToken   : " + config.maxBusinessRequestsPerToken());
        System.out.println("refreshSkewSecondsOverride    : " + config.refreshSkewSecondsOverride());
        System.out.println();
    }

    private static final class Worker implements Callable<WorkerResult> {
        private final int workerId;
        private final HttpClient client;
        private final CipherTrustRestSupport.ClientConfig clientConfig;
        private final CipherTrustRestSupport.AuthTokenProvider authProvider;
        private final Config config;

        private Worker(int workerId,
                       HttpClient client,
                       CipherTrustRestSupport.ClientConfig clientConfig,
                       CipherTrustRestSupport.AuthTokenProvider authProvider,
                       Config config) {
            this.workerId = workerId;
            this.client = client;
            this.clientConfig = clientConfig;
            this.authProvider = authProvider;
            this.config = config;
        }

        @Override
        public WorkerResult call() {
            try {
                for (int iteration = 1; iteration <= config.iterationsPerThread(); iteration++) {
                    log("starting iteration " + iteration + " of " + config.iterationsPerThread());

                    String encryptBody = "{"
                            + quote("id") + ":" + quote(config.keyName()) + ","
                            + quote("pad") + ":" + quote(config.pad()) + ","
                            + quote("batch_request") + ":[{" 
                            + quote("plaintext") + ":" + quote(config.plaintextBase64())
                            + "}]"
                            + "}";

                    HttpResponse<String> encryptResponse = CipherTrustRestSupport.sendAuthenticatedJsonPost(
                            client,
                            authProvider,
                            clientConfig,
                            "/api/v1/crypto/encrypt",
                            encryptBody);
                    CipherTrustRestSupport.ensureSuccess(encryptResponse, "encrypt");
                    String ciphertext = extractValue(encryptResponse.body(), "ciphertext");
                    log("encrypt complete; ciphertext length=" + ciphertext.length());

                    if (config.sleepSecondsBeforeDecrypt() > 0) {
                        log("sleeping " + config.sleepSecondsBeforeDecrypt() + " seconds before decrypt");
                        Thread.sleep(config.sleepSecondsBeforeDecrypt() * 1000L);
                    }

                    String decryptBody = "{"
                            + quote("id") + ":" + quote(config.keyName()) + ","
                            + quote("pad") + ":" + quote(config.pad()) + ","
                            + quote("batch_request") + ":[{" 
                            + quote("ciphertext") + ":" + quote(ciphertext)
                            + "}]"
                            + "}";

                    HttpResponse<String> decryptResponse = CipherTrustRestSupport.sendAuthenticatedJsonPost(
                            client,
                            authProvider,
                            clientConfig,
                            "/api/v1/crypto/decrypt",
                            decryptBody);
                    CipherTrustRestSupport.ensureSuccess(decryptResponse, "decrypt");
                    String plaintext = extractValue(decryptResponse.body(), "plaintext");
                    log("decrypt complete; plaintext base64 length=" + plaintext.length());

                    if (iteration < config.iterationsPerThread() && config.sleepSecondsBetweenIterations() > 0) {
                        log("sleeping " + config.sleepSecondsBetweenIterations() + " seconds before next iteration");
                        Thread.sleep(config.sleepSecondsBetweenIterations() * 1000L);
                    }
                }
                return new WorkerResult(workerId, true, null);
            } catch (Exception ex) {
                log("failed: " + ex.getMessage());
                return new WorkerResult(workerId, false, ex.getMessage());
            }
        }

        private void log(String message) {
            System.out.println("[worker-" + workerId + "] " + message);
        }
    }

    private record WorkerResult(int workerId, boolean success, String message) {
    }

    private record Config(
            String baseUrl,
            String username,
            String password,
            String basicAuth,
            String keyName,
            String pad,
            String plaintextBase64,
            int timeoutSeconds,
            boolean insecureTls,
            boolean debug,
            int threads,
            int iterationsPerThread,
            int sleepSecondsBeforeDecrypt,
            int sleepSecondsBetweenIterations,
            int maxBusinessRequestsPerToken,
            Integer refreshSkewSecondsOverride) {
        private static Config fromArgs(String[] args) {
            Map<String, String> values = parseArgs(args);
            String basicAuth = firstNonBlank(
                    values.get("basicAuth"),
                    CipherTrustRestSupport.ClientConfig.encodeBasic(values.get("basicUsername"), values.get("basicPassword")));
            Integer refreshSkewOverride = values.containsKey("refreshSkewSecondsOverride")
                    ? parseNonNegativeInt(values.get("refreshSkewSecondsOverride"), "refreshSkewSecondsOverride")
                    : null;

            return new Config(
                    require(values, "baseUrl"),
                    require(values, "username"),
                    require(values, "password"),
                    basicAuth,
                    require(values, "keyName"),
                    values.getOrDefault("pad", "oaep"),
                    require(values, "plaintextBase64"),
                    parsePositiveInt(values.getOrDefault("timeoutSeconds", "60"), "timeoutSeconds"),
                    Boolean.parseBoolean(values.getOrDefault("insecureTls", "true")),
                    Boolean.parseBoolean(values.getOrDefault("debug", "false")),
                    parsePositiveInt(values.getOrDefault("threads", "3"), "threads"),
                    parsePositiveInt(values.getOrDefault("iterationsPerThread", "2"), "iterationsPerThread"),
                    parseNonNegativeInt(values.getOrDefault("sleepSecondsBeforeDecrypt", "0"), "sleepSecondsBeforeDecrypt"),
                    parseNonNegativeInt(values.getOrDefault("sleepSecondsBetweenIterations", "0"), "sleepSecondsBetweenIterations"),
                    parseNonNegativeInt(values.getOrDefault("maxBusinessRequestsPerToken", "0"), "maxBusinessRequestsPerToken"),
                    refreshSkewOverride);
        }

        private static Map<String, String> parseArgs(String[] args) {
            Map<String, String> values = new HashMap<>();
            for (String arg : args) {
                if (!arg.startsWith("--")) {
                    throw new IllegalArgumentException("Invalid argument: " + arg);
                }
                int eq = arg.indexOf('=');
                if (eq < 0) {
                    throw new IllegalArgumentException("Expected --name=value format, found: " + arg);
                }
                values.put(arg.substring(2, eq), arg.substring(eq + 1));
            }
            return values;
        }

        private static String require(Map<String, String> values, String key) {
            String value = values.get(key);
            if (value == null || value.isBlank()) {
                throw new IllegalArgumentException("Missing required argument: --" + key);
            }
            return value;
        }

        private static int parsePositiveInt(String value, String label) {
            int parsed = Integer.parseInt(value);
            if (parsed <= 0) {
                throw new IllegalArgumentException(label + " must be > 0");
            }
            return parsed;
        }

        private static int parseNonNegativeInt(String value, String label) {
            int parsed = Integer.parseInt(value);
            if (parsed < 0) {
                throw new IllegalArgumentException(label + " must be >= 0");
            }
            return parsed;
        }

        private static String firstNonBlank(String first, String second) {
            return first != null && !first.isBlank() ? first : second;
        }
    }

    private static String quote(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    private static String extractValue(String responseBody, String fieldName) {
        String token = "\"" + fieldName + "\"";
        int fieldIndex = responseBody.indexOf(token);
        if (fieldIndex < 0) {
            throw new IllegalStateException("Unable to locate field '" + fieldName + "' in response: " + responseBody);
        }
        int colonIndex = responseBody.indexOf(':', fieldIndex + token.length());
        int firstQuote = responseBody.indexOf('"', colonIndex + 1);
        int cursor = firstQuote + 1;
        StringBuilder value = new StringBuilder();
        boolean escaping = false;
        while (cursor < responseBody.length()) {
            char ch = responseBody.charAt(cursor++);
            if (escaping) {
                value.append(ch);
                escaping = false;
                continue;
            }
            if (ch == '\\') {
                escaping = true;
                continue;
            }
            if (ch == '"') {
                return value.toString().replace("\\/", "/");
            }
            value.append(ch);
        }
        throw new IllegalStateException("Unterminated JSON string for field '" + fieldName + "'.");
    }
}
