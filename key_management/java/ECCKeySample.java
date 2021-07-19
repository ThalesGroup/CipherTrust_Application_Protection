/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.Provider;
import java.security.Security;

import com.ingrian.security.nae.ECCParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KeyExportData;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEPermission;
import com.ingrian.security.nae.NAEPrivateKey;
import com.ingrian.security.nae.NAEPublicKey;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows how to use following key operations for ECC keys:
 * 
 * 1-create an ECC key pair with the group permissions. 
 * 2-export public key data.
 * 3-export private key data.
 * 4-delete the key pair from Key Manager.
 * 5-import the key pair back to Key Manager.
 * 6-export private key data in PEM-PKCS#8 and PEM-SEC1 format.
 * 
 */
public class ECCKeySample {
	public static void main(String[] args) throws Exception {
	
		if (args.length != 4) {
			System.err.println("Usage: java ECCKeySample user password keyName groupName");
			System.exit(-1);
		}
		
		String userName = args[0];
		String password = args[1];
		String keyName  = args[2];
		String groupName= args[3];
	
		//KeyImportName must be unique each time importKey API is used.
		String keyImportName= keyName+"_Import";
		String algorithm = "EC";
		
		// Add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());
		
		NAESession session = null;
		try {
			//Creates NAESession: pass in NAE user and password
			session = NAESession.getSession(userName, password.toCharArray());
			
			  //Configure the key permissions to be granted to NAE group.
			  NAEPermission permission = new NAEPermission(groupName); 
			  // Add permission to sign
			  permission.setSign (true); 
			  // Add permission to verify signature
			  permission.setSignV (true); 
			  NAEPermission[] permissions = {permission};
			 
			//Creates ECCParameterSpec to generate ECC key pair which is exportable, deletable, non-versioned and
			//prime256v1 curve ID
			//Permissions granted to sign and verify 
			ECCParameterSpec spec1 = new ECCParameterSpec(keyName, true, true, false, null, session, permissions,
					ECCParameterSpec.CurveId.prime256v1);
			
			//Creates the ECC KeyPair generator object
			KeyPairGenerator generator = KeyPairGenerator.getInstance("EC", "IngrianProvider");
			
			//Initializes KeyPair generator with ECCParameterSpec
			generator.initialize(spec1);
			
			//Creates the Key Pair for ECC key
			KeyPair pair = generator.generateKeyPair();
			System.out.println("Created ECC key: " + keyName);
			
		    //Exports public key data from Key Manager
		    NAEPublicKey pubKey = NAEKey.getPublicKey(keyName, session );
		    byte[] pubKeyData = pubKey.export();
		    System.out.println("Exported public key: " + pubKey.getName());
		    
		    //Creates NAEPrivateKey object
		    NAEPrivateKey privKey = NAEKey.getPrivateKey(keyName, session);
		    
		    
		    //Exports private key data in default format i.e. PEM-PKCS#1
		    byte[] privKeyData = privKey.export();
		    
		    boolean exportAllVersion = false;
		    //Exports private key data in PEM-PKCS#8 format
		    //If exportAllVersion is set to true, the following export API will export all key versions
		    KeyExportData[]	privKeyExport_PKCS8 = privKey.export(exportAllVersion, "PEM-PKCS#8");
		    
		    for (KeyExportData keyExportDataPKCS8 : privKeyExport_PKCS8) {
		    	System.out.println("Private Key exported in PKCS#8 format:\n " + keyExportDataPKCS8.getKeyData());
		    }
		    
		    //Exports private key data in PEM-SEC1 format
		    //If exportAllVersion is set to true, the following export API will export all key versions
		    KeyExportData[]	privKeyExport_SEC1 = privKey.export(exportAllVersion, "PEM-SEC1");
		    
		    for (KeyExportData keyExportDataSEC1 : privKeyExport_SEC1) {
		    	System.out.println("Private Key exported in PEM-SEC1 format:\n" + keyExportDataSEC1.getKeyData());
		    }
		    
		    //Delete the key pair from Key Manager
		    pubKey.delete();
		    
		    //Creates a ECCParameterSpec to import ECC key
		    //Keys are exportable, deletable  and non-versioned
			ECCParameterSpec importSpec = new ECCParameterSpec(keyImportName, true, true, false, null, session, null, null);
 
			//Imports the key to the Key Manager
			NAEKey.importKey(privKeyData, algorithm, importSpec);
			
			System.out.println("Imported the key " + keyImportName +
				       " on the Key Manager.");
				
		} catch (Exception e) {
			e.printStackTrace();
			throw e;
		} finally {
			if (session != null)
				//Close NAESession
				session.closeSession();
		}

	}

}
