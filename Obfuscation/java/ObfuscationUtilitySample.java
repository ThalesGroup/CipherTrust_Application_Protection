

import java.util.Scanner;

import com.ingrian.security.nae.IngrianProvider;

/**
 * 
 * @author shivali This class is used to provide obfuscated value
 *
 */
public class ObfuscationUtilitySample {

	public static void main(String []dataToEncrypt) {
		String encryptData=null;
		
        if (dataToEncrypt.length==0) {
                 Scanner sc =new Scanner(System.in);
			System.out.println("Please Enter Text to be Encrypted:");
			encryptData = sc.next();      
		}
		else{
         encryptData=dataToEncrypt[0];	
		}		 
		
		String encrptedData = null;
		try {
			encrptedData = IngrianProvider.obfuscate(encryptData.getBytes()
					);
		} catch (Exception e) {
			e.printStackTrace();
		}
		System.out.println("Encrypted Text: " + encrptedData);

	}
	}