package com.example;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.SecureRandom;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.time.Duration;
import java.util.Base64;
import java.util.Collection;
import java.util.concurrent.TimeUnit;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.KeyManager;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import okhttp3.ConnectionPool;
import okhttp3.OkHttpClient;

@Configuration
@EnableConfigurationProperties(CrdpProperties.class)
public class CrdpHttpClientConfig {

	private static final Logger log = LoggerFactory.getLogger(CrdpHttpClientConfig.class);

	@Bean
	OkHttpClient crdpOkHttpClient(CrdpProperties properties) {
		CrdpProperties.Ssl ssl = properties.getSsl();

		OkHttpClient.Builder builder = new OkHttpClient.Builder()
				.connectTimeout(Duration.ofMillis(properties.getConnectTimeoutMs()))
				.readTimeout(Duration.ofMillis(properties.getReadTimeoutMs()))
				.writeTimeout(Duration.ofMillis(properties.getWriteTimeoutMs()))
				.connectionPool(new ConnectionPool(properties.getHttpMaxIdleConnections(),
						properties.getHttpKeepaliveMinutes(), TimeUnit.MINUTES));

		if (!ssl.isEnabled()) {
			log.info("CRDP TLS disabled; using plain HTTP client for {}", properties.getBaseUrl());
			return builder.build();
		}

		try {
			TrustManagerAndContext tls = buildSslContext(ssl);
			builder.sslSocketFactory(tls.sslContext().getSocketFactory(), tls.trustManager());

			if (!ssl.isVerifyServer()) {
				HostnameVerifier allowAllHostnames = (hostname, session) -> true;
				builder.hostnameVerifier(allowAllHostnames);
				log.warn("CRDP TLS server verification is disabled. Use this only for non-production testing.");
			}

			log.info("CRDP TLS enabled for {}", properties.getBaseUrl());
			return builder.build();
		} catch (IOException | GeneralSecurityException e) {
			throw new IllegalStateException("Unable to configure CRDP TLS client", e);
		}
	}

	private TrustManagerAndContext buildSslContext(CrdpProperties.Ssl ssl)
			throws IOException, GeneralSecurityException {
		X509TrustManager trustManager;
		TrustManager[] trustManagers;

		if (ssl.isVerifyServer()) {
			trustManager = buildTrustManager(ssl);
			trustManagers = new TrustManager[] { trustManager };
		} else {
			trustManager = new InsecureTrustManager();
			trustManagers = new TrustManager[] { trustManager };
		}

		KeyManager[] keyManagers = buildKeyManagers(ssl);
		SSLContext sslContext = SSLContext.getInstance("TLS");
		sslContext.init(keyManagers, trustManagers, new SecureRandom());
		return new TrustManagerAndContext(trustManager, sslContext);
	}

	private X509TrustManager buildTrustManager(CrdpProperties.Ssl ssl) throws IOException, GeneralSecurityException {
		TrustManagerFactory trustManagerFactory = TrustManagerFactory
				.getInstance(TrustManagerFactory.getDefaultAlgorithm());
		String caCertPath = ssl.getCaCertPath();
		String trustStorePath = ssl.getTrustStorePath();

		if (!isBlank(caCertPath) && !isBlank(trustStorePath)) {
			throw new IllegalStateException(
					"Configure either CRDP_CA_CERT_PATH or CRDP_SSL_TRUST_STORE_PATH, not both.");
		}

		if (!isBlank(trustStorePath)) {
			String trustStoreType = isBlank(ssl.getTrustStoreType()) ? "JKS" : ssl.getTrustStoreType().trim();
			String trustStorePassword = resolveTrustStorePassword(ssl);
			KeyStore trustStore = KeyStore.getInstance(trustStoreType);

			try (InputStream inputStream = Files.newInputStream(Path.of(trustStorePath.trim()))) {
				trustStore.load(inputStream,
						trustStorePassword == null ? null : trustStorePassword.toCharArray());
			}

			trustManagerFactory.init(trustStore);
			return extractTrustManager(trustManagerFactory);
		}

		if (isBlank(caCertPath)) {
			trustManagerFactory.init((KeyStore) null);
			return extractTrustManager(trustManagerFactory);
		}

		KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
		trustStore.load(null, null);

		CertificateFactory certificateFactory = CertificateFactory.getInstance("X.509");
		try (InputStream inputStream = Files.newInputStream(Path.of(caCertPath.trim()))) {
			Collection<? extends Certificate> certificates = certificateFactory.generateCertificates(inputStream);
			if (certificates.isEmpty()) {
				throw new IllegalStateException("No CA certificates found at " + caCertPath);
			}

			int alias = 0;
			for (Certificate certificate : certificates) {
				trustStore.setCertificateEntry("crdp-ca-" + alias++, certificate);
			}
		}

		trustManagerFactory.init(trustStore);
		return extractTrustManager(trustManagerFactory);
	}

