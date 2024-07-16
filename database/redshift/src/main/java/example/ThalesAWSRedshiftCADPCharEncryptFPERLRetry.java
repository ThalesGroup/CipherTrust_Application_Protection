package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestStreamHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.logging.Logger;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.spec.IvParameterSpec;
import org.apache.commons.io.IOUtils;

import com.google.common.util.concurrent.RateLimiter;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import com.google.gson.JsonParser;
import com.google.gson.JsonPrimitive;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;

/*
 * This test app to test the logic for a Redshift Database User Defined
 * Function(UDF). It is an example of how to use Thales Cipher Trust Application Data Protection (CADP)
 * to protect sensitive data in a column. This example uses
 * Format Preserve Encryption (FPE) to maintain the original format of the data
 * so applications or business intelligence tools do not have to change in order
 * to use these columns.  
 * 
 * Note: This source code is only to be used for testing and proof of concepts.
 * Not production ready code. Was not tested for all possible data sizes and
 * combinations of encryption algorithms and IV, etc. Was tested with CM 2.14 &
 * CADP 8.15.0.001 For more information on CADP see link below.   
*  For more details on how to write Redshift UDF's please see
*  https://docs.aws.amazon.com/redshift/latest/dg/udf-creating-a-lambda-sql-udf.html#udf-lambda-json
*     
 */

public class ThalesAWSRedshiftCADPCharEncryptFPERLRetry implements RequestStreamHandler {
    private static final Logger logger = Logger.getLogger(ThalesAWSRedshiftCADPCharEncryptFPERLRetry.class.getName());
    private static final Gson gson = new Gson();
    private static final int MAX_RETRIES = 3;
   // private static final double REQUESTS_PER_SECOND = 5.0; // Adjust this rate as needed
    private static final double REQUESTS_PER_SECOND = 10.0; // Adjust this rate as needed

    private static final RateLimiter rateLimiter = RateLimiter.create(REQUESTS_PER_SECOND);

    public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {
        rateLimiter.acquire(); // Acquire a permit from the rate limiter
        System.out.println("rate limit set to = " + rateLimiter.getRate());
        String input = IOUtils.toString(inputStream, "UTF-8");
        JsonParser parser = new JsonParser();
        NAESession session = null;
        int statusCode = 200;

        String redshiftreturnstring = null;
        StringBuffer redshiftreturndata = new StringBuffer();

        boolean status = true;

        JsonObject redshiftinput = null;
        JsonElement rootNode = parser.parse(input);
        JsonArray redshiftdata = null;
        String redshiftuserstr = null;

        if (rootNode.isJsonObject()) {
            redshiftinput = rootNode.getAsJsonObject();
            if (redshiftinput != null) {
                redshiftdata = redshiftinput.getAsJsonArray("arguments");
                JsonPrimitive userjson = redshiftinput.getAsJsonPrimitive("user");
                redshiftuserstr = userjson.getAsJsonPrimitive().toString();
                redshiftuserstr = redshiftuserstr.replace("\"", "");
            } else {
                System.out.println("Root node not found.");
            }
        } else {
            System.out.println("Bad data from snowflake.");
        }

        JsonPrimitive nbr_of_rows_json = redshiftinput.getAsJsonPrimitive("num_records");
        String nbr_of_rows_json_str = nbr_of_rows_json.getAsJsonPrimitive().toString();
        int nbr_of_rows_json_int = Integer.parseInt(nbr_of_rows_json_str);

        String keyName = "testfaas";
        String userName = System.getenv("CMUSER");
        String password = System.getenv("CMPWD");

        String returnciphertextforuserwithnokeyaccess = System.getenv("returnciphertextforuserwithnokeyaccess");
		boolean returnciphertextbool = returnciphertextforuserwithnokeyaccess.equalsIgnoreCase("yes");

        String usersetlookup = System.getenv("usersetlookup");
        String usersetID = System.getenv("usersetidincm");
        String userSetLookupIP = System.getenv("usersetlookupip");
		boolean usersetlookupbool = usersetlookup.equalsIgnoreCase("yes");

        int attempt = 0;
        boolean success = false;

        while (attempt < MAX_RETRIES && !success) {
            try {
                redshiftreturndata.append("{ \"success\":");
                redshiftreturndata.append(status);
                redshiftreturndata.append(",");
                redshiftreturndata.append(" \"num_records\":");
                redshiftreturndata.append(nbr_of_rows_json_int);
                redshiftreturndata.append(",");
                redshiftreturndata.append(" \"results\": [");

    			if (usersetlookupbool) {
    				// make sure cmuser is in Application Data Protection Clients Group

    					boolean founduserinuserset = findUserInUserSet(redshiftuserstr, userName, password, usersetID,
    							userSetLookupIP);
    					// System.out.println("Found User " + founduserinuserset);
    					if (!founduserinuserset)
    						throw new CustomException("1001, User Not in User Set", 1001);

    				} else {
    					usersetlookupbool = false;
    				}

                System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename", "CADP_for_JAVA.properties");
                IngrianProvider builder = new Builder().addConfigFileInputStream(
                        getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();

                session = NAESession.getSession(userName, password.toCharArray());
                NAEKey key = NAEKey.getSecretKey(keyName, session);

                String algorithm = "FPE/FF1/CARD62";
                String tweakAlgo = null;
                String tweakData = null;
                FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo).build();

                Cipher encryptCipher = Cipher.getInstance(algorithm, "IngrianProvider");
                encryptCipher.init(Cipher.ENCRYPT_MODE, key, param);
                redshiftreturnstring = doTransform(encryptCipher, redshiftdata, redshiftreturndata);

                success = true; // Mark success if no exceptions occurred
            } catch (Exception e) {
                attempt++;
                if (attempt >= MAX_RETRIES) {
                    handleException(e, redshiftreturndata, redshiftdata, returnciphertextbool);
                    redshiftreturnstring = new String(redshiftreturndata);
                    statusCode = 400;
                } else {
                    logger.warning("Attempt " + attempt + " failed, retrying...");
                }
            } finally {
                if (session != null) {
                    session.closeSession();
                }
            }
        }
        success = true;
        outputStream.write(new Gson().toJson(redshiftreturnstring).getBytes());
    }

    private void handleException(Exception e, StringBuffer redshiftreturndata, JsonArray redshiftdata, boolean returnciphertextbool) {
        String sensitive = null;
        if (returnciphertextbool) {
            if (e.getMessage().contains("1401") || e.getMessage().contains("1001") || e.getMessage().contains("1002")) {
                for (int i = 0; i < redshiftdata.size(); i++) {
                    JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();
                    if (redshiftrow != null && redshiftrow.size() > 0) {
                        JsonElement element = redshiftrow.get(0);
                        if (element != null && !element.isJsonNull()) {
                            sensitive = element.getAsString();
                            if (sensitive.isEmpty()) {
                                JsonElement elementforNull = new JsonPrimitive("null");
                                sensitive = elementforNull.getAsJsonPrimitive().toString();
                            } else {
                                sensitive = element.getAsJsonPrimitive().toString();
                            }
                        } else {
                            JsonElement elementforNull = new JsonPrimitive("null");
                            sensitive = elementforNull.getAsJsonPrimitive().toString();
                        }
                    }
                    redshiftreturndata.append(sensitive);
                    if (redshiftdata.size() != 1 && i != redshiftdata.size() - 1) {
                        redshiftreturndata.append(",");
                    }
                }
                redshiftreturndata.append("]}");
            }
        }
    }

    public boolean findUserInUserSet(String userName, String cmuserid, String cmpwd, String userSetID, String userSetLookupIP) throws Exception {
        CMUserSetHelper cmuserset = new CMUserSetHelper(userSetID, userSetLookupIP);
        String jwthtoken = CMUserSetHelper.geAuthToken(cmuserset.authUrl, cmuserid, cmpwd);
        String newtoken = "Bearer " + CMUserSetHelper.removeQuotes(jwthtoken);
        return cmuserset.findUserInUserSet(userName, newtoken);
    }

    public String doTransform(Cipher encryptCipher, JsonArray redshiftdata, StringBuffer redshiftreturndata) throws IllegalBlockSizeException, BadPaddingException {
        String encdata = "";
        String redshiftreturnstring = null;
        String sensitive = null;
        for (int i = 0; i < redshiftdata.size(); i++) {
            JsonArray redshiftrow = redshiftdata.get(i).getAsJsonArray();
            if (redshiftrow != null && redshiftrow.size() > 0) {
                JsonElement element = redshiftrow.get(0);
                if (element != null && !element.isJsonNull()) {
                    sensitive = element.getAsString();
                    if (sensitive.isEmpty() || sensitive.length() < 2) {
                        if (sensitive.isEmpty()) {
                            JsonElement elementforNull = new JsonPrimitive("null");
                            sensitive = elementforNull.getAsJsonPrimitive().toString();
                        } else {
                            sensitive = element.getAsJsonPrimitive().toString();
                        }
                        encdata = sensitive;
                    } else {
                        if (sensitive.equalsIgnoreCase("null")) {
                            sensitive = element.getAsJsonPrimitive().toString();
                            encdata = sensitive;
                        } else {
                            sensitive = element.getAsJsonPrimitive().toString();
                            byte[] outbuf = encryptCipher.doFinal(sensitive.getBytes());
                            encdata = new String(outbuf);
                       
                        }
                    }
                } else {
                    JsonElement elementforNull = new JsonPrimitive("null");
                    sensitive = elementforNull.getAsJsonPrimitive().toString();
                    System.out.println("Sensitive data is null or empty.");
                    encdata = sensitive;
                }
            } else {
                JsonElement elementforNull = new JsonPrimitive("null");
                sensitive = elementforNull.getAsJsonPrimitive().toString();
                System.out.println("redshiftrow is null or empty.");
                encdata = sensitive;
            }
            redshiftreturndata.append(encdata);
            if (redshiftdata.size() != 1 && i != redshiftdata.size() - 1) {
                redshiftreturndata.append(",");
            }
        }
        redshiftreturndata.append("]}");
        redshiftreturnstring = new String(redshiftreturndata);
        return redshiftreturnstring;
    }

    public String formatReturnValue(int statusCode) {
        StringBuffer redshiftreturndata = new StringBuffer();
        String errormsg = "\"Error in UDF \"";
        redshiftreturndata.append("{ \"success\":");
        redshiftreturndata.append(false);
        redshiftreturndata.append(" \"num_records\":");
        redshiftreturndata.append(0);
        redshiftreturndata.append(",");
        redshiftreturndata.append(" \"error_msg\":");
        redshiftreturndata.append(errormsg);
        redshiftreturndata.append(",");
        redshiftreturndata.append(" \"results\": [] }");
        return redshiftreturndata.toString();
    }
}
