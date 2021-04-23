package com.thales.cm.rest.cmhelper;

import java.io.IOException;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args ) 
    {
        
		CipherTrustManagerHelper awsresrest =  new CipherTrustManagerHelper();
		
		String results = null;
		String sensitive = "HelloWorld";
		
		awsresrest.username = "admin";
		awsresrest.password = "yourpwd";
		awsresrest.cmipaddress = "192.168.159.160";
		
		try {
			String tkn = awsresrest.getToken();

			awsresrest.key = "MyAESEncryptionKey26";
			System.out.println( "Original Data "  + sensitive );
			results =  awsresrest.cmRESTProtect(  "gcm",  sensitive,  "encrypt");
			System.out.println( "Print results for encrypt"  + results);
			results =  awsresrest.cmRESTProtect(  "gcm",  results,  "decrypt");
			System.out.println( "Print results for decrypt "  + results);
		
			awsresrest.key = "rsa-key5";
			results =  awsresrest.cmRESTSign( "SHA1", "na", sensitive,"sign");
			System.out.println( "Print results for sign"  + results);
			results =  awsresrest.cmRESTSign(  "SHA1",  results, sensitive,   "signv");
			System.out.println( "Print results for verify "  + results);
			
			awsresrest.key = "hmacsha256-1";
			results =  awsresrest.cmRESTMac( "na", sensitive,"mac");
			System.out.println( "Print results for mac "  + results);
			results =  awsresrest.cmRESTMac( results, sensitive,   "macv");
			System.out.println( "Print results for verify "  + results);
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
    }
}
