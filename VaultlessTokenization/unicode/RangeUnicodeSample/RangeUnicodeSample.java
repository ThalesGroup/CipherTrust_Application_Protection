
/*
 * Before Running this sample,
 * "UnicodeCodePointProperties" parameter should be set to 
 * <Absolute Path of TM Package Directory>/VaultlessTokenization/samples/VaultlessTokenization/unicode/RangeUnicodeSample/unicode.properties 
 * in SafeNetVaultlessTokenization.properties file.
 * 
 * Scope and undefined Ranges specified in unicode.properties file have codepoint values for Armenian Unicode block.
 * 
 */

import com.safenet.vaultLessTokenization.AlgoSpec;
import com.safenet.vaultLessTokenization.TokenException;
import com.safenet.vaultLessTokenization.TokenServiceVaultless;
import com.safenet.vaultLessTokenization.TokenSpec;

public class RangeUnicodeSample {
	
	public static void main(String[] args)
	{
		try
		{
			
			if (args.length != 3)
	        {
	            System.err.println("Usage: java RangeUnicodeSample naeuser naepassword keyname");
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
			
			String value = "\u0532\u0561\u0580\u0565\u0582";
			
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
	        String[] dataToEncryptBatch = {"\u0565\u0580\u057b\u0561\u0576\u056b\u056f" ,"\u057f\u056d\u0578\u0582\u0580"};
	        System.out.println("Tokenized Data for Batch : ");
	        String[] tokenBatch = ts.tokenize(dataToEncryptBatch , tokenSpec);
	        for (int i = 0; i < tokenBatch.length; i++) {
	        	System.out.println("" + tokenBatch[i]);
	        }

	        //DeTokenization for Batch API
	        System.out.println("Detokenized Data retrieved for Batch : ");
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
