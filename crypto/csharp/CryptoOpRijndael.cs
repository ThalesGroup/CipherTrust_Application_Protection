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
    /// This sample shows how to perform crypto-operations(Encrypt and Decrypt) using AES mode.
    /// </summary>
    class NaeCryptoOpRijndael
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

                nkm = new NaeKeyManagement(session);
                Console.WriteLine("Enter the keyname");
                string keyname = Console.ReadLine();

                // Gets or Generate the key.
                key = GetOrGenerateKey(nkm, session, keyname);

                // If key is null, return. Else proceed with further steps.
                if (key == null)
                {
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


                /*Set IV , Padding and Mode*/
                byte[] iv = { 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35 };
                key.IV = iv;
                key.Padding = PaddingMode.PKCS7;
                key.Mode = CipherMode.CBC;

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
                            Console.WriteLine($"Encrypted Data (B64 encoded): {Convert.ToBase64String(encrBytes)}");
                        }
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
                    Console.Write("Error in encrypting/decrypting the data \n{0}", e.Message);
                    Console.ReadLine();
                    return;
                }

                //Delete Key
                nkm.DeleteKey(keyname);
                Console.WriteLine($"Key {keyname}, deleted successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in running the code. {ex.Message}");
            }
        }

        /// <summary>
        /// Gets the keyname if exists, else generate it.
        /// </summary>
        /// <param name="naeKeyManagement">nae Key Management</param>
        /// <param name="session">session</param>
        /// <param name="keyName">keyName to be generated.</param>
        /// <returns>The Key Object.</returns>
        private static NaeRijndaelKey GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName)
        {
            NaeRijndaelKey naeRijndaelKey = null;
            try
            {

                naeRijndaelKey = (NaeRijndaelKey)naeKeyManagement.GetKey(keyName);

                /* Other way to get key is:
                 *  NaeRijndaelKey rijndaelkey = new NaeRijndaelKey(session, keyname);
                 */
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error occurred: {e.Message}");
                NaeRijndaelKey rijndaelkey = new NaeRijndaelKey(session);
                {
                    rijndaelkey.IsDeletable = true;
                    rijndaelkey.IsExportable = true;
                    rijndaelkey.KeySize = 128;
                }
                naeRijndaelKey = rijndaelkey;
                try
                {
                    /* If key does not exist, try creating a new AES key */
                    Console.WriteLine("Generating a new key.");
                    rijndaelkey.GenerateKey(keyName);
                }
                catch (Exception excp)
                {
                    Console.WriteLine($"Error occurred: {excp.Message}");
                    naeRijndaelKey = null;
                }
            }

            return naeRijndaelKey;
        }
    }
}