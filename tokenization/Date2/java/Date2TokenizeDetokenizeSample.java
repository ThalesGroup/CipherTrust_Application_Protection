/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Security;

import com.ingrian.internal.enums.DateFormatScheme;
import com.ingrian.internal.enums.Preserve;
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
		
		if (args.length < 9)
		{
			System.err.println("Usage: java Date2EncryptionDecryptionSample user password keyname startYear endYear "
					+ "dateFormat dateToTokenize dateFormatScheme preserve tweakData(Optional)");
			/*
			 * Usage: user key manager user name
			 * Usage: password key manager password
			 * Usage: keyname supports AES Non-versioned key
			 * Usage: startYear start year for date2 algorithm 
			 * Usage: endYear end year for date2 algorithm
			 * Usage: dateFormat is format of date in which user want to tokenize and detokenize date
			 * Usage: dateToTokenize input date that needs to be tokenized
			 * Usage: dateFormatScheme, if provided, the value must be a string - ddMMyyyy/ddMMyy/MMyyyy/MMyy
			 * Usage: preserve, if provided, the value must be a string - NONE/YEAR_MONTH/MONTH/YEAR
			 * Usage: tweakData(Optional), if provided, the value must be a string
			 *
			 * Note: Refer to Thales documentation for more information.
			 */

			System.exit(-1);
		} 
		
		String username  = args[0];
		String password  = args[1];
		String keyName   = args[2];
		int startYear = 0;
		int endYear = 0;
		String dateFormat = args[5];
		String dateToTokenize = args[6];		
		String dateFormatScheme = args[7];
		String preserve = args[8];
		String tweakData = null;
		
		if (!(args[3].equals("null"))) {
			startYear = Integer.parseInt(args[3]);
		}
		
		if (!(args[4].equals("null"))) {
			endYear = Integer.parseInt(args[4]);
		}
		if (args.length > 9) {
			tweakData = args[9];
		}
		
		// add Ingrian provider to the list of JCE providers
		Security.addProvider(new IngrianProvider());	
		
		 // Get the list of all registered JCE providers
		Provider[] providers = Security.getProviders();
		for (int i = 0; i < providers.length; i++)
			System.out.println(providers[i].getInfo());
		
		NAESession session  = null;
		Date2ParameterSpec date2ParameterSpec = null;
		try {
			
			// create NAE Session: pass in Key Manager username and password
			session = NAESession.getSession(username, password.toCharArray());
			// create the key
			NAEKey key = NAEKey.getSecretKey(keyName, session);
						
			DateFormatScheme dateFormatSchemeObj = DateFormatScheme.valueOf(dateFormatScheme.toUpperCase());
			Preserve preserveType = Preserve.valueOf(preserve.toUpperCase());

			/**
			 * Creating a DateParameterSpec using the deprecated method, still supported for backward compatibility.
			 * Take startYear as String startYear;
		     * Take endYear as String endYear;
			 * date2ParameterSpec = new Date2ParameterSpec.Date2ParameterBuilder(startYear, endYear, tweakData).build();
			 */

			if (Preserve.YEAR.equals(preserveType) || Preserve.YEAR_MONTH.equals(preserveType)) {

				// create the Date2ParameterSpec when preserve type is YEAR or YEAR_MONTH
				date2ParameterSpec = new Date2ParameterSpec.Date2ParameterBuilder(dateFormatSchemeObj)
						.setPreserve(preserveType).setTweakData(tweakData).build();
			} else {

				// create the Date2ParameterSpec for all input parameters
				date2ParameterSpec = new Date2ParameterSpec.Date2ParameterBuilder(dateFormatSchemeObj)
						.setPreserve(preserveType).setStartYear(startYear).setEndYear(endYear).setTweakData(tweakData)
						.build();
			}

			//create the Tokenization Service: pass in algorithm, key and algorithm parameter spec
			TokenizationService tokenizationService =TokenizationFactory.getTokenizationService("DATE2", key, date2ParameterSpec);
			
			if(tokenizationService!=null) {
			
				//tokenize the date
				byte[] tokenizedOutput =tokenizationService.tokenize(dateToTokenize.getBytes(), dateFormat);
				System.out.println("Tokenized date: " + new String(tokenizedOutput));
				
				//detokenize the date
				byte[] detokenizedOutput = tokenizationService.detokenize(tokenizedOutput, dateFormat);
				String detokenizedDate = new String(detokenizedOutput);
				System.out.println("Detokenized date: " + detokenizedDate);
				
				//cleanup 
				tokenizationService.cleanup();

				//check the detokenize date with user input date
				if(!detokenizedDate.equalsIgnoreCase(dateToTokenize))
					throw new Exception("=== dateToTokenize and detokenizedDate are NOT equal ===");

				System.out.println("=== dateToTokenize and detokenizedDate are equal !!!===");
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
