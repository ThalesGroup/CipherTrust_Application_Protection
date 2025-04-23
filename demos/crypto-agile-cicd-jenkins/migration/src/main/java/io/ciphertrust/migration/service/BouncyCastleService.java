package io.ciphertrust.migration.service;

public interface BouncyCastleService {
    String encryptCreditCard(String ccNumber);
    String encryptCVV(String cvv);
    String encryptTelemetryData(String data);

    String decryptCreditCard(String encryptedCC);
    String decryptCVV(String encryptedCVV);
    String decryptTelemetryData(String encryptedData);
}