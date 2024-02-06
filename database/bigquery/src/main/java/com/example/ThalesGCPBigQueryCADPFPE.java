package com.example;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.ingrian.security.nae.FPEParameterAndFormatSpec;
import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecureRandom;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.FPEParameterAndFormatSpec.FPEParameterAndFormatBuilder;
import com.ingrian.security.nae.IngrianProvider.Builder;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonPrimitive;

import java.util.logging.Logger;

public class ThalesGCPBigQueryCADPFPE implements HttpFunction {
//  @Override
	/* This sample GCP Function is used to implement a BigQuery User Defined Function(UDF).  It is an example of how to use Thales Cipher Trust Manager Protect Application
	 * to protect sensitive data in a column.  This example uses Format Preserve Encryption (FPE) to maintain the original format of the 
	 * data so applications or business intelligence tools do not have to change in order to use these columns.
	*  
	*  Note: This source code is only to be used for testing and proof of concepts. Not production ready code.  Was not tested
	*  for all possible data sizes and combinations of encryption algorithms and IV, etc.  
	*  Was tested with CM 2.11 & CADP 8.13
	*  For more information on CADP see link below. 
	https://thalesdocs.com/ctp/con/cadp/cadp-java/latest/admin/index.html
	 *@author  mwarner
	 * 
	 */  
  private static final Logger logger = Logger.getLogger(ThalesGCPBigQueryCADPFPE.class.getName());
  private static final Gson gson = new Gson();
  public void service(HttpRequest request, HttpResponse response)
      throws Exception {
	 
	  String encdata = "";
      String keyName =  "testfaas";
      String userName =  System.getenv("CMUSER");
      String password =  System.getenv("CMPWD");
      
		String bigqueryreturnstring = null;
		StringBuffer bigqueryreturndata = new StringBuffer();
    
    //  Optional<String> parm = request.getFirstQueryParameter("parm");
      
      String bigquerysessionUser = "" ;
      JsonElement bigqueryuserDefinedContext = null ;
      String mode = null;
      String datatype = null;
   
	    try {
            


            // Parse JSON request and check for "name" field
            JsonObject requestJson = null;
            try {
              JsonElement requestParsed = gson.fromJson(request.getReader(), JsonElement.class);
  

              if (requestParsed != null && requestParsed.isJsonObject()) {
                requestJson = requestParsed.getAsJsonObject();
              }

              if (requestJson != null && requestJson.has("sessionUser")) {
                bigquerysessionUser  = requestJson.get("sessionUser").getAsString();
                System.out.println("name " + bigquerysessionUser );
              }
              
              if (requestJson != null && requestJson.has("userDefinedContext")) {
            	  bigqueryuserDefinedContext  = requestJson.get("userDefinedContext");
                  JsonObject location = requestJson.getAsJsonObject("userDefinedContext");
                   mode = location.get("mode").getAsString();                
                  datatype = location.get("datatype").getAsString();                

                }
              

            } catch (JsonParseException e) {
              logger.severe("Error parsing JSON: " + e.getMessage());
            }
     
   

            JsonArray bigquerydata	 = requestJson.getAsJsonArray("calls");
 
			//System.setProperty("com.ingrian.security.nae.NAE_IP.1", "10.20.1.9");
			System.setProperty("com.ingrian.security.nae.CADP_for_JAVA_Properties_Conf_Filename",
					"CADP_for_JAVA.properties");
			IngrianProvider builder = new Builder().addConfigFileInputStream(
					getClass().getClassLoader().getResourceAsStream("CADP_for_JAVA.properties")).build();
			NAESession session = NAESession.getSession(userName, password.toCharArray());
			NAEKey key = NAEKey.getSecretKey(keyName, session);
			NAESecureRandom rng = new NAESecureRandom(session);

			byte[] iv = new byte[16];
			rng.nextBytes(iv);
			IvParameterSpec ivSpec = new IvParameterSpec(iv);

			// Serialization

			bigqueryreturndata.append("{ \"replies\": [");

			int cipherType = 0;
			String algorithm = "FPE/FF1/CARD62";
			
			if (mode.equals("encrypt"))
				cipherType = Cipher.ENCRYPT_MODE;
			else
				cipherType = Cipher.DECRYPT_MODE;
			if (datatype.equals("char"))
				algorithm = "FPE/FF1/CARD62";
			else
				algorithm = "FPE/FF1/CARD10";
					
			// String algorithm = "AES/CBC/PKCS5Padding";
			String tweakAlgo = null;
			String tweakData = null;
			FPEParameterAndFormatSpec param = new FPEParameterAndFormatBuilder(tweakData).set_tweakAlgorithm(tweakAlgo)
					.build();
			///
			ivSpec = param;
			Cipher thalesCipher = Cipher.getInstance(algorithm, "IngrianProvider");


			for (int i = 0; i < bigquerydata.size(); i++) {
				JsonArray bigquerytrow = bigquerydata.get(i).getAsJsonArray();
				String sensitive = bigquerytrow.getAsString();
				//String sensitive = bigquerycolumn.getAsJsonPrimitive().toString();
				// initialize cipher to encrypt.
				
				thalesCipher.init(cipherType, key, ivSpec);
				// encrypt data
				byte[] outbuf = thalesCipher.doFinal(sensitive.getBytes());
				encdata = new String(outbuf);
				// System.out.println("Enc data : " + encdata);

				bigqueryreturndata.append(encdata);
				if (bigquerydata.size() == 1 || i == bigquerydata.size() - 1)
					continue;
				else
					bigqueryreturndata.append(",");
			}

			bigqueryreturndata.append("]}");

			bigqueryreturnstring = new String(bigqueryreturndata);


		} catch (Exception e) {


			System.out.println("in exception with ");
			e.printStackTrace(System.out);
		}
	    
	    String formattedString = formatString(bigqueryreturnstring);

	      response.getWriter().write(formattedString);
	    
  }
  
	public static String formatString(String inputString) {
        // Split the input string to isolate the array content
        String[] parts = inputString.split("\\[")[1].split("\\]")[0].split(",");

        // Reformat the array elements to enclose them within double quotes
        StringBuilder formattedArray = new StringBuilder();
        for (String part : parts) {
            formattedArray.append("\"").append(part.trim()).append("\",");
        }

        // Build the final formatted string
        return inputString.replaceFirst("\\[.*?\\]", "[" + formattedArray.deleteCharAt(formattedArray.length() - 1) + "]");
    }
	
}