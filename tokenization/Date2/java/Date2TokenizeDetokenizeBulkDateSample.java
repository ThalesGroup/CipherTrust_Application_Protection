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
 * This sample shows how to tokenize and detokenize bulk date using Date2 algorithm.
 */
public class Date2TokenizeDetokenizeBulkDateSample
{
    public static void main( String[] args ) throws Exception
    {

        if (args.length < 9)
        {
            System.err.println("Usage: java Date2TokenizeDetokenizeBulkDateSample username password keyName startYear endYear "
                    + "dateFormat dateToTokenize dateFormatScheme preserve tweakData(Optional)");
            /*
             * Usage: username : key manager user name
             * Usage: password : key manager password
             * Usage: keyName : supports AES Non-versioned key
             * Usage: startYear : start year for date2 algorithm
             * Usage: endYear : end year for date2 algorithm
             * Usage: dateFormat : format of date in which user want to tokenize and detokenize date
             * Usage: dateToTokenize : array of input date that needs to be tokenized eg. 24/11/1997,01/01/2003,31/12/2009
             * Usage: dateFormatScheme : if provided, the value must be a string - ddMMyyyy/ddMMyy/MMyyyy/MMyy
             * Usage: preserve : if provided, the value must be a string - NONE/YEAR_MONTH/MONTH/YEAR
             * Usage: tweakData(Optional) : if provided, the value must be a string
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
        String[] dateToTokenize = args[6].split(",");
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
            //Print date format scheme and all other input parameters
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

            System.out.println("Start Year : " + date2ParameterSpec.getStartYearAsString());
            System.out.println("End Year : " + date2ParameterSpec.getEndYearAsString());
            System.out.println("Date Format Scheme : " + date2ParameterSpec.getDateFormatScheme());
            System.out.println("Date Format : " + dateFormat);
            System.out.println("Preserve : " + date2ParameterSpec.getPreserve());
            System.out.println("Tweak : " + date2ParameterSpec.getTweakData());

            //create the Tokenization Service: pass in algorithm, key and algorithm parameter spec
            TokenizationService tokenizationService =TokenizationFactory.getTokenizationService("DATE2", key, date2ParameterSpec);

            if(tokenizationService!=null) {

                byte[][] tokenizedOutput = tokenizeBulkDate(dateToTokenize, tokenizationService, dateFormat);

                for(int i=0; i< tokenizedOutput.length; i++) {
                    System.out.println("Tokenized date for "+ dateToTokenize[i] +" : " + new String(tokenizedOutput[i]));
                }

                byte[][] detokenizedOutput = detokenizeBulkDate(tokenizedOutput, tokenizationService, dateFormat);

                for(int i=0; i<detokenizedOutput.length; i++) {
                    System.out.println("Detokenized date for "+ new String(tokenizedOutput[i]) +" : " + new String(detokenizedOutput[i]));
                }

                //cleanup
                tokenizationService.cleanup();

                //check the detokenize date with user input date
                for(int i=0; i<dateToTokenize.length; i++){
                    String detokenizedDate = new String(detokenizedOutput[i]);

                    if(!detokenizedDate.equalsIgnoreCase(dateToTokenize[i]))
                        throw new Exception("=== Date To Tokenize "+ dateToTokenize[i]+" and Detokenized date "+detokenizedDate+" are NOT equal ===");

                    System.out.println("=== Date To Tokenize "+ dateToTokenize[i]+" and Detokenized date "+detokenizedDate+" are equal ===");
                }
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


    private static byte[][] tokenizeBulkDate(String[] dateToTokenize, TokenizationService tokenizationService, String dateFormat){
        //2D array that will store tokenized date
        byte[][] tokenizedOutput = new byte[dateToTokenize.length][];

        for(int i=0; i< dateToTokenize.length; i++) {
            //tokenize the date
            tokenizedOutput[i] = tokenizationService.tokenize(dateToTokenize[i].getBytes(), dateFormat);
        }

        return tokenizedOutput;
    }

    private static byte[][] detokenizeBulkDate(byte[][] tokenizedOutput, TokenizationService tokenizationService, String dateFormat){
        //2D array that will store detokenized date
        byte[][] detokenizedOutput = new byte[tokenizedOutput.length][];

        for(int i=0; i<tokenizedOutput.length; i++) {
            //detokenize the date
            detokenizedOutput[i] = tokenizationService.detokenize(tokenizedOutput[i], dateFormat);
        }

        return detokenizedOutput;
    }
}
