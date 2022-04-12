
import java.lang.Character.UnicodeBlock;
import com.safenet.vaultLessTokenization.AlgoSpec;
import com.safenet.vaultLessTokenization.TokenException;
import com.safenet.vaultLessTokenization.TokenServiceVaultless;
import com.safenet.vaultLessTokenization.TokenSpec;


public class AlgoSpecUnicodeSample {
	
	public static void main(String[] args) throws TokenException
	{
		
		if (args.length != 3)
        {
            System.err.println("Usage: java AlgoSpecUnicodeSample naeuser naepassword keyname");
            System.exit(-1);
        }
        String naeUser = args[0];
        char[] naePswd = args[1].toCharArray();
        String keyName = args[2];  
			
		Integer[] AlgoSpecUnicodeBlocks = {
										AlgoSpec.UNICODE_KATAKANA,
										AlgoSpec.UNICODE_HIRAGANA,
										AlgoSpec.UNICODE_CJK_UNIFIED_IDEOGRAPHS,
										AlgoSpec.UNICODE_HEBREW,
										AlgoSpec.UNICODE_ARABIC,
										AlgoSpec.UNICODE_HANGUL,
										AlgoSpec.UNICODE_THAI,
										AlgoSpec.UNICODE_RUSSIAN_CYRILLIC,
										AlgoSpec.UNICODE_JOYO_KANJI,
										AlgoSpec.UNICODE_GREEK							
				
		};
		
		
		 System.out.println("/************************************************************");
	     System.out.println(" *   Tokenize and Detokenize Various Unicode Strings");
	     System.out.println("/************************************************************");

	        String[] unicodeStrings = new String[10];
	        
	     // Japanese Katakana
	        unicodeStrings[0] = "\u30C6\u30AF\u30B9\u30FB\u30C6\u30AF\u30B5\u30F3";
	        
		 // Japanese Hiragana
	        unicodeStrings[1] = "\u3042\u3040\u3064\u3076\u3089\u3075\u3090\u305F";
	        
	     // CJK_UNIFIED_IDEOGRAPHS 
	        unicodeStrings[2] = "\u674E\u5B89\u7AE0\u5B50\u6021";
	        
	     // Hebrew  
	        unicodeStrings[3] = "\u05D9\u05D4\u05D5\u05E8\u05DD\u0020\u05D2\u05D0\u05D5\u05DF";
	        
	     //Arabic   
	        unicodeStrings[4] = "\u0645\u0631\u062d\u0628\u0627";	  
	        
	     // Korean / Hangul
	        unicodeStrings[5] = "\uC2EC\uC740\uD558";
	        
	     //Thai    
	        unicodeStrings[6] = "\u0e2a\u0e27\u0e31\u0e2a\u0e14\u0e35";
	        
	     // Russian	     
	        unicodeStrings[7] = "\u0411\u043E\u0440\u0438\u0441\u0020\u0413\u0440\u0435" +
                    "\u0431\u0435\u043D\u0449\u0438\u043A\u043E\u0432";
	        
	     // Japanese Kanji
	        unicodeStrings[8] = "\u6797\u539F\u0020\u3081\u3050\u307F";
	        
	     // Greek
	        unicodeStrings[9] = "\u0393\u03B9\u03CE\u03C1\u03B3\u03BF\u03C2\u0020\u039D" +
                    "\u03C4\u03B1\u03BB\u03AC\u03C1\u03B1\u03C2";
	        
	        TokenServiceVaultless ts = null;
	        
	        AlgoSpec algoSpec =new AlgoSpec();
			algoSpec.setVersion(1);
			
			TokenSpec tokenSpec = new TokenSpec();
	        tokenSpec.setFormat(TokenServiceVaultless.TOKEN_ALL);
	        tokenSpec.setGroupID(1);
	        tokenSpec.setClearTextSensitive(true);
	        
	        for(int i=0; i<unicodeStrings.length; ++i) {
				
				//setting unicode in AlgoSpec for different Unicode Blocks.
	        	algoSpec.setUnicode(AlgoSpecUnicodeBlocks[i]);
				
				//Creating  instance of TokenServiceVaultless for different Unicode Blocks.
	        	ts = new TokenServiceVaultless(naeUser, naePswd, keyName,algoSpec);
	            tokenizeAUnicodeString( ts, tokenSpec,  unicodeStrings[i] );
	            ts.closeService();
				
	        }
	       
			System.out.println("\n" + TokenServiceVaultless.getVersion());
		
		
	}

	
	static void tokenizeAUnicodeString(TokenServiceVaultless ts, TokenSpec spec,
            String unicodeString) {

        try {

            System.out.println();
            System.out.println("Tokenize this value: " + unicodeString);

            System.out.println("First character is from the Unicode block, " +
                    UnicodeBlock.of( unicodeString.codePointAt( 0 ) ).toString() + ".");

            String token = ts.tokenize(unicodeString, spec);

            System.out.println("Here is the token: " + token);

            System.out.println("Return the original value from the Token ...");

            String value = ts.detokenize (token, spec) ;

            System.out.println("Decrypted Value: " + value);

            if (value.equals(unicodeString))
                System.out.println("Detokenized value matches with original value: " + value);
            else
                System.err.println("Error: wrong value returned: " + value);            

        } catch( Exception ex ) {

            System.err.println( ex.getMessage() );

            if( ex.getCause() != null ) {
                Throwable t = ex.getCause();
                System.out.println( "Cause: " + t.getMessage() );
            }

            System.exit(-1);
        }
    }
	
}