	private KeyManager[] buildKeyManagers(CrdpProperties.Ssl ssl) throws IOException, GeneralSecurityException {
		byte[] pkcs12Bytes = loadPkcs12Bytes(ssl);
		if (pkcs12Bytes == null) {
			return null;
		}

		String password = resolvePassword(ssl);
		if (password == null) {
			throw new IllegalStateException(
					"CRDP client PKCS12 content is configured, but no password or password file was provided.");
		}

		KeyStore keyStore = KeyStore.getInstance("PKCS12");
		try (InputStream inputStream = new ByteArrayInputStream(pkcs12Bytes)) {
			keyStore.load(inputStream, password.toCharArray());
		}

		KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
		keyManagerFactory.init(keyStore, password.toCharArray());
		return keyManagerFactory.getKeyManagers();
	}

	private byte[] loadPkcs12Bytes(CrdpProperties.Ssl ssl) throws IOException {
		if (!isBlank(ssl.getClientPkcs12Path())) {
			return Files.readAllBytes(Path.of(ssl.getClientPkcs12Path().trim()));
		}
		if (!isBlank(ssl.getClientPkcs12B64File())) {
			String encoded = Files.readString(Path.of(ssl.getClientPkcs12B64File().trim()), StandardCharsets.UTF_8);
			return Base64.getMimeDecoder().decode(encoded.trim());
		}
		if (!isBlank(ssl.getClientPkcs12B64())) {
			return Base64.getMimeDecoder().decode(ssl.getClientPkcs12B64().trim());
		}
		return null;
	}

	private String resolvePassword(CrdpProperties.Ssl ssl) throws IOException {
		if (!isBlank(ssl.getClientPkcs12Password())) {
			return ssl.getClientPkcs12Password();
		}
		if (!isBlank(ssl.getClientPkcs12PasswordFile())) {
			return Files.readString(Path.of(ssl.getClientPkcs12PasswordFile().trim()), StandardCharsets.UTF_8).trim();
		}
		return null;
	}

	private String resolveTrustStorePassword(CrdpProperties.Ssl ssl) throws IOException {
		if (!isBlank(ssl.getTrustStorePassword())) {
			return ssl.getTrustStorePassword();
		}
		if (!isBlank(ssl.getTrustStorePasswordFile())) {
			return Files.readString(Path.of(ssl.getTrustStorePasswordFile().trim()), StandardCharsets.UTF_8).trim();
		}
		return null;
	}

	private X509TrustManager extractTrustManager(TrustManagerFactory trustManagerFactory) {
		for (TrustManager trustManager : trustManagerFactory.getTrustManagers()) {
			if (trustManager instanceof X509TrustManager x509TrustManager) {
				return x509TrustManager;
			}
		}
		throw new IllegalStateException("No X509TrustManager available for CRDP TLS configuration");
	}

	private boolean isBlank(String value) {
		return value == null || value.trim().isEmpty();
	}

	private record TrustManagerAndContext(X509TrustManager trustManager, SSLContext sslContext) {
	}

	private static final class InsecureTrustManager implements X509TrustManager {

		@Override
		public void checkClientTrusted(java.security.cert.X509Certificate[] chain, String authType) {
		}

		@Override
		public void checkServerTrusted(java.security.cert.X509Certificate[] chain, String authType) {
		}

		@Override
		public java.security.cert.X509Certificate[] getAcceptedIssuers() {
			return new java.security.cert.X509Certificate[0];
		}
	}
}
