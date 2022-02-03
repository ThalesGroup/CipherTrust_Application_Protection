using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.Text;
using System.Security.Cryptography;
using System.IO;
using System.Linq;

/// <summary>
/// This sample shows how to perform crypto-operations(Encrypt and Decrypt) using RSA key.
/// </summary>
class CryptoOpRsaEncDec
{
    static void Main(string[] args)
    {
        NaeRsaKey key = null;
        byte[] inputBytes = null;
        string keyname;
        
        NaeSession session = null;

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

            NaeKeyManagement nkm = new NaeKeyManagement(session);
            Console.WriteLine("Enter the keyname");
            keyname = Console.ReadLine();

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


            RSAEncryptionPadding padding = RSAEncryptionPadding.OaepSHA256;
            try
            {
                //Encrypt Data
                byte[] encrBytes = key.Encrypt(inputBytes, padding);
                Console.WriteLine($"Encrypted Data {Convert.ToString(encrBytes.Length)} bytes (B64 encoded): {Convert.ToBase64String(encrBytes)}");

                //Decrypt Data
                byte[] decrBytes = key.Decrypt(encrBytes, padding);
                Console.WriteLine($"Decrypted {Convert.ToString(decrBytes.Length)} bytes: {new String(Encoding.UTF8.GetChars(decrBytes))}");

            }
            catch (Exception e)
            {
                Console.WriteLine($"Error in Encrypt/Decrypt {e.Message}");
            }

            //DeleteKey
            nkm.DeleteKey(keyname);
            Console.WriteLine($"Key {keyname}, deleted successfully.");
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error in Encrypt/Decrypt {e.Message}");
        }
    }

    /// <summary>
    /// Gets the keyname if exists, else generate it.
    /// </summary>
    /// <param name="naeKeyManagement">Nae Key Management</param>
    /// <param name="session">session</param>
    /// <param name="keyName">keyName to be generated.</param>
    /// <returns>The Key Object.</returns>
    private static NaeRsaKey GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName)
    {
        NaeRsaKey rsaKey = null;
        try
        {
            rsaKey = (NaeRsaKey)naeKeyManagement.GetKey(keyName);

            /* Other way to get key is:
            *  NaeRsaKey key = new NaeRsaKey(session, keyname);
            */
        }
        catch (Exception e1)
        {
            Console.WriteLine($"Error occurred: {e1.Message}");

            NaeRsaKey naersakey = new NaeRsaKey(session);
            {
                naersakey.IsDeletable = true;
                naersakey.IsExportable = true;
                naersakey.KeySize = 2048;
            }
            rsaKey = naersakey;
            try
            {
                /* If key does not exist, try creating a new RSA key */
                Console.WriteLine("Generating new key.");
                naersakey.GenerateKey(keyName);
            }

            catch (Exception e)
            {
                Console.WriteLine($"Error occurred: {e.Message}");
                rsaKey = null;
            }
        }

        return rsaKey;
    }
}