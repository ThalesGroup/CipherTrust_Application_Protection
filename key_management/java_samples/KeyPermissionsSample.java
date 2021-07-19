/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Provider;
import java.security.Security;
import java.util.List;
import javax.crypto.KeyGenerator;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAEParameterSpec;
import com.ingrian.security.nae.NAEPermission;
import com.ingrian.security.nae.NAESession;

/**
 * This sample shows the group permissions linked to any key.
 * Here we are creating an AES key and setting permissions for group &
 * retrieving the permissions list<NAEPermission> object.
 *
 */
public class KeyPermissionsSample {
	public static void main(String[] args) throws Exception {
		if (args.length != 4) {
			System.err.println("Usage: java KeyPermissionsSample user password keyname group");
			System.exit(-1);
		}
		String username = args[0];
		String password = args[1];
		String keyName = args[2];
		String group = args[3];

		// add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());

		// get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());

		NAESession session = null;
		try {
			// create NAE Session: pass in NAE user name and password
			session = NAESession.getSession(username, password.toCharArray());
			// set the key permissions to the set of permissions granted to NAE group.
			NAEPermission permission = new NAEPermission(group);
			// add permission to encrypt
			permission.setEncrypt(true);
			// add permission to decrypt
			permission.setDecrypt(true);

			NAEPermission[] permissions = { permission };

			// set permission for encryption decryption
			// use builder pattern to make key exportable & versioned ,deletable
			NAEParameterSpec naeParamSpec = new NAEParameterSpec.Builder(keyName).withSession(session)
					.permissions(permissions).deletable(true).exportable(true).versioned(true).keylength(256).build();
			KeyGenerator kg = KeyGenerator.getInstance("AES", "IngrianProvider");
			kg.init(naeParamSpec);
			kg.generateKey();

			// retreive permissions for that key
			List<NAEPermission> linkedPermissions = NAEKey.getKeyPermissions(session, keyName);
			for (NAEPermission naePermission : linkedPermissions) {
				System.out.println(naePermission);
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (session != null)
				session.closeSession();
		}
	}
}
