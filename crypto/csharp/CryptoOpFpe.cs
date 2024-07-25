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
                /*
                 * Read the CADP.NETCore_Properties.xml from the nuget folder.
                 *In case, of multiple versions available it will take the latest one.
                 *Please update the code in case of below requirement:
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

                Console.Write("\nPlease select mode to continue:\n" +
                                   "  1. Non versioned key\n" +
                                   "  2. Versioned key internal header\n" +
                                   "  3. Versioned key external header\n" +
                                   "Enter option number: ");
                int mode = Convert.ToInt32(Console.ReadLine().Trim());

                if (mode < 1 || mode > 3)
                {
                    Console.WriteLine("Invalid option selected !");
                    return;
                }
                Console.Write("\nEnter the keyName: ");
                string keyName = Console.ReadLine();

                if (!GetOrGenerateKey(session, keyName, mode))
                    return;

                nkm = new NaeKeyManagement(session);

                UserSpec userSpec = new UserSpec();
                userSpec.TweakAlgo = "SHA1";
                userSpec.TweakData = "SampleTweakData";
                try
                {
                    /* Below constructor and parameters will be used for FPE algorithms with NaeFpe.AlgorithmName having options as 
                     * FPE_AES_CARD10, FPE_AES_CARD26, FPE_AES_CARD62, FPE_AES_UNICODE.
                     * FPE_FF1v2_CARD10, FPE_FF1v2_CARD26, FPE_FF1v2_CARD62, FPE_FF1v2_UNICODE.
                     * FPE_FF3_CARD10, FPE_FF3_CARD26, FPE_FF3_CARD62, FPE_FF3_UNICODE.
                     * Charset is mandatory for Unicode, it is comma separated and can have ranegs (separated with '-') and single values. Refer below example.*/
                    //var charset = "0100-017F,F900-FA2D,A490-A4A1,A4A4-A4B3,A4B5-A4C0,A4C2-A4C4, A4C6";
                    //key = NaeFpe( session, keyName, algoName, userSpec, charset, null, versionKeyHeaderSupported);;

                    switch (mode)
                    {
                        case 1: //non versioned key
                            key = new NaeFpe(session, keyName, NaeFpe.AlgorithmName.FPE_AES_CARD10, userSpec);
                            break;
                        case 2: //internal header
                            key = new NaeFpe(session, keyName, NaeFpe.AlgorithmName.FPE_AES_CARD10, userSpec, null, null, VersionKeyHeaderSupported.Internal_Header_Supported);
                            break;
                        case 3: //external header
                            key = new NaeFpe(session, keyName, NaeFpe.AlgorithmName.FPE_AES_CARD10, userSpec, null, null, VersionKeyHeaderSupported.External_Header_Supported);
                            break;
                    }

                    // Below constructor will be deprecated in future.
                    // This constructor will be used for FPE/AES/CARD10, FPE/AES/CARD26, FPE/AES/CARD62 only.
                    //key = new NaeFpe(session, keyName, NaeFpe.Cardinality.CARD10, userSpec);
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error occurred: {e.Message}");
                    Console.ReadLine();
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

                /*Set IV only when data size is more than block size of the cardinality. */
                // The block size for CARD 10.
                var blockSizeForCard10 = new KeyValuePair<int, int>(10, 56);
                if (inputBytes.Length > blockSizeForCard10.Value)
                {
                    byte[] iv = new byte[blockSizeForCard10.Value];
                    Random random = new Random();
                    for (int i = 0; i < blockSizeForCard10.Value; i++)
                    {
                        iv[i] = (byte)random.Next(0, blockSizeForCard10.Key);
                    }

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

                    if (mode == 3)/*external header case, for internal header nothing needs to handle explicitly*/
                    {
                        byte[] header = ((NaeFpe)key).GetExternalHeader();
                        Console.WriteLine($"External header bytes: {BitConverter.ToString(header)}");
                        ((NaeFpe)key).SetExternalHeader(header);
                    }

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
        private static bool GetOrGenerateKey(NaeSession session, string keyName, int mode)
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
                    
                    if (mode == 2 || mode == 3)
                    {
                        rijndaelkey.GenerateKey(keyName + "#");
                        Console.WriteLine("Generating a new versioned key.");
                    }
                    else
                    {
                        Console.WriteLine("Generating a new key.");
                        rijndaelkey.GenerateKey(keyName);
                    }
                    result = true;
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
