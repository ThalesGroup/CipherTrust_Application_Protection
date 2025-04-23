package io.ciphertrust.migration.service.impl;

import io.ciphertrust.migration.service.BouncyCastleService;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.crypto.fpe.FPEFF1Engine;
import org.bouncycastle.crypto.params.FPEParameters;
import org.springframework.stereotype.Service;
import org.bouncycastle.crypto.params.KeyParameter;
import java.nio.ByteBuffer;

import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.util.*;
import java.nio.charset.StandardCharsets;
import java.io.*;

@Service
public class BouncyCastleServiceImpl implements BouncyCastleService {
    
    // =============================================
    // INSECURE CONFIGURATION - FOR TESTING ONLY
    // =============================================
    private static final byte[] FIXED_IV = {
        (byte) 0x01, (byte) 0x23, (byte) 0x45, (byte) 0x67,
        (byte) 0x89, (byte) 0xAB, (byte) 0xCD, (byte) 0xEF,
        (byte) 0xFE, (byte) 0xDC, (byte) 0xBA, (byte) 0x98,
        (byte) 0x76, (byte) 0x54, (byte) 0x32, (byte) 0x10
    };
    // =============================================

    private enum DataType {
        CREDIT_CARD(256, "FPE/FF1", "keys/cc.key", "0123456789-"),
        CVV(256, "AES/CBC/PKCS5Padding", "keys/cvv.key", "0123456789-"),
        TELEMETRY_DATA(256, "AES/CBC/PKCS5Padding", "keys/telemetry.key", "0123456789.-");

        final int keySize;
        final String algorithm;
        final String keyPath;
        final String charset;

        DataType(int keySize, String algorithm, String keyPath, String charset) {
            this.keySize = keySize;
            this.algorithm = algorithm;
            this.keyPath = keyPath;
            this.charset = charset;
        }
    }

    static {
        if (Security.getProvider("BC") == null) {
            Security.addProvider(new BouncyCastleProvider());
        }
        System.setProperty("org.bouncycastle.fips.approved_only", "false");
    }

    @Override
    public String encryptCreditCard(String ccNumber) {
        try {
            return processCreditCard(DataType.CREDIT_CARD, ccNumber, true);
        } catch (Exception e) {
            throw new RuntimeException("Credit card encryption failed", e);
        }
    }

    @Override
    public String encryptCVV(String cvv) {
        try {
            return encryptAESCBCPKCS5(DataType.CVV, cvv);
        } catch (Exception e) {
            throw new RuntimeException("CVV encryption failed", e);
        }
    }

    @Override
    public String encryptTelemetryData(String data) {
        try {
            return encryptAESCBCPKCS5(DataType.TELEMETRY_DATA, data);
        } catch (Exception e) {
            throw new RuntimeException("Telemetry data encryption failed", e);
        }
    }

    @Override
    public String decryptCreditCard(String encryptedCC) {
        try {
            return processCreditCard(DataType.CREDIT_CARD, encryptedCC, false);
        } catch (Exception e) {
            throw new RuntimeException("Credit card decryption failed", e);
        }
    }

    @Override
    public String decryptCVV(String encryptedCVV) {
        try {
            return decryptAESCBCPKCS5(DataType.CVV, encryptedCVV, String.class);
        } catch (Exception e) {
            throw new RuntimeException("CVV decryption failed", e);
        }
    }

    @Override
    public String decryptTelemetryData(String encryptedData) {
        try {
            return decryptAESCBCPKCS5(DataType.TELEMETRY_DATA, encryptedData, String.class);
        } catch (Exception e) {
            throw new RuntimeException("Telemetry data decryption failed", e);
        }
    }

    // ============ PRIVATE METHODS ============
    
    // For encryption method:
    private byte[] numberToBytes(Number number) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(baos);

        if (number instanceof Double) {
           dos.writeDouble(number.doubleValue());
        } else if (number instanceof Integer) {
           dos.writeInt(number.intValue());
        } else if (number instanceof Long) {
           dos.writeLong(number.longValue());
        } else if (number instanceof Float) {
           dos.writeFloat(number.floatValue());
        } else if (number instanceof Short) {
           dos.writeShort(number.shortValue());
        } else if (number instanceof Byte) {
           dos.writeByte(number.byteValue());
        } else {
           throw new IllegalArgumentException("Unsupported number type: " + number.getClass());
        }

        dos.close();
        return baos.toByteArray();
    }

    // In encryption method:
    private Object convertToOriginalType(String base64Value, Class<?> targetType) {
       if (targetType == String.class) {
           return base64Value;
       } else if (targetType == Double.class || targetType == double.class) {
           return Double.valueOf(base64Value);
       } else if (targetType == Integer.class || targetType == int.class) {
           return Integer.valueOf(base64Value);
       } else if (targetType == Long.class || targetType == long.class) {
           return Long.valueOf(base64Value);
       } else if (targetType == Float.class || targetType == float.class) {
           return Float.valueOf(base64Value);
       } else if (targetType == Short.class || targetType == short.class) {
           return Short.valueOf(base64Value);
       } else if (targetType == Byte.class || targetType == byte.class) {
           return Byte.valueOf(base64Value);
       }
       throw new UnsupportedOperationException("Type " + targetType + " not supported");
    }
    private Object convertToNumber(byte[] encryptedValue, Class<?> targetType) {
       if (targetType == Double.class || targetType == double.class) {
          return ByteBuffer.wrap(encryptedValue).getDouble();
       } else if (targetType == Integer.class || targetType == int.class) {
           return ByteBuffer.wrap(encryptedValue).getInt();
       } else if (targetType == Long.class || targetType == long.class) {
           return ByteBuffer.wrap(encryptedValue).getLong();
       } else if (targetType == Float.class || targetType == float.class) {
           return ByteBuffer.wrap(encryptedValue).getFloat();
       } else if (targetType == Short.class || targetType == short.class) {
           return ByteBuffer.wrap(encryptedValue).getShort();
       } else if (targetType == Byte.class || targetType == byte.class) {
           return encryptedValue;
       }
       throw new UnsupportedOperationException("Type " + targetType + " not supported");
    }

    // Corresponding decryption:
    private Number bytesToNumber(byte[] bytes, Class<?> numberType) throws IOException {
        DataInputStream dis = new DataInputStream(new ByteArrayInputStream(bytes));

        if (numberType == Double.class || numberType == double.class) {
           return dis.readDouble();
        } else if (numberType == Integer.class || numberType == int.class) {
           return dis.readInt();
        } else if (numberType == Long.class || numberType == long.class) {
           return dis.readLong();
        } else if (numberType == Float.class || numberType == float.class) {
           return dis.readFloat();
        } else if (numberType == Short.class || numberType == short.class) {
           return dis.readShort();
        } else if (numberType == Byte.class || numberType == byte.class) {
           return dis.readByte();
        }

        throw new IllegalArgumentException("Unsupported number type: " + numberType);
    }

    private String processCreditCard(DataType type, String data, boolean encrypt) throws Exception {
        if (type.charset == null) throw new IllegalArgumentException("FPE requires charset");
        byte[] tweak = new byte[] {
           (byte)0xA1, (byte)0xB2, (byte)0xC3, (byte)0xD4,
           (byte)0xE5, (byte)0xF6, (byte)0x11, (byte)0x22,
           (byte)0x33, (byte)0x44, (byte)0x55, (byte)0x66,
           (byte)0x77, (byte)0x88, (byte)0x99, (byte)0x00
        };
        int radix = 256;

        KeyParameter keyParam = new KeyParameter(loadKey(type).getEncoded());

        FPEFF1Engine engine = new FPEFF1Engine();
        FPEParameters params = new FPEParameters(
            keyParam,
            radix,
            tweak
        );

        engine.init(encrypt, params);

        byte[] inputBytes = data.getBytes(StandardCharsets.UTF_8);
        byte[] encrypted = new byte[inputBytes.length];
        engine.processBlock(inputBytes, 0, inputBytes.length, encrypted, 0);

        return new String(encrypted, StandardCharsets.UTF_8);
    }

    @SuppressWarnings("unchecked")
    private <T> T encryptAESCBCPKCS5(DataType type, T plaintext) throws Exception {
        if (plaintext == null) throw new IllegalArgumentException("Cannot encrypt null");

        byte[] bytesToEncrypt;

        if (plaintext instanceof String) {
            bytesToEncrypt = ((String) plaintext).getBytes(StandardCharsets.UTF_8);
            byte[] encryptedBytes  = performEncryption(type, bytesToEncrypt);
            String base64Result = Base64.getEncoder().encodeToString(encryptedBytes);
            return (T) convertToOriginalType(base64Result, plaintext.getClass());
        } else if (plaintext instanceof Number) {
            bytesToEncrypt = numberToBytes((Number) plaintext);
            byte[] encryptedBytes  = performEncryption(type, bytesToEncrypt);
            System.out.println("+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+");
            System.out.println(convertToNumber(encryptedBytes, plaintext.getClass()));
            return (T) convertToNumber(encryptedBytes, plaintext.getClass());
        } else {
            throw new UnsupportedOperationException("Type " + plaintext.getClass() + " not supported");
        }
    }

    private byte[] performEncryption(DataType type, byte[] input) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "BC");
        cipher.init(Cipher.ENCRYPT_MODE, loadKey(type), new IvParameterSpec(FIXED_IV));

        byte[] ciphertext = cipher.doFinal(input);
        byte[] combined = new byte[FIXED_IV.length + ciphertext.length];
        System.arraycopy(FIXED_IV, 0, combined, 0, FIXED_IV.length);
        System.arraycopy(ciphertext, 0, combined, FIXED_IV.length, ciphertext.length);

        return combined;
    }

    @SuppressWarnings("unchecked")
    private <T> T decryptAESCBCPKCS5(DataType type, String encrypted, Class<T> returnType) throws Exception {
        if (encrypted == null) {
            throw new IllegalArgumentException("Cannot decrypt null value");
        }

        byte[] decryptedBytes = performDecryption(type, encrypted);

        if (returnType == String.class) {
            return (T) new String(decryptedBytes, StandardCharsets.UTF_8);
        }
        else if (Number.class.isAssignableFrom(returnType) || returnType.isPrimitive()) {
            return (T) bytesToNumber(decryptedBytes, returnType);
        }

        throw new UnsupportedOperationException("Unsupported return type: " + returnType);
    }

    private byte[] performDecryption(DataType type, String encrypted) throws Exception {
        byte[] combined = Base64.getDecoder().decode(encrypted);
        byte[] iv = Arrays.copyOfRange(combined, 0, 16);
        byte[] ciphertext = Arrays.copyOfRange(combined, 16, combined.length);

        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "BC");
        cipher.init(Cipher.DECRYPT_MODE, loadKey(type), new IvParameterSpec(iv));
        return cipher.doFinal(ciphertext);
    }

    private SecretKey loadKey(DataType type) throws Exception {
        File keyFile = new File(type.keyPath);
        if (!keyFile.exists()) {
            generateKey(type);
        }

        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(keyFile))) {
            return (SecretKey) ois.readObject();
        }
    }

    private void generateKey(DataType type) throws Exception {
        KeyGenerator keyGen = KeyGenerator.getInstance("AES", "BC");

        switch(type) {
            case CREDIT_CARD -> keyGen.init(type.keySize, SecureRandom.getInstanceStrong());
            case CVV -> keyGen.init(type.keySize, new SecureRandom());
            case TELEMETRY_DATA -> keyGen.init(type.keySize);
        }

        SecretKey key = keyGen.generateKey();
        new File(type.keyPath).getParentFile().mkdirs();

        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(type.keyPath))) {
            oos.writeObject(key);
        }
    }
}