import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyStore;
import java.security.SecureRandom;
import java.security.cert.CertificateFactory;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.util.Collection;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

import okhttp3.ConnectionPool;
import okhttp3.OkHttpClient;

public final class ThalesCrdpHttpClientFactory {

    private static final Object CLIENT_LOCK = new Object();
    private static volatile OkHttpClient sharedClient;
    private static volatile String sharedClientSignature;

    private ThalesCrdpHttpClientFactory() {
    }

    public static OkHttpClient getOrCreate(ThalesDataBricksUdfConfig config) {
        String signature = buildClientSignature(config);
        OkHttpClient existingClient = sharedClient;
        if (existingClient != null && signature.equals(sharedClientSignature)) {
            return existingClient;
        }

        synchronized (CLIENT_LOCK) {
            existingClient = sharedClient;
            if (existingClient != null && signature.equals(sharedClientSignature)) {
                return existingClient;
            }

            sharedClient = buildClient(config);
            sharedClientSignature = signature;
            return sharedClient;
        }
    }

    private static OkHttpClient buildClient(ThalesDataBricksUdfConfig config) {
        OkHttpClient.Builder builder = new OkHttpClient.Builder()
                .connectTimeout(config.getCrdpConnectTimeoutMs(), TimeUnit.MILLISECONDS)
                .readTimeout(config.getCrdpReadTimeoutMs(), TimeUnit.MILLISECONDS)
                .writeTimeout(config.getCrdpWriteTimeoutMs(), TimeUnit.MILLISECONDS)
                .connectionPool(new ConnectionPool(
                        config.getCrdpHttpMaxIdleConnections(),
                        config.getCrdpHttpKeepAliveMinutes(),
                        TimeUnit.MINUTES));

        if (!config.isCrdpSslEnabled()) {
            return builder.build();
        }

        try {
            X509TrustManager trustManager = buildTrustManager(config);
            SSLContext sslContext = SSLContext.getInstance("TLS");

            if (hasText(config.getCrdpClientPkcs12Path())) {
                KeyManagerFactory keyManagerFactory = buildKeyManagerFactory(config);
                sslContext.init(keyManagerFactory.getKeyManagers(), new TrustManager[]{trustManager}, new SecureRandom());
            } else {
                sslContext.init(null, new TrustManager[]{trustManager}, new SecureRandom());
            }

            SSLSocketFactory sslSocketFactory = sslContext.getSocketFactory();
            builder.sslSocketFactory(sslSocketFactory, trustManager);

            if (!config.isCrdpSslVerifyServerEnabled()) {
                builder.hostnameVerifier(new HostnameVerifier() {
                    @Override
                    public boolean verify(String hostname, SSLSession session) {
                        return true;
                    }
                });
            }

            return builder.build();
        } catch (Exception ex) {
            throw new RuntimeException("Failed to create CRDP HTTPS client.", ex);
        }
    }

    private static KeyManagerFactory buildKeyManagerFactory(ThalesDataBricksUdfConfig config) throws Exception {
        Path pkcs12Path = requireExistingPath(config.getCrdpClientPkcs12Path(), "CRDP_CLIENT_PKCS12_PATH");
        char[] password = config.getCrdpClientPkcs12Password().toCharArray();
        KeyStore keyStore = KeyStore.getInstance("PKCS12");
        try (InputStream input = Files.newInputStream(pkcs12Path)) {
            keyStore.load(input, password);
        }

        KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        keyManagerFactory.init(keyStore, password);
        Arrays.fill(password, '\0');
        return keyManagerFactory;
    }

    private static X509TrustManager buildTrustManager(ThalesDataBricksUdfConfig config) throws Exception {
        if (!config.isCrdpSslVerifyServerEnabled()) {
            return trustAllManager();
        }

        if (hasText(config.getCrdpCaCertPath())) {
            Path caCertPath = requireExistingPath(config.getCrdpCaCertPath(), "CRDP_CA_CERT_PATH");
            CertificateFactory certificateFactory = CertificateFactory.getInstance("X.509");
            Collection<? extends Certificate> certificates;
            try (InputStream input = Files.newInputStream(caCertPath)) {
                certificates = certificateFactory.generateCertificates(input);
            }
            if (certificates == null || certificates.isEmpty()) {
                throw new IllegalStateException("No certificates found in CRDP_CA_CERT_PATH: " + caCertPath);
            }

            KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
            trustStore.load(null, null);
            int index = 0;
            for (Certificate certificate : certificates) {
                if (!(certificate instanceof X509Certificate)) {
                    continue;
                }
                trustStore.setCertificateEntry("crdp-ca-" + index, certificate);
                index++;
            }
            if (index == 0) {
                throw new IllegalStateException("No X509 certificates found in CRDP_CA_CERT_PATH: " + caCertPath);
            }

            TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            trustManagerFactory.init(trustStore);
            return extractTrustManager(trustManagerFactory);
        }

        TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        trustManagerFactory.init((KeyStore) null);
        return extractTrustManager(trustManagerFactory);
    }

    private static X509TrustManager extractTrustManager(TrustManagerFactory trustManagerFactory) {
        TrustManager[] managers = trustManagerFactory.getTrustManagers();
        if (managers.length != 1 || !(managers[0] instanceof X509TrustManager)) {
            throw new IllegalStateException("Unable to resolve X509TrustManager for CRDP HTTPS client.");
        }
        return (X509TrustManager) managers[0];
    }

    private static X509TrustManager trustAllManager() {
        return new X509TrustManager() {
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
        };
    }

    private static Path requireExistingPath(String value, String propertyName) {
        if (!hasText(value)) {
            throw new IllegalStateException("Missing required property: " + propertyName);
        }

        Path path = Paths.get(value.trim());
        if (Files.notExists(path)) {
            throw new IllegalStateException("File does not exist for " + propertyName + ": " + value);
        }
        return path;
    }

    private static boolean hasText(String value) {
        return value != null && !value.trim().isEmpty();
    }

    private static String buildClientSignature(ThalesDataBricksUdfConfig config) {
        return String.join("|",
                String.valueOf(config.isCrdpSslEnabled()),
                String.valueOf(config.isCrdpSslVerifyServerEnabled()),
                valueOrBlank(config.getCrdpClientPkcs12Path()),
                valueOrBlank(config.getCrdpCaCertPath()),
                String.valueOf(config.getCrdpConnectTimeoutMs()),
                String.valueOf(config.getCrdpReadTimeoutMs()),
                String.valueOf(config.getCrdpWriteTimeoutMs()),
                String.valueOf(config.getCrdpHttpMaxIdleConnections()),
                String.valueOf(config.getCrdpHttpKeepAliveMinutes()));
    }

    private static String valueOrBlank(String value) {
        return value == null ? "" : value.trim();
    }
}
