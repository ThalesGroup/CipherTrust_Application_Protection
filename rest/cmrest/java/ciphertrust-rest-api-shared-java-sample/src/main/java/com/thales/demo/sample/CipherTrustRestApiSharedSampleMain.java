package com.thales.demo.sample;

import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class CipherTrustRestApiSharedSampleMain {
    private static final Pattern CIPHERTEXT_PATTERN = Pattern.compile("\"ciphertext\"\\s*:\\s*\"([^\"]+)\"");
    private static final Pattern PLAINTEXT_PATTERN = Pattern.compile("\"plaintext\"\\s*:\\s*\"([^\"]+)\"");

    private CipherTrustRestApiSharedSampleMain() {
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

        for (int iteration = 1; iteration <= config.repeat(); iteration++) {
            System.out.println("Iteration " + iteration + " of " + config.repeat());

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
            System.out.println("Encrypt response:");
            System.out.println(encryptResponse.body());

            String ciphertext = extractCiphertext(encryptResponse.body());

            System.out.println();
            System.out.println("Ciphertext passed into decrypt:");
            System.out.println(ciphertext);

            if (config.sleepSecondsBeforeDecrypt() > 0) {
                System.out.println();
                System.out.println("Sleeping " + config.sleepSecondsBeforeDecrypt() + " seconds before decrypt to exercise token lifetime behavior...");
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
            System.out.println();
            System.out.println("Decrypt response:");
            System.out.println(decryptResponse.body());

            String plaintextBase64 = extractPlaintext(decryptResponse.body());
            byte[] decodedBytes = Base64.getDecoder().decode(plaintextBase64);
            String decodedText = new String(decodedBytes, StandardCharsets.UTF_8);

            System.out.println();
            System.out.println("Decoded plaintext (Base64):");
            System.out.println(plaintextBase64);
            System.out.println();
            System.out.println("Decoded plaintext (UTF-8 text rendering):");
            System.out.println(decodedText);
            System.out.println();

            if (iteration < config.repeat() && config.sleepSecondsBetweenIterations() > 0) {
                System.out.println("Sleeping " + config.sleepSecondsBetweenIterations() + " seconds before next iteration...");
                Thread.sleep(config.sleepSecondsBetweenIterations() * 1000L);
                System.out.println();
            }
        }
    }

    private static String quote(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    private static String extractCiphertext(String responseBody) {
        Matcher matcher = CIPHERTEXT_PATTERN.matcher(responseBody);
        if (!matcher.find()) {
            throw new IllegalStateException("Unable to locate ciphertext in encrypt response: " + responseBody);
        }
        return matcher.group(1).replace("\\/", "/").replace("\\\"", "\"").replace("\\\\", "\\");
    }

    private static String extractPlaintext(String responseBody) {
        Matcher matcher = PLAINTEXT_PATTERN.matcher(responseBody);
        if (!matcher.find()) {
            throw new IllegalStateException("Unable to locate plaintext in decrypt response: " + responseBody);
        }
        return matcher.group(1).replace("\\/", "/").replace("\\\"", "\"").replace("\\\\", "\\");
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
            int repeat,
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
                    parsePositiveInt(values.getOrDefault("repeat", "1"), "repeat"),
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
}