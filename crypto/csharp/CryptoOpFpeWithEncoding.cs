using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace CryptoOpFpeWithEncoding
{
    /// <summary>
    /// This sample shows how to encrypt and decrypt data using FPE Unicode with different Encodings.
    /// </summary>
    class NaeCryptoOpFpeWithEncoding
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
                var highestPackage = Directory.GetDirectories(cadpPackage).Select(x => Path.GetFileName(x)).OrderBy(x => Path.GetFileName(x)).Last();
                propertyFilePath = Path.Combine(cadpPackage, highestPackage, "content", "CADP.NETCore_Properties.xml");

                /* Create a new NAE Session using the username and password */
                session = new NaeSession(user, pass, propertyFilePath);
                Console.WriteLine("NaeSession created successfully.");

                Console.WriteLine("Enter the keyName");
                string keyName = Console.ReadLine();
                if (!GetOrGenerateKey(session, keyName))
                    return;

                nkm = new NaeKeyManagement(session);

                //Set Algorithm
                /* Below constructor and parameters will be used for FPE algorithms with NaeFpe.AlgorithmName having options as 
                   * FPE_FF1v2_UNICODE , FPE_FF3_UNICODE, FPE_AES_UNICODE
                */
                NaeFpe.AlgorithmName algorithm = NaeFpe.AlgorithmName.FPE_AES_UNICODE;

                //Set charset
                /* Charset is mandatory for Unicode, it is comma separated and can have ranegs (separated with '-') and single values. Refer below example.
                  *i.e: charset = "0100-017F,F900-FA2D,A490-A4A1,A4A4-A4B3,A4B5-A4C0,A4C2-A4C4, A4C6";
                  *charset ="0100,0101,0102,0103,0104,0105";
                */
                var charset = "0100,0101,0102,0103,0104,0105";

                //Set Encoding
                /*Below mention encoding we can use
                 Encoding.UTF8, Encoding.Unicode (UTF-16LE), Encoding.BigEndianUnicode (UTF-16BE), Encoding.UTF32 
                */
                Encoding encoding = Encoding.UTF32;

                try
                {
                    UserSpec userSpec = new UserSpec();
                    userSpec.TweakAlgo = "SHA1";
                    userSpec.TweakData = "SampleTweakData";

                    key = new NaeFpe(session, keyName, algorithm, userSpec, charset, encoding);
                }
               catch (Exception e)
               {
                   Console.WriteLine($"Error occurred: {e.Message}");
                   return;
               }

               /*Setting the input based on charset provided in the sampe application.*/                
                string input = "ĀĀāāĂĂăă";
                if (string.IsNullOrEmpty(input))
                {
                    Console.WriteLine("Please enter a valid input");
                    return;
                }

                //For FPE UNICODE algorithm, the input bytes should be encoded based on encoding
                if (encoding == null || encoding == Encoding.UTF8)
                {
                    inputBytes = Encoding.UTF8.GetBytes(input);
                }
                else if (encoding == Encoding.Unicode) // UTF-16LE
                {
                    inputBytes = Encoding.Unicode.GetBytes(input);
                }
                else if (encoding == Encoding.BigEndianUnicode) // UTF-16BE
                {
                    inputBytes = Encoding.BigEndianUnicode.GetBytes(input);

                }
                else if (encoding == Encoding.UTF32) // UTF-32LE
                {
                    inputBytes = Encoding.UTF32.GetBytes(input);
                }

                Console.WriteLine($"Encoding used: {encoding.EncodingName}");
                Console.WriteLine($"Input Bytes: {BitConverter.ToString(inputBytes).Replace('-', ' ')}");

                /* For FPE UNICODE IV block size is calculated based on Cardinality. 
                 * The value of each hex encoded byte in the IV value will be in the range 00 to (cardinality-1). 
                 * For example, when Charset is 26 , the maximum value will be 0x19 (hex encode of 26-1=25).
                 */
                byte[] iv = null;
                key.IV = iv;

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
                            Console.WriteLine($"Encrypted Bytes: {BitConverter.ToString(encrBytes).Replace('-', ' ')}");
                        }
                    }

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
                            string Decrypted_decrBytes_len = Convert.ToString(decrBytes.Length);
                            Console.WriteLine($"Decrypted Bytes: {BitConverter.ToString(decrBytes).Replace('-', ' ')}");
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
                    result = true;
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error occurred: {e.Message}");
                }

            }
            return result;
        }
        /// <summary>
        /// ByteToString method use for convert byte to string as per encoding
        /// </summary>
        /// <param name="encoding"></param>
        /// <param name="bytes"></param>
        /// <returns></returns>
        private static string ByteToString(Encoding encoding, byte[] bytes)
        {
            string rtnVal = string.Empty;
            try
            {
                if (encoding == null || encoding == Encoding.UTF8) // UTF-8
                {
                    rtnVal = new String(new UTF8Encoding().GetChars(bytes));
                }
                else if (encoding == Encoding.Unicode) // UTF-16LE
                {
                    rtnVal = new String(new UnicodeEncoding().GetChars(bytes));
                }
                else if (encoding == Encoding.BigEndianUnicode) // UTF-16BE 
                {
                    rtnVal = Encoding.BigEndianUnicode.GetString(bytes);

                }
                else if (encoding == Encoding.UTF32) // UTF-32
                {
                    rtnVal = new String(new UTF32Encoding().GetChars(bytes));
                }
            }
            catch(Exception ex)
            {
                Console.WriteLine($"Error in running the code. {ex.Message}");
            }
            return rtnVal;
        }
    }
}
