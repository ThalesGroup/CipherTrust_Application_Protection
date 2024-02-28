
/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

import java.security.Security;

import com.ingrian.security.nae.Date2ParameterSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.TokenizationFactory;
import com.ingrian.security.nae.TokenizationService;
import java.security.Provider;

/**
 * This sample shows how to tokenize and detokenize date using Date2 algorithm.
 */
public class Date2TokenizeDetokenizeSample 
{
	public static void main( String[] args ) throws Exception
	{
		
		if (args.length <7)
		{
			System.err.println("Usage: java Date2EncryptionDecryptionSample user password keyname startYear endYear dateFormat inputDate tweakData(Optional)");
			/*
			 * Usage: user key manager user name
			 * Usage: password key manager password
			 * Usage: keyname supports AES Non-versioned key
			 * Usage: startYear start year for date2 algorithm 
			 * Usage: endYear end year for date2 algorithm
			 * Usage: dateFormat is format of date in which user want to tokenize and detokenize date
			 * Usage: inputDate input date that needs to be tokenized
			 * Usage: tweakData(Optional), if provided, the value must be a string
			 */

			System.exit(-1);
		} 
		
		String username  = args[0];
		String password  = args[1];
		String keyName   = args[2];
		String startYear = args[3];
		String endYear   = args[4];
		String dateFormat = args[5];
		String dateToTokenize = args[6];
		 String tweakData = null;
        
        if(args.length > 7)
		 {
			tweakData   = args[7];
		 }
		
		
		// add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());	
		
		 // Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());
		
		NAESession session  = null;
		try {

			// create the Date2ParameterSpec
			Date2ParameterSpec date2ParameterSpec = new Date2ParameterSpec.Date2ParameterBuilder(startYear, endYear,tweakData).build();

			// create NAE Session: pass in Key Manager user name and password
			session  = NAESession.getSession(username, password.toCharArray());
			// create the key
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			
			//create the Tokenization Service: pass in algorithm, key and algorithm parameter spec
			TokenizationService tokenizationService =TokenizationFactory.getTokenizationService("DATE2", key, date2ParameterSpec);
			
			if(tokenizationService!=null) {
			
				//tokenize the date
				byte[] tokenizedOutput =tokenizationService.tokenize(dateToTokenize.getBytes(), dateFormat);
				System.out.println("Tokenized date: " + new String(tokenizedOutput));
				
				//detokenize the date
				byte[] detokenizedOutput = tokenizationService.detokenize(tokenizedOutput, dateFormat);
				System.out.println("Detokenized date: " + new String(detokenizedOutput));
				
			}
			
		} catch (Exception e) {
			System.out.println("The Cause is " + e.getMessage() + ".");
			throw e;
		} finally{
			if(session!=null) {
				session.closeSession();
			}
		}
	}
}
