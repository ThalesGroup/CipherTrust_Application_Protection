package com.vertica.JavaLibs;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAECipher;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.vertica.sdk.*;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.GCMParameterSpec;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;


//import org.apache.commons.codec.binary.Base64;

import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;

/* This sample Database User Defined Function(UDF) for Vertica is an example of how to use Thales Cipher Trust Manager Protect Application
 * to protect sensitive data in a column.  This example uses CBC-GCM mode of encryption. This example decrypts data in a column or whatever
 * is passed to the function. It normally would be used by an ETL process or any query that needs clear text access to the sensitive data. 
 *  
*  
*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
*  Was tested with CM 2.1 & 2.2 & protect app 8.12.1 
*  Uses the VerticaSDK library and was tested with Vertica Analytic Database v8.1.0-2.
*  For more details on how to write Vertica UDF's please see
*  https://github.com/vertica/UDx-Examples
*  These examples assume you have placed all of the protect app required jar files in the java lib directory as specified in the Thales
*  protectapp documentation at: https://thalesdocs.com/ctp/cm/latest/
*     
 */

public class ThalesProtectAppDecryptGCM extends ScalarFunctionFactory {

	String username = "admin";
	String password = "YoursuperSecret!";
	String keyName = "MyAESEncryptionKey26";
	int authTagLength = Integer.parseInt("128");
	String iv = "6162636465666768696a6b6c";
	String aad = "6162636465666768696a6b6c";	
	NAESession session = null;
	NAEKey key = null;
	byte[] ivBytes = IngrianProvider.hex2ByteArray(iv);
	byte[] aadBytes = IngrianProvider.hex2ByteArray(aad);
	String tweakData = null;
	String tweakAlgo = null;
	GCMParameterSpec param   = null;

	public static final String plainTextInp = "Plain text message to be encrypted.";


	@Override
	public void getPrototype(ServerInterface srvInterface, ColumnTypes argTypes, ColumnTypes returnType) {
		// field name is column to encrypt
		argTypes.addVarchar();
	//	argTypes.addVarchar();
		// field name operation
		returnType.addVarchar();

	}

	/**
	* Returns an String that will be the decrypted value
	* <p>
	* Examples:
	* select employee_first_name, thalesdecryptgcmdata(employee_last_name)  from employee_dimension_protectapp limit 3
	*
	* @param is any column in the database or any value that needs to be decrypted based on the original encrypted data. 
	*/
	
	public class ThalesDecryptGCMData extends ScalarFunction {

		public void setup(ServerInterface srvInterface, SizedColumnTypes argTypes) {

			session = NAESession.getSession(username, password.toCharArray(), "hello".toCharArray());
			 key = NAEKey.getSecretKey(keyName, session);
			  param = new GCMParameterSpec(authTagLength, ivBytes, aadBytes);

		}

		public void destroy(ServerInterface srvInterface, SizedColumnTypes argTypes) {
	

		}

		public void processBlock(ServerInterface srvInterface, BlockReader arg_reader, BlockWriter res_writer)
				throws UdfException, DestroyInvocation {

			do {
				String results = null;
				String sensitive   = arg_reader.getString(0);

				Cipher decryptCipher;
				try {
					decryptCipher = NAECipher.getNAECipherInstance("AES/GCM/NoPadding", "IngrianProvider");
					decryptCipher.init(Cipher.DECRYPT_MODE, key, param);
					
					byte[] outbuf = decryptCipher.doFinal(IngrianProvider.hex2ByteArray(sensitive));
					//results = IngrianProvider.byteArray2Hex(outbuf);
					results = new String(outbuf);
				//	srvInterface.log("results = " + results);		
				} catch (NoSuchAlgorithmException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (NoSuchProviderException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (NoSuchPaddingException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (InvalidKeyException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (InvalidAlgorithmParameterException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (IllegalBlockSizeException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (BadPaddingException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

				res_writer.setString(results);

				res_writer.next();

			} while (arg_reader.next());

		}

	}


	@Override
	public void getReturnType(ServerInterface srvInterface, SizedColumnTypes argTypes, SizedColumnTypes returnType) {
		returnType.addVarchar((argTypes.getColumnType(0).getStringLength() + 200) * 2, argTypes.getColumnName(0));
	}


	@Override
	public ScalarFunction createScalarFunction(ServerInterface srvInterface) {
		return new ThalesDecryptGCMData();
	}
	
}
