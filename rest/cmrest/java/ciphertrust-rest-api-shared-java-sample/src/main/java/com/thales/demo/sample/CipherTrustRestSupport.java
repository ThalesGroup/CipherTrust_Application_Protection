package com.thales.demo.sample;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;
import java.time.Duration;
import java.util.Base64;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLParameters;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

public final class CipherTrustRestSupport {
    private static final Pattern JWT_PATTERN = Pattern.compile("\"jwt\"\\s*:\\s*\"([^\"]+)\"");

    private CipherTrustRestSupport() {
    }

    public static HttpClient buildHttpClient(boolean insecureTls, int timeoutSeconds) throws GeneralSecurityException {
        if (insecureTls) {
            System.setProperty("jdk.internal.httpclient.disableHostnameVerification", "true");
        }

        HttpClient.Builder builder = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(timeoutSeconds))
                .followRedirects(HttpClient.Redirect.NORMAL);

        if (insecureTls) {
            SSLContext sslContext = SSLContext.getInstance("TLS");
            TrustManager[] trustAll = new TrustManager[]{
                    new X509TrustManager() {
                        @Override
                        public void checkClientTrusted(X509Certificate[] chain, String authType) {
                        }

                        @Override
                        public void checkServerTrusted(X509Certificate[] chain, String authType) {
                        }

                        @Override
                        public X509Certificate[] getAcceptedIssuers() {
                            return new X509Certificate[0];
                        }
                    }
            };
            sslContext.init(null, trustAll, new SecureRandom());
            builder.sslContext(sslContext);
            SSLParameters sslParameters = new SSLParameters();
            sslParameters.setEndpointIdentificationAlgorithm("");
            builder.sslParameters(sslParameters);
        }

