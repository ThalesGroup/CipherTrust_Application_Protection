package com.thalesgroup.crdp_demo.service;

import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.springframework.stereotype.Service;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.KeyGenerator;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import java.nio.charset.StandardCharsets;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.SecureRandom;
import java.security.Security;
import java.util.Base64;

/**
 * @author CipherTrust.io
 *
 */
@Service
public class Crypto {
	private final SecretKey secretKey;
    private final IvParameterSpec ivSpec;

	public Crypto() throws Exception {
		// Add Bouncy Castle as a security provider
		Security.addProvider(new BouncyCastleProvider());

		// Generate AES key
		KeyGenerator keyGen = KeyGenerator.getInstance("AES", "BC");
		keyGen.init(256); // 256-bit key for AES
		this.secretKey = keyGen.generateKey();

		// Generate a random IV (16 bytes for AES)
		byte[] iv = new byte[16];
		SecureRandom random = new SecureRandom();
		random.nextBytes(iv);
		this.ivSpec = new IvParameterSpec(iv);
	}

	public String BouncyCastleEncrypt(String plainText) throws NoSuchAlgorithmException, NoSuchProviderException, NoSuchPaddingException, InvalidKeyException, InvalidAlgorithmParameterException, IllegalBlockSizeException, BadPaddingException {
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "BC");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivSpec);

        byte[] cipherBytes = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(cipherBytes);
    }

	public String BouncyCastleDecrypt(String cipherText) throws NoSuchAlgorithmException, NoSuchProviderException, NoSuchPaddingException, InvalidKeyException, InvalidAlgorithmParameterException, IllegalBlockSizeException, BadPaddingException {
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "BC");
        cipher.init(Cipher.DECRYPT_MODE, secretKey, ivSpec);

        byte[] plainBytes = cipher.doFinal(Base64.getDecoder().decode(cipherText));
        return new String(plainBytes, StandardCharsets.UTF_8);
    }
}
