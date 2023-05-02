using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.Text;
using System.Security.Cryptography;
using System.IO;
using System.Linq;

namespace CADP.NetCoreNaeSamples
{
    /// <summary>
    /// This sample shows how to encrypt and decrypt data using FPE.
    /// </summary>
    class NaeCryptoOpFpe
    {
        static void Main(string[] args)
        {
            SymmetricAlgorithm key = null;
            byte[] inputBytes = { };
            byte[] encrBytes = null;
            NaeSession session = null;
            NaeKeyManagement nkm = null;

            /*Read Username and password*/
            Console.Write("Enter username: ");
            string user = Console.ReadLine();
            Console.Write("Enter password: ");
            string pass = string.Empty;
            ConsoleKeyInfo consoleKeyInfo;

            do
            {
                consoleKeyInfo = Console.ReadKey(true);

                // Handle backspace and remove the key.
                if (consoleKeyInfo.Key == ConsoleKey.Backspace)
                {
                    Console.Write("\b \b");
                    pass = (pass.Length > 0) ? pass.Remove(pass.Length - 1, 1) : pass;
                }
                else
                {
                    // Not adding the function keys, other keys having key char as '\0' in the password string.
                    if (consoleKeyInfo.KeyChar != '\0')
                    {
                        pass += consoleKeyInfo.KeyChar;
                        Console.Write("*");
                    }
                }
            }
            // Stops Receving Keys Once Enter is Pressed
            while (consoleKeyInfo.Key != ConsoleKey.Enter);

            // cleaning up the newline character
            pass = pass.Replace("\r", "");
            Console.WriteLine();

            try
            {
                /*Read the CADP.NETCore_Properties.xml from the nuget folder.
                  In case, of multiple versions available it will take the latest one.
                  Please update the code in case of below requirement:
                    1. latest version is not required to be picked.
                    2. custom location for the file
                */
                var propertyFilePath = string.Empty;
                string path = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                var cadpPackage = Path.Combine(path, ".nuget", "packages", "ciphertrust.cadp.netcore");
                var highestPackage = Directory.GetDirectories(cadpPackage).Select(x => Path.GetFileName(x)).OrderByDescending(e => new Version(e)).First();
                propertyFilePath = Path.Combine(cadpPackage, highestPackage, "content", "CADP.NETCore_Properties.xml");

                /* Create a new NAE Session using the username and password */
                session = new NaeSession(user, pass, propertyFilePath);
                Console.WriteLine("NaeSession created successfully.");

                Console.WriteLine("Enter the keyName");
                string keyName = Console.ReadLine();
                if (!GetOrGenerateKey(session, keyName))
                    return;
				
	        nkm = new NaeKeyManagement(session);

                try
                {
                    UserSpec userSpec = new UserSpec();
                    userSpec.TweakAlgo = "SHA1";
                    userSpec.TweakData = "SampleTweakData";
		    
		    // Below constructor will be deprecated in future.
                    // This constructor will be used for FPE/AES/CARD10, FPE/AES/CARD26, FPE/AES/CARD62 only, for any other FPE Algo refer below section.
                    key = new NaeFpe(session, keyName, NaeFpe.Cardinality.CARD10, userSpec);
			
		    /* Below constructor and parameters will be used for FPE algorithms with NaeFpe.AlgorithmName having options as 
                     * FPE_AES_CARD10, FPE_AES_CARD26, FPE_AES_CARD62, FPE_AES_UNICODE.
                     * FPE_FF1v2_CARD10, FPE_FF1v2_CARD26, FPE_FF1v2_CARD62, FPE_FF1v2_UNICODE.
                     * FPE_FF3_CARD10, FPE_FF3_CARD26, FPE_FF3_CARD62, FPE_FF3_UNICODE.
                     * Charset is mandatory for Unicode, it is comma separated and can have ranegs (separated with '-') and single values. Refer below example.*/
                    //var charset = "0100-017F,F900-FA2D,A490-A4A1,A4A4-A4B3,A4B5-A4C0,A4C2-A4C4, A4C6";
                    //key = new NaeFpe(session, keyName, NaeFpe.AlgorithmName.FPE_AES_UNICODE, userSpec, charset);
			
		    /* For versioned keys, below are the two header modes supported
		     * 1. Internal header mode : version key header adjusted in cipher data. No explicit handling needed for it to work.
		     * 2. External header mode : version key header needs explicit handling.
						 Set the optional versionKeyHeaderSupported paramater as VersionKeyHeaderSupported.External_Header_Supported in NaeFpe Constructor.Refer below example- 
			                         //key = new NaeFpe(session, keyName, NaeFpe.AlgorithmName.FPE_AES_UNICODE, userSpec, charset,null, VersionKeyHeaderSupported.External_Header_Supported);
						 Get version key header after encryption using GetExternalHeader() API and then set it at the time of decryption using SetExternalHeader(header) API. */  
                    
		}
                catch (Exception e)
                {
                   Console.WriteLine($"Error occurred: {e.Message}");
                   return;
                }

                /*Read the input data form console*/
                Console.WriteLine("Please enter the input text");
                string input = Console.ReadLine();
                if (string.IsNullOrEmpty(input))
                {
                    Console.WriteLine("Please enter a valid input");
                    return;
                }

                inputBytes = Encoding.ASCII.GetBytes(input);
		
		/* For FPE UNICODE algorithm, the input bytes should be encoded using UT8 and not ASCII. */
                // inputBytes = Encoding.UTF8.GetBytes(input);
		
		/* For FPE set IV only when data size is greater than its block size eg CARD10: 56, CARD26: 40, CARD62:32.
                 * UNICODE, the block size is calculated based on Cardinality. */
		    
                /*Set IV only when data size is more than 56 Bytes */
                if (inputBytes.Length > 56)
                {
                    byte[] iv = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5 };
                    key.IV = iv;
                }

                try
                {
                    /*Create encryptor to Encyrpt the input bytes.*/
                    using (var encryptor = key.CreateEncryptor())
                    {
                        using (var memstr = new System.IO.MemoryStream())
                        {
                            /* Create a crypto stream and encrypt data */
                            using (var encrstr = new CryptoStream(memstr, encryptor, CryptoStreamMode.Write))
                            {
                                encrstr.Write(inputBytes, 0, inputBytes.Length);
                            }
                            encrBytes = memstr.ToArray();
                            Console.WriteLine($"Encrypted Data: {new String(new UTF8Encoding().GetChars(encrBytes))}");
                        }
                    }
                    
		    /* for external header mode, uncomment the below lines */
		    // byte[] header = ((NaeFpe)key).GetExternalHeader();
		    // ((NaeFpe)key).SetExternalHeader(header);

                    /*Create decryptor to Decyrpt the encrypted bytes.*/
                    using (var decryptor = key.CreateDecryptor())
                    {
                        using (var memstr2 = new System.IO.MemoryStream())
                        {
                            /* Create a crypto stream and decrypt data */
                            using (var decrstr = new CryptoStream(memstr2, decryptor, CryptoStreamMode.Write))
                            {
                                decrstr.Write(encrBytes, 0, encrBytes.Length);
                            }
                            byte[] decrBytes = memstr2.ToArray();
                            Console.WriteLine($"Decrypted {Convert.ToString(decrBytes.Length)} bytes: {new String(Encoding.UTF8.GetChars(decrBytes))}");
                        }

                    }
                }
                catch (Exception e)
                {
                    Console.Write($"Error in encrypting/decrypting the data \n{e.Message}");
                    Console.ReadLine();
                    return;
                }

                //Delete Key
                nkm.DeleteKey(keyName);
                Console.WriteLine($"Key {keyName}, deleted successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in running the code. {ex.Message}");
            }
        }
        private static bool GetOrGenerateKey(NaeSession session, string keyName)
        {
            bool result = false;
            SymmetricAlgorithm key;
            /* Try to get the key. If the key does not exist, we will create a new AES key
            */
            try
            {
                NaeKeyManagement nkm = new NaeKeyManagement(session);
                key = (NaeRijndaelKey)nkm.GetKey(keyName);
                result = true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in getting key {keyName}");

                NaeRijndaelKey rijndaelkey = new NaeRijndaelKey(session);
                {
                    rijndaelkey.IsDeletable = true;
                    rijndaelkey.IsExportable = true;
                    rijndaelkey.KeySize = 256;
                }
                key = rijndaelkey;
                try
                {
                    /* If key does not exist, try creating a new AES key */
                    Console.WriteLine("Generating a new key.");
                    rijndaelkey.GenerateKey(keyName);
                    result =  true;
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error occurred: {e.Message}");
                }

            }
            return result;
        }
    }
}
