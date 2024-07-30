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
    /// This sample shows how to perform crypto-operations(Encrypt and Decrypt) using AES-GCM mode.
    /// </summary>
    class NaeCryptoOpAesGcm
    {
        const int TAG_LENGTH = 14;
        static void Main(string[] args)
        {
            const string Default_AAD = "TestAadData";
            byte[] inputBytes = { };
            NaeSession session = null;
            NaeKeyManagement nkm = null;
            NaeAesGcm gcm = null;

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

                /* Create a new NAE Session using the username and password as string */
                session = new NaeSession(user, pass, propertyFilePath);

                Console.WriteLine("NaeSession created successfully.");

                nkm = new NaeKeyManagement(session);
                Console.WriteLine("Enter the keyname");
                string keyname = Console.ReadLine();

                // Gets or Generate the key.
                gcm = GetOrGenerateKey(nkm, session, keyname);

                // If key is null, return. Else proceed with further steps.
                if (gcm == null)
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

                //The nonce sizes supported by this instance: 12 bytes (96 bits).
                //which should be a unique value for every operation with the same key.
                byte[] nonce = new byte[12];
                Random random = new Random();
                random.NextBytes(nonce);

                try
                {
                    byte[] tag = null;

                    byte[] encData = gcm.Encrypt(nonce, inputBytes, out tag, Encoding.ASCII.GetBytes(Default_AAD));
                    Console.WriteLine($"Tag data: {BitConverter.ToString(tag).Replace("-", string.Empty)}");
                    byte[] decData = gcm.Decrypt(nonce, encData, tag, Encoding.ASCII.GetBytes(Default_AAD));

                    Console.WriteLine($"Decrypted data: {Encoding.Default.GetString(decData)}");
                }
                catch (Exception e)
                {
                    Console.Write($"Error in encrypting/decrypting the data \n{e.Message}");
                    Console.ReadLine();
                    return;
                }
                finally
                {
                    gcm.Dispose();
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
        /// <param name="naeKeyManagement">Nae Key Management</param>
        /// <param name="session">session</param>
        /// <param name="keyName">keyName to be generated.</param>
        /// <returns>The Key Object.</returns>
        private static NaeAesGcm GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName)
        {
            NaeAesGcm naeAesGcm = null;
            try
            {
                naeAesGcm = new NaeAesGcm(session, keyName, TAG_LENGTH);
            }
            catch (CryptographicException ex)
            {
                Console.WriteLine($"Error : {ex.Message}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error occurred: {e.Message}");
                naeAesGcm = new NaeAesGcm(session);
                {
                    naeAesGcm.IsDeletable = true;
                    naeAesGcm.IsExportable = true;
                    naeAesGcm.TagLen = TAG_LENGTH;
                    naeAesGcm.KeySize = 256;
                }
                try
                {
                    /* If key does not exist, try creating a new AES key */
                    Console.WriteLine("Generating a new key.");
                    naeAesGcm.GenerateKey(keyName);
                }
                catch (Exception excp)
                {
                    Console.WriteLine($"Error occurred: {excp.Message}");
                    naeAesGcm = null;
                }
            }

            return naeAesGcm;
        }
    }
}