package com.example;

import java.net.URI;
import java.net.URISyntaxException;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "crdp")
public class CrdpProperties {

	private String host = "thales-crdp-service.stuff.svc.spcs.internal";
	private int port = 8090;
	private int connectTimeoutMs = 10000;
	private int readTimeoutMs = 30000;
	private int writeTimeoutMs = 30000;
	private int httpMaxIdleConnections = 20;
	private int httpKeepaliveMinutes = 5;
	private final Ssl ssl = new Ssl();

	public String getHost() {
		return host;
	}

	public void setHost(String host) {
		this.host = host;
	}

	public int getPort() {
		return port;
	}

	public void setPort(int port) {
		this.port = port;
	}

	public int getConnectTimeoutMs() {
		return connectTimeoutMs;
	}

	public void setConnectTimeoutMs(int connectTimeoutMs) {
		this.connectTimeoutMs = connectTimeoutMs;
	}

	public int getReadTimeoutMs() {
		return readTimeoutMs;
	}

	public void setReadTimeoutMs(int readTimeoutMs) {
		this.readTimeoutMs = readTimeoutMs;
	}

	public int getWriteTimeoutMs() {
		return writeTimeoutMs;
	}

	public void setWriteTimeoutMs(int writeTimeoutMs) {
		this.writeTimeoutMs = writeTimeoutMs;
	}

	public int getHttpMaxIdleConnections() {
		return httpMaxIdleConnections;
	}

	public void setHttpMaxIdleConnections(int httpMaxIdleConnections) {
		this.httpMaxIdleConnections = httpMaxIdleConnections;
	}

	public int getHttpKeepaliveMinutes() {
		return httpKeepaliveMinutes;
	}

	public void setHttpKeepaliveMinutes(int httpKeepaliveMinutes) {
		this.httpKeepaliveMinutes = httpKeepaliveMinutes;
	}

	public Ssl getSsl() {
		return ssl;
	}

	public String getBaseUrl() {
		String configuredHost = host == null ? "" : host.trim();
		if (configuredHost.isEmpty()) {
			throw new IllegalStateException("CRDP host is not configured");
		}

		if (configuredHost.startsWith("http://") || configuredHost.startsWith("https://")) {
			try {
				URI uri = new URI(configuredHost);
				String scheme = uri.getScheme();
				boolean configuredTls = "https".equalsIgnoreCase(scheme);
				if (ssl.enabled != configuredTls) {
					throw new IllegalStateException("CRDP URL scheme conflicts with CRDP_SSL_ENABLED. "
							+ "Use a bare CRDP_HOST or make the URL scheme match the TLS setting.");
				}
				String authority = uri.getRawAuthority();
				if (authority == null || authority.isBlank()) {
					throw new IllegalStateException("CRDP host is missing authority: " + configuredHost);
				}
				String path = uri.getPath();
				if (path == null || path.isBlank() || "/".equals(path)) {
					return scheme + "://" + authority + "/v1/";
				}
				String normalizedPath = path.endsWith("/") ? path : path + "/";
				return scheme + "://" + authority + normalizedPath + "v1/";
			} catch (URISyntaxException e) {
				throw new IllegalStateException("Invalid CRDP host URI: " + configuredHost, e);
			}
		}

		String scheme = ssl.enabled ? "https" : "http";
		return scheme + "://" + configuredHost + ":" + port + "/v1/";
	}

	public static class Ssl {
		private boolean enabled = false;
		private boolean verifyServer = true;
		private String caCertPath;
		private String trustStorePath;
		private String trustStoreType;
		private String trustStorePassword;
		private String trustStorePasswordFile;
		private String clientPkcs12Path;
		private String clientPkcs12Password;
		private String clientPkcs12PasswordFile;
		private String clientPkcs12B64;
		private String clientPkcs12B64File;

		public boolean isEnabled() {
			return enabled;
		}

		public void setEnabled(boolean enabled) {
			this.enabled = enabled;
		}

		public boolean isVerifyServer() {
			return verifyServer;
		}

		public void setVerifyServer(boolean verifyServer) {
			this.verifyServer = verifyServer;
		}

		public String getCaCertPath() {
			return caCertPath;
		}

		public void setCaCertPath(String caCertPath) {
			this.caCertPath = caCertPath;
		}

		public String getTrustStorePath() {
			return trustStorePath;
		}

		public void setTrustStorePath(String trustStorePath) {
			this.trustStorePath = trustStorePath;
		}

		public String getTrustStoreType() {
			return trustStoreType;
		}

		public void setTrustStoreType(String trustStoreType) {
			this.trustStoreType = trustStoreType;
		}

		public String getTrustStorePassword() {
			return trustStorePassword;
		}

		public void setTrustStorePassword(String trustStorePassword) {
			this.trustStorePassword = trustStorePassword;
		}

		public String getTrustStorePasswordFile() {
			return trustStorePasswordFile;
		}

		public void setTrustStorePasswordFile(String trustStorePasswordFile) {
			this.trustStorePasswordFile = trustStorePasswordFile;
		}

		public String getClientPkcs12Path() {
			return clientPkcs12Path;
		}

		public void setClientPkcs12Path(String clientPkcs12Path) {
			this.clientPkcs12Path = clientPkcs12Path;
		}

		public String getClientPkcs12Password() {
			return clientPkcs12Password;
		}

		public void setClientPkcs12Password(String clientPkcs12Password) {
			this.clientPkcs12Password = clientPkcs12Password;
		}

		public String getClientPkcs12PasswordFile() {
			return clientPkcs12PasswordFile;
		}

		public void setClientPkcs12PasswordFile(String clientPkcs12PasswordFile) {
			this.clientPkcs12PasswordFile = clientPkcs12PasswordFile;
		}

		public String getClientPkcs12B64() {
			return clientPkcs12B64;
		}

		public void setClientPkcs12B64(String clientPkcs12B64) {
			this.clientPkcs12B64 = clientPkcs12B64;
		}

		public String getClientPkcs12B64File() {
			return clientPkcs12B64File;
		}

		public void setClientPkcs12B64File(String clientPkcs12B64File) {
			this.clientPkcs12B64File = clientPkcs12B64File;
		}
	}
}
