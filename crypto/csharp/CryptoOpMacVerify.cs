using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.Text;
using System.Security.Cryptography;
using System.IO;
using System.Linq;


/// <summary>
/// This samples show how to generate MAC and verify it.
/// </summary>
class NaeCryptoOpMACVerify
{
    static void Main(string[] args)
    {

        NaeHmacKey key = null;

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

            /*Initialize the CADP.NetCore library once for till library unloads. */
            NaeSession.Initialize(NaeSession.PropFileSource.file, propertyFilePath);

            /*Create a new NAE Session using the username and password */
            NaeSession session = new NaeSession(user, pass, null);
            Console.WriteLine("NaeSession created successfully.");

            NaeKeyManagement nkm = new NaeKeyManagement(session);
            Console.WriteLine("Enter the keyname");
            string keyname = Console.ReadLine();

            // Gets or Generate the key.
            key = GetOrGenerateKey(nkm, session, keyname);

            // If key is null, return. Else proceed with further steps.
            if (key == null)
            {
                return;
            }

            byte[] inputBytes;

            Console.Write("Enter data to calculate MAC: ");
            string input = Console.ReadLine();
            if (string.IsNullOrEmpty(input))
            {
                Console.WriteLine("Enter data to calculate MAC: ");
                return;
            }

            UTF8Encoding utf8 = new UTF8Encoding();
            inputBytes = utf8.GetBytes(input);
            try
            {
                //MAC request
                byte[] outBytes = key.GenerateMac(inputBytes);

                Console.WriteLine($"Mac Data {outBytes.Length} bytes (B64 encoded): {Convert.ToBase64String(outBytes)}");
                //MAC Verify request
                bool resVer = key.VerifyMac(inputBytes, outBytes);
                if (resVer == true)
                    Console.WriteLine("Mac verified successfully");
                else
                    Console.WriteLine("Mac verification failed");
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error in mac or mac verify {e.Message}");
            }
            //Delete Key
            nkm.DeleteKey(keyname);
            Console.WriteLine($"Key {keyname}, deleted successfully.");
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error check logfile for details on error. {e.Message}");
            return;
        }

    }
    /// <summary>
    /// Gets the keyname if exists, else generate it.
    /// </summary>
    /// <param name="naeKeyManagement">nae Key Management</param>
    /// <param name="session">session</param>
    /// <param name="keyName">keyName to be generated.</param>
    /// <returns>The Key Object.</returns>
    private static NaeHmacKey GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName)
    {
        NaeHmacKey naeHmacKey = null;
        //Other options for algorithm name are HmacSHA1, HmacSHA256, HmacSHA384 and HmacSHA512
        HmacAlgo algoEnum = HmacAlgo.HmacSHA512;
        string strAlgo = algoEnum.ToString();
        try
        {
            naeHmacKey = (NaeHmacKey)naeKeyManagement.GetKey(keyName);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error occured: {ex.Message}");
            NaeHmacKey hmacKey = new NaeHmacKey(session, algoEnum);
            hmacKey.IsDeletable = true;
            hmacKey.IsExportable = true;
            naeHmacKey = hmacKey;
            try
            {
                /* If key does not exist, try creating a new HMAC key */
                Console.WriteLine("Generating new key.");
                hmacKey.GenerateKey(keyName);
                naeHmacKey = hmacKey;

            }
            catch (Exception e)
            {
                Console.WriteLine($"Error occured: {e.Message}");
                naeHmacKey = null;
            }
        }

        return naeHmacKey;
    }
}

