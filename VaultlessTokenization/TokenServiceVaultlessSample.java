/**
 * Created by toberoi on 19-09-2016.
 */

import com.safenet.vaultLessTokenization.TokenSpec;
import com.safenet.vaultLessTokenization.TokenServiceVaultless;

public class TokenServiceVaultlessSample {
    public static void main( String[] args ) throws Exception {



        if (args.length != 4)
        {
            System.err.println("Usage: java TokenServiceVaultlessSample naeuser naepassword keyname dataToEncrypt");
            System.exit(-1);
        }
        String naeUser = args[0];
        char[] naePswd = args[1].toCharArray();
        String keyName = args[2];


        //Creating Vaultless TokenService instance
        TokenServiceVaultless ts = new TokenServiceVaultless(naeUser, naePswd, keyName );


        /*
        Create TokenSpec for the tokenization and detokenization. The same tokenSpec should be used for tokenization and detokenization
        Prepare the tokenSpec :-
        1. Format
        2. LuhnCheck : Note on setting this value either true or false, input data must have luhndigit as last digit
        3. GroupID
        4. ClearTextSenitive
        5. NonIdempotent
        For definition and possible values, refer CADP Vaultless Tokenization User Guide
        */
        TokenSpec tokenSpec = new TokenSpec();


        tokenSpec.setFormat(TokenServiceVaultless.TOKEN_ALL);
        tokenSpec.setGroupID(1);
        tokenSpec.setClearTextSensitive(false);
        tokenSpec.setNonIdempotentTokens(false);


        ////////////////////////////////////token/detoken single//////////////////////////////////////////////
        //Tokenization
        System.out.println("+++++++++++++++++++++++++++++++Token/Detoken for Single API++++++++++++++++++++++++++++++++++++++++++++++++++++");
        String dataToEncrypt = args[3] ;
        String token = ts.tokenize(dataToEncrypt , tokenSpec);
        System.out.println("Token generated : " + token);

        //Detokenization
        String data = ts.detokenize(token,tokenSpec) ;
        System.out.println("Data retrieved  : " + data);
        if(!dataToEncrypt.equals(data)){
            System.out.println("Test FAIL");
        }else
        {
            System.out.println("Test PASS");
        }
            ////////////////////////////////////token/detoken single//////////////////////////////////////////////


            ////////////////////////////////////token/detoken batch//////////////////////////////////////////////
            //Tokenization for Batch API
			//Hard coding the input values for batch
        System.out.println();
        System.out.println("+++++++++++++++++++++++++++++++Token/Detoken for Batch API ++++++++++++++++++++++++++++++++++++++++++++++++++++");
         String[] dataToEncryptBatch = {"8989191729303832" ,"971200625910987444"};
        System.out.println("Token generated for Batch : ");
        String[] tokenBatch = ts.tokenize(dataToEncryptBatch , tokenSpec);
        for (int i = 0; i < tokenBatch.length; i++) {
            System.out.println("" + tokenBatch[i]);
        }

        //DeTokenization for Batch API
        System.out.println("Data retrieved for Batch : ");
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
            System.out.println("Test PASS");
        }else{
            System.out.println("Test FAIL");
        }
        ////////////////////////////////////token/detoken batch//////////////////////////////////////////////

        //Close tokenService instance
        ts.closeService();
    }
}



