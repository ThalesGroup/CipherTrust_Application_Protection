
/*
 * 
 * Before Running this sample,
 * 
 * "UnicodeCodePointProperties" parameter should be set to 
 * <Absolute Path of TM Package Directory>/VaultlessTokenization/samples/VaultlessTokenization/unicode/FromFileUnicodeSample/unicode.properties 
 * in SafeNetVaultlessTokenization.properties file.
 * 
 * 
 * "Unicode.FromFile" parameter should be set to 
 * <Absolute Path of TM Package Directory>/VaultlessTokenization/samples/VaultlessTokenization/unicode/FromFileUnicodeSample/vietnamese.unicode
 * in  <Absolute Path of TM Package Directory>/VaultlessTokenization/samples/VaultlessTokenization/unicode/FromFileUnicodeSample/unicode.properties file.
 * 
 * 
 * vietnamese.unicode file contains unicode codepoints for Vietnamese language.
 * 
 * 
 * 
 */

import com.safenet.vaultLessTokenization.AlgoSpec;
import com.safenet.vaultLessTokenization.TokenException;
import com.safenet.vaultLessTokenization.TokenServiceVaultless;
import com.safenet.vaultLessTokenization.TokenSpec;

public class FromFileUnicodeSample {
	
	public static void main(String[] args)
	{
		try
		{
			
			if (args.length != 3)
	        {
	            System.err.println("Usage: java FromFileUnicodeSample naeuser naepassword keyname");
	            System.exit(-1);
	        }
	        String naeUser = args[0];
	        char[] naePswd = args[1].toCharArray();
	        String keyName = args[2];        
	       
			
			AlgoSpec algoSpec =new AlgoSpec();
			algoSpec.setVersion(1);
			
			//Creating Vaultless TokenService instance
	        TokenServiceVaultless ts = new TokenServiceVaultless(naeUser, naePswd, keyName, algoSpec );
	        
	        TokenSpec tokenSpec = new TokenSpec();
	        tokenSpec.setFormat(TokenServiceVaultless.TOKEN_ALL);
	        tokenSpec.setGroupID(1);
	        tokenSpec.setClearTextSensitive(true);
			
	        ////////////////////////////////////token/detoken single//////////////////////////////////////////////
	        //Tokenization
	        System.out.println("+++++++++++++++++++++++++++++++Token/Detoken for Single API++++++++++++++++++++++++++++++++++++++++++++++++++++");
	        String value = "\u00d0\u01b0\u1edd\u006e\u1ecb\u1ed1";
			
			System.out.println("Value to be tokenized : " + value);
			
			String token = ts.tokenize(value, tokenSpec);
			
			System.out.println("Tokenized Data         : " + token);
			
			
			 //Detokenization
	        String detoken = ts.detokenize(token,tokenSpec) ;
	        System.out.println("Detokenized Data      : " + detoken);
	        if(!value.equals(detoken)){
	            System.out.println("Test FAIL");
	        }else
	        {
	            System.out.println("Input value and Detokenized value matched - Test PASS");
	        }
	        
	        ////////////////////////////////////token/detoken single//////////////////////////////////////////////


	        ////////////////////////////////////token/detoken batch//////////////////////////////////////////////
	        //Tokenization for Batch API
	        //Hard coding the input values for batch
	        System.out.println();
	        System.out.println("+++++++++++++++++++++++++++++++Token/Detoken for Batch API ++++++++++++++++++++++++++++++++++++++++++++++++++++");
	        String[] dataToEncryptBatch = {"\u0062\u00e0\u0069\u0074\u0068\u01a1" ,"\u0079\u00ea\u006e\u1eed"};
	        System.out.println("Tokenized Data for Batch : ");
	        String[] tokenBatch = ts.tokenize(dataToEncryptBatch , tokenSpec);
	        for (int i = 0; i < tokenBatch.length; i++) {
	        	System.out.println("" + tokenBatch[i]);
	        }

	        //DeTtkenization for Batch API
	        System.out.println("Detokenized Data for Batch : ");
	        String[] dataBatch = ts.detokenize(tokenBatch,tokenSpec) ;
	        for (int i = 0; i < dataBatch.length; i++) {
	        	System.out.println("" + dataBatch[i]);
	        	}

	        boolean status = true ;
	        for (int i = 0; i < dataToEncryptBatch.length; i++) {
	        	if(!dataToEncryptBatch[i].equals(dataBatch[i])){
	        		status = false ;
	        	}
	        }
	        if(status){
	        	System.out.println("Input values and Detokenized values matched - Test PASS");
	        }else{
	        	System.out.println("Test FAIL");
	        }
	        ////////////////////////////////////token/detoken batch//////////////////////////////////////////////

	        //Close tokenService instance
	        ts.closeService();
			 
			System.out.println("\n" + TokenServiceVaultless.getVersion());	
	               
			
		}catch(TokenException ex)
		{
			ex.printStackTrace();
		}       
		
		
	}

}