        return builder.build();
    }

    public record ClientConfig(
            String baseUrl,
            String username,
            String password,
            String basicAuth,
            List<String> labels,
            int timeoutSeconds,
            boolean debug,
            int maxBusinessRequestsPerToken,
            Integer refreshSkewSecondsOverride) {

        public ClientConfig {
            if (isBlank(baseUrl) || isBlank(username) || isBlank(password)) {
                throw new IllegalArgumentException("baseUrl, username, and password are required");
            }
            labels = labels == null || labels.isEmpty() ? List.of("myapp", "cli") : List.copyOf(labels);
            timeoutSeconds = timeoutSeconds <= 0 ? 60 : timeoutSeconds;
            maxBusinessRequestsPerToken = Math.max(0, maxBusinessRequestsPerToken);
            if (refreshSkewSecondsOverride != null && refreshSkewSecondsOverride < 0) {
                throw new IllegalArgumentException("refreshSkewSecondsOverride must be >= 0");
            }
        }

        public ClientConfig(String baseUrl,
                            String username,
                            String password,
                            String basicAuth,
                            List<String> labels,
                            int timeoutSeconds) {
            this(baseUrl, username, password, basicAuth, labels, timeoutSeconds, false, 0, null);
        }

        public static String encodeBasic(String username, String password) {
            if (isBlank(username) || isBlank(password)) {
                return null;
            }
            return Base64.getEncoder().encodeToString((username + ":" + password).getBytes(StandardCharsets.UTF_8));
        }
    }

    public static final class AuthTokenProvider {
        private final HttpClient client;
        private final ClientConfig config;
        private Session currentSession;
        private int businessRequestsOnCurrentToken;

        public AuthTokenProvider(HttpClient client, ClientConfig config) {
            this.client = client;
            this.config = config;
        }

        public synchronized Session getValidSession() throws IOException, InterruptedException {
            if (currentSession == null) {
                debug("No token cached yet. Authenticating.");
                currentSession = authenticate(client, config);
                businessRequestsOnCurrentToken = 0;
                return currentSession;
            }

            if (config.maxBusinessRequestsPerToken() > 0
                    && businessRequestsOnCurrentToken >= config.maxBusinessRequestsPerToken()) {
                debug("Refreshing token because maxBusinessRequestsPerToken="
                        + config.maxBusinessRequestsPerToken() + " was reached.");
                currentSession = authenticate(client, config);
                businessRequestsOnCurrentToken = 0;
                return currentSession;
            }

            if (currentSession.isExpiringSoon()) {
                debug("Refreshing token proactively because it is nearing expiry.");
                currentSession = authenticate(client, config);
                businessRequestsOnCurrentToken = 0;
            }
            return currentSession;
        }

        public synchronized Session forceRefresh() throws IOException, InterruptedException {
            debug("Refreshing token reactively after auth failure or expiry response.");
            currentSession = authenticate(client, config);
            businessRequestsOnCurrentToken = 0;
            return currentSession;
        }

        public synchronized void recordBusinessRequestUse(String path) {
            businessRequestsOnCurrentToken++;
            debug("Recorded authenticated business request to " + path
                    + ". Requests on current token=" + businessRequestsOnCurrentToken + ".");
        }

        private void debug(String message) {
            if (config.debug()) {
                System.out.println("[CipherTrustRestSupport] " + message);
            }
        }
    }

    public record Session(String jwt, int durationSeconds, long expiresAtMillis, int refreshSkewSeconds) {
        public boolean isExpiringSoon() {
            long refreshAtMillis = expiresAtMillis - (refreshSkewSeconds * 1000L);
            return System.currentTimeMillis() >= refreshAtMillis;
        }

        public String shortToken() {
            return jwt.length() <= 16 ? jwt : jwt.substring(0, 16) + "...";
        }
    }

    public static HttpResponse<String> sendAuthenticatedJsonPost(HttpClient client,
                                                                 AuthTokenProvider authProvider,
                                                                 ClientConfig config,
                                                                 String path,
                                                                 String jsonBody) throws IOException, InterruptedException {
        Session session = authProvider.getValidSession();
        debug(config, "POST " + path + " using token " + session.shortToken());
        HttpResponse<String> response = sendAuthenticatedJsonPostOnce(client, session.jwt(), config, path, jsonBody);

        if (response.statusCode() == 401 || tokenLooksExpired(response.body())) {
            debug(config, "Received auth-expiry style response for " + path + ". Refreshing and retrying once.");
            Session refreshed = authProvider.forceRefresh();
            debug(config, "Retrying POST " + path + " using token " + refreshed.shortToken());
            response = sendAuthenticatedJsonPostOnce(client, refreshed.jwt(), config, path, jsonBody);
        }

        authProvider.recordBusinessRequestUse(path);
        return response;
    }

    public static void ensureSuccess(HttpResponse<String> response, String action) {
        int code = response.statusCode();
        if (code < 200 || code >= 300) {
            throw new IllegalStateException("Unable to " + action + ". HTTP " + code + ": " + response.body());
        }
    }

    public static Session authenticate(HttpClient client, ClientConfig config) throws IOException, InterruptedException {
        String authUrl = trimTrailingSlash(config.baseUrl()) + "/api/v1/auth/tokens";
        String json = "{"
                + quote("grant_type") + ":" + quote("password") + ","
                + quote("username") + ":" + quote(config.username()) + ","
                + quote("password") + ":" + quote(config.password()) + ","
                + quote("refresh_token_lifetime") + ":20,"
                + quote("refresh_token_revoke_unused_in") + ":10,"
                + quote("labels") + ":" + toJsonArray(config.labels())
                + "}";

        debug(config, "Authenticating to /api/v1/auth/tokens" + (isBlank(config.basicAuth()) ? " without Basic header." : " with Basic header."));

        HttpRequest.Builder builder = HttpRequest.newBuilder(URI.create(authUrl))
                .timeout(Duration.ofSeconds(config.timeoutSeconds()))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json, StandardCharsets.UTF_8));

        if (!isBlank(config.basicAuth())) {
            builder.header("Authorization", "Basic " + config.basicAuth());
        }

        HttpResponse<String> response = client.send(builder.build(), HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            String hint = isBlank(config.basicAuth())
                    ? " If your environment requires a Basic header, provide one in ClientConfig.basicAuth."
                    : "";
            throw new IllegalStateException("Unable to authenticate. HTTP " + response.statusCode() + ": " + response.body() + hint);
        }

        String jwt = extractJwt(response.body());
        int duration = extractOptionalNumber(response.body(), "duration").orElse(300);
        long expiresAtMillis = System.currentTimeMillis() + (duration * 1000L);
        int skewSeconds = config.refreshSkewSecondsOverride() != null
                ? config.refreshSkewSecondsOverride()
                : Math.min(30, Math.max(5, duration / 10));

        Session session = new Session(jwt, duration, expiresAtMillis, skewSeconds);
        debug(config, "Received token " + session.shortToken() + " with duration=" + duration + " seconds and refreshSkewSeconds=" + skewSeconds + ".");
        return session;
    }

    private static HttpResponse<String> sendAuthenticatedJsonPostOnce(HttpClient client,
                                                                      String jwt,
                                                                      ClientConfig config,
                                                                      String path,
                                                                      String jsonBody) throws IOException, InterruptedException {
        String url = trimTrailingSlash(config.baseUrl()) + path;
        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(config.timeoutSeconds()))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .header("Authorization", "Bearer " + jwt)
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody, StandardCharsets.UTF_8))
                .build();
        return client.send(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
    }

    private static boolean tokenLooksExpired(String body) {
        String lower = body == null ? "" : body.toLowerCase(Locale.US);
        return lower.contains("token expired") || lower.contains("jwt expired") || lower.contains("expired token");
    }

    private static String extractJwt(String body) {
        Matcher matcher = JWT_PATTERN.matcher(body);
        if (!matcher.find()) {
            throw new IllegalStateException("Unable to locate jwt in response: " + body);
        }
        return unescapeJson(matcher.group(1));
    }

    private static java.util.Optional<Integer> extractOptionalNumber(String body, String fieldName) {
        Pattern pattern = Pattern.compile("\\\"" + Pattern.quote(fieldName) + "\\\"\\s*:\\s*(\\d+)");
        Matcher matcher = pattern.matcher(body);
        if (matcher.find()) {
            return java.util.Optional.of(Integer.parseInt(matcher.group(1)));
        }
        return java.util.Optional.empty();
    }

    private static String toJsonArray(List<String> values) {
        return values.stream().map(CipherTrustRestSupport::quote).collect(Collectors.joining(",", "[", "]"));
    }

    private static String quote(String value) {
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    private static String unescapeJson(String text) {
        return text.replace("\\/", "/").replace("\\\"", "\"").replace("\\\\", "\\");
    }

    private static String trimTrailingSlash(String value) {
        return value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private static void debug(ClientConfig config, String message) {
        if (config.debug()) {
            System.out.println("[CipherTrustRestSupport] " + message);
        }
    }
}