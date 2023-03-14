

import java.util.Scanner;

import com.ingrian.security.nae.IngrianProvider;

/**
 * 
 * @author shivali This class is used to provide obfuscated value
 *
 */
public class ObfuscationUtilitySample {

	public static void main(String []dataToEncrypt) {
	
		Scanner sc =new Scanner(System.in);
		System.out.println("Enter text to be encrypted");
        String str = sc.next();      
		
		if ("".equalsIgnoreCase(str) || str == null) {
			System.exit(-1);
		}
		String encrptedData = null;
		try {
			encrptedData = IngrianProvider.obfuscate(str.getBytes()
					);
		} catch (Exception e) {
			e.printStackTrace();
		}
		System.out.println("Obfuscate data=" + encrptedData);

	}
	}

