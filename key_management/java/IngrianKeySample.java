/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Provider;
import java.security.Security;
import java.util.Enumeration;
import java.util.Hashtable;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;

import com.ingrian.security.nae.CustomAttributes;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KeyExportData;
import com.ingrian.security.nae.KeyInfoData;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
//CADP for JAVA specific classes.
import com.ingrian.security.nae.NAEPermission;
import com.ingrian.security.nae.NAESecretKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to use additional key features defined by CADP for JAVA:
 * create an AES key with custom attributes; add and delete this key's custom 
 * attributes; create new version of that key on NAE server; modify key version of that key.
 */

public class IngrianKeySample
{
    public static void main( String[] args ) throws Exception
    {
	if (args.length != 4)
	{
            System.err.println("Usage: java IngrianKeySample user password keyname group");
            System.exit(-1);
	} 
        String username  = args[0];
        String password  = args[1];
        String keyName   = args[2];
	String group     = args[3];

	// add Ingrian provider to the list of JCE providers
	Security.addProvider(new IngrianProvider());

	// get the list of all registered JCE providers
	Provider[] providers = Security.getProviders();
	for (Provider provider : providers) {
		System.out.println(provider.getInfo());
	}

	NAESession session  = null;
	try {
	    // Create AES key on NAE server

	    // create NAE Session: pass in NAE user name and password
	    session  = NAESession.getSession(username, password.toCharArray());

            // set the key permissions to the set of permissions granted to NAE group.
            NAEPermission permission = new NAEPermission(group);

            // add permission to sign
            permission.setSign (true);

            // add permission to verify signature
            permission.setSignV (true);
            NAEPermission[] permissions = {permission};

            // create key pair which is exportable and deletable
            // key owner is NAE user, default key length 1024 bits and 
            // permissions granted to sign and verify
            NAEParameterSpec rsaParamSpec = 
                new NAEParameterSpec(keyName, true, true, session, permissions);


	    // create key custom attributes
	    CustomAttributes attrs = new CustomAttributes("Attr1", "abc");
            attrs.addAttribute("Attr2", "1234");

	    // create key which is exportable, deletable and versioned,
	    // with custom attributes,
	    // key owner is passed in NAE user and  key length 128 bits
	    NAEParameterSpec spec = new NAEParameterSpec( keyName, true, true, true,
							  128, attrs, session);	    
	    KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
	    kg.init(spec); 
            SecretKey secret_key = kg.generateKey();

	    NAEKey key = NAEKey.getSecretKey(keyName, session);

	    // Get default IV assiciated with this key
	    String defaultIV = key.getDefaultIV();
	    System.out.println("Key " + keyName + " has default IV " + defaultIV);

	    // Modify custom attributes.

	    // Create new attribute to add
	    CustomAttributes newAttrs = new CustomAttributes("Attr3", "ABC");

	    // Create list of attribute names to delete
	    String[] dAttrs = {"Attr1"};
	    key.modifyCustomAttributes(false, dAttrs, newAttrs);

	    // Create a new version of the key
	    int newVersion = key.generateVersion();
	    // and couple more 
	    newVersion = key.generateVersion();
	    newVersion = key.generateVersion();

	    // retire version 1 
	    key.modifyVersion(1, "Retired");
	    // restrict version 2
	    key.modifyVersion(2, "Restricted");

	    // get key instance
	    NAEKey newKey = NAEKey.getSecretKey(keyName, session);

	    // get custom attributes
	    CustomAttributes attributes = newKey.getCustomAttributes();
	    Hashtable attrTable = attributes.getAttributes();
	    for (Enumeration e = attrTable.keys(); e.hasMoreElements();) {
		String name = (String)e.nextElement();
		String value = (String)attrTable.get(name);
                System.out.println("Key custom attribute - name: " + name + " : value: " + value);
	    }
	    
	    // get key version info

	    if (newKey.isVersioned()) {
			System.out.println("\nKey " + newKey.getName() + " is versioned.");
		}
	    System.out.println("Number of key versions: " + newKey.getAllKeyVersions());
	    System.out.println("Number of active versions: " + newKey.getActiveKeyVersions());
	    System.out.println("Number of restricted versions: " + newKey.getRestrictedKeyVersions());
	    System.out.println("Number of retired versions: " + newKey.getRetiredKeyVersions());
	    System.out.println("Key Version: " + newKey.getKeyVersion() + "\n");
		
		// get key instance by adding #all with keyname in order to get all versions of key under getKeyInfoData
	    NAEKey keys = NAEKey.getSecretKey(keyName+"#all", session);
	    // get key info for all versions of this key
	    KeyInfoData[] infoData = keys.getKeyInfoData(true);
	    System.out.println("Key data for each version");
	    for (KeyInfoData element : infoData) {
		System.out.println("Key version: " + element.getKeyVersion());
		System.out.println("Key fingerprint: " + element.getFingerprint());
		System.out.println("Key State: " +  element.getKeyVersionState());
		System.out.println("Key iv: " + element.getDefaultIV() + "\n");
	    }
	    session.logEvent("Created versioned key.");

	    // export all versions of this key
	    KeyExportData[] keyData = newKey.export(true);
	    System.out.println("Exported key data for each version");
	    for (KeyExportData element : keyData) {
		System.out.println("Exported Key version: " + element.getKeyVersion());
		System.out.println("Exported Key fingerprint: " + element.getFingerprint());
		System.out.println("Exported Key data: " + element.getKeyData() + "\n");
	    }

	    // import the key back. we can import the key only as a non-versioned key.
	    NAEParameterSpec spec_import =
		new NAEParameterSpec(keyName + "Import", true, true, session);
	    if (keyData != null && keyData.length >= 2)
			NAEKey.importKey(IngrianProvider.hex2ByteArray(keyData[2].getKeyData()), "AES", spec_import);
		else {
			System.out.println("in persistance cache mode");
		}
	    NAESecretKey importKey = NAEKey.getSecretKey(keyName + "Import", session);
	    System.out.println("Imported key data; Key " + 
			       importKey.getName() + " was created on NAE Server.\n");

	    // encrypt data with all key versions
	    NAEKey allKey = NAEKey.getSecretKey(keyName+"#all", session);

	    String dataToEncrypt = "2D2D2D2D2D424547494E2050455253495354454E54204346EB17960";
	    System.out.println("Data to encrypt \"" + dataToEncrypt + "\"");

	    // get IV
	    NAESecureRandom rng = new NAESecureRandom (session);

	    byte[] iv = new byte[16];
	    rng.nextBytes(iv);
	    IvParameterSpec ivSpec = new IvParameterSpec(iv);
	    
	    // get a cipher
	    Cipher encryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
	    // initialize cipher to encrypt.
	    encryptCipher.init(Cipher.ENCRYPT_MODE, allKey, ivSpec);
	    // encrypt data
	    // outbuf is an array of ciphertexts; the size of this array is number of key versions;
	    // each ciphertext is the data encrypted by one version of the key: 
	    // result[0] is the data encrypted with the latest key version.
	    byte[] outbuf = encryptCipher.doFinal(dataToEncrypt.getBytes());
	    byte[][] result = IngrianProvider.encryptAllResult(outbuf);
	    for (byte[] element : result) {		
		System.out.println("Ciphertext "+ IngrianProvider.byteArray2Hex(element));
	    }
	   
	    
	    Cipher decryptCipher = Cipher.getInstance("AES/CBC/PKCS5Padding", "IngrianProvider");
	    // decrypt ciphertext
	    // init cipher 
	    NAEKey dKey = NAEKey.getSecretKey(keyName, session);
	    decryptCipher.init(Cipher.DECRYPT_MODE, dKey, ivSpec);
	    // will use correct key version from cipher text header

	    byte[] newbuf = decryptCipher.doFinal(result[0]);
	    System.out.println("Decrypted data  \"" + new String(newbuf) + "\"");
	}  catch (Exception e) {
	    System.out.println("The Cause is " + e.getMessage() + ".");
	    e.printStackTrace();
	} finally{
		if(session!=null) {
			session.closeSession();
		}
	}
    }
}
