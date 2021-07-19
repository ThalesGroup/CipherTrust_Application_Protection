/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Security;

import com.ingrian.internal.kmip.api.CryptographicUsageMask.UsageMask;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPAttributes;
import com.ingrian.security.nae.KMIPKeyWrapSpecification;
import com.ingrian.security.nae.KMIPKeyWrappingData;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;
import com.ingrian.security.nae.NAEException;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.KMIPAttributeNames.KMIPAttribute;
import com.ingrian.security.nae.KMIPKeyFormatTypes.KeyFormatType;

/**
 * 
 * 
 * This sample use to test Key Wrap/unwrap functionality
 * 
 */
public class KMIPWrapUnwrapSample {

	static String algorithm = "AES";
	static int length = 128;
	static KeyFormatType keyFormat = KeyFormatType.Raw;

	public static void main(String[] args) {
		if (args.length != 4)
		{
			usage();
		} 
		// add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());
		String wrapping_key = args[2];
		String wrapped_key = args[3];

		// key bytes
		String wrapping_keybytes = "49E3BD09F079E4F8842F1C6620FFF6EC";
		String wrapped_keybytes = "92F6355221CC38DF5F374275631C774D";
		
		System.out.println("wrapped_keybytes Key-1 " + wrapped_keybytes);
		System.out.println("wrapping_keybytes Key-2" + wrapping_keybytes);


		// key specification and key wrapping data
		String wrappingMethod = "Encrypt";
		String uniqueIdentifier_wrappingkey = null;
		String uniqueIdentifier_wrappedkey = null;
		String blockCipherMode = "NISTKeyWrap";
		String paddingMethod = null;		// not required as of now
		String hashingAlgorithm = null;		// not required as of now
		String keyRoleType = null;			// not required as of now
		String encodingOption = "NoEncoding";

		//initiate KMIP session
		KMIPSession session  = KMIPSession.getSession(new NAEClientCertificate(args[0], args[1].toCharArray()));

		// KMIP attributes for to declare an encrypting key
		KMIPAttributes initialAttribute = new KMIPAttributes();
		initialAttribute.add(KMIPAttribute.CryptographicUsageMask, (int)( UsageMask.WrapKey.getValue() | UsageMask.UnwrapKey.getValue() ));

		// KMIP attribute to declare a plain key
		KMIPAttributes initialAttributes2 = new KMIPAttributes();
		initialAttributes2.add(KMIPAttribute.CryptographicUsageMask, (int)( UsageMask.Encrypt.getValue() | UsageMask.Decrypt.getValue() ));

		
		NAEParameterSpec spec = new NAEParameterSpec( wrapping_key, 128, initialAttribute, (KMIPSession)session);
		NAEParameterSpec spec2 = new NAEParameterSpec( wrapped_key, 128, initialAttributes2, (KMIPSession)session);


		
		NAEKey key3 = NAEKey.getSecretKey(wrapping_key,session);
		NAEKey key4 = NAEKey.getSecretKey(wrapped_key,session);

		//register wrapping key
		try{
			uniqueIdentifier_wrappingkey = key3.registerKey(IngrianProvider.hex2ByteArray(wrapping_keybytes), algorithm, keyFormat, spec);
		}
		catch(NAEException e)
		{
			if(e.getMessage().contains("Key already exists"))
			{
				System.out.println("this key already exist");
				try {
					//updating UID for wrapping key
					uniqueIdentifier_wrappingkey = key3.getUID();
				} catch (NAEException e1) {
					e1.printStackTrace();
				} catch (Exception e1) {
					e1.printStackTrace();
				}
			}
		}
		
		//register wrapped key
		try{
			uniqueIdentifier_wrappedkey = key4.registerKey(IngrianProvider.hex2ByteArray(wrapped_keybytes), algorithm, keyFormat, spec2);
		}catch(NAEException e)
		{
			if(e.getMessage().contains("Key already exists"))
			{
				System.out.println("this key already exist");
				try {
					//updating UID for wrapped key
					uniqueIdentifier_wrappedkey = key4.getUID();
				} catch (Exception e1) {
					e1.printStackTrace();
				}
			}

		}

		//KMIP attribute to get a wrapped key
		KMIPAttributes initialAttributes1 = new KMIPAttributes();
		initialAttributes1.add(new KMIPKeyWrapSpecification(wrappingMethod, uniqueIdentifier_wrappingkey , blockCipherMode, paddingMethod, hashingAlgorithm, keyRoleType, encodingOption),0);

		// Getting wrapped key bytes
		byte[] x = session.wrapKey(wrapped_key, initialAttributes1 );
		System.out.println("Encrypted key bytes Key 1 " + IngrianProvider.byteArray2Hex(x));

		//KMIP attribute to register a new key using encrypted key bytes
		KMIPAttributes unwrapAttribute = new KMIPAttributes();
		unwrapAttribute.add(new KMIPKeyWrappingData(wrappingMethod, uniqueIdentifier_wrappingkey, blockCipherMode, paddingMethod, hashingAlgorithm, keyRoleType, encodingOption),0);
		unwrapAttribute.add(KMIPAttribute.CryptographicUsageMask, (int)( UsageMask.Encrypt.getValue() | UsageMask.Decrypt.getValue() ));
		
		String new_unwrapkeyuid = null;
		//register a new key using wrapped key bytes
		try{
			new_unwrapkeyuid = session.registerKey(x, algorithm, null, length,unwrapAttribute );
		}catch(NAEException e)
		{
			if(e.getMessage().contains("Key already exists"))
				System.out.println("this key already exist");
		}

		// Getting plain key bytes of new key
		System.out.println("Plain key bytes of Key-3 " +IngrianProvider.byteArray2Hex(session.getKeyBytes(new_unwrapkeyuid)));
		
		session.closeSession();
	}

	private static void usage() {
		System.err.println("Usage: java KMIPWrapUnwrapSample clientCertAlias keyStorePassword wrapping_keyname wrapped_keyname");
		System.exit(-1);
	}

}
