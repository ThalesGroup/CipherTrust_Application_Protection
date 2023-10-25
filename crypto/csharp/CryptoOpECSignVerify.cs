using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Linq;

class CryptoOpECSignVerify
{
    static void Main(string[] args)
    {
        NaeECIESKey key = null;
        NaeSession session = null;
        string keyName = "";
        byte[] inputBytes = null;
        byte[] outputBytes = null;

        /*Read Username and password*/
        Console.Write("Enter username: ");
        string user = Console.ReadLine();
        Console.Write("Enter password: ");
        string pass = string.Empty;
        ConsoleKeyInfo consoleKeyInfo;

        do
        {
            consoleKeyInfo = Console.ReadKey(true);

            //Handle backspace and remove the key.
            if (consoleKeyInfo.Key == ConsoleKey.Backspace)
            {
                Console.Write("\b \b");
                pass = (pass.Length > 0) ? pass.Remove(pass.Length - 1, 1) : pass;
            }
            else
            {
                //Not adding the function keys, other keys having key char as '\0' in the password string.
                if (consoleKeyInfo.KeyChar != '\0')
                {
                    pass += consoleKeyInfo.KeyChar;
                    Console.Write("*");
                }
            }
        }

        //Stops Receving Keys Once Enter is Pressed
        while (consoleKeyInfo.Key != ConsoleKey.Enter);

        //Cleaning up the newline character
        pass = pass.Replace("\r", "");
        Console.WriteLine();

        try
        {
            /*Read the CADP.NETCore_Properties.xml from the nuget folder. As per the configuration inside CADP.NETCore_Properties.xml application will run either in Local mode or Remote mode.
                In case, of multiple versions available it will take the latest one.
                Please update the code in case of below requirement:
                1. latest version is not required to be picked.
                2. custom location for the file */
            var propertyFilePath = string.Empty;
            string path = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            var cadpPackage = Path.Combine(path, ".nuget", "packages", "ciphertrust.cadp.netcore");
            var highestPackage = Directory.GetDirectories(cadpPackage).Select(x => Path.GetFileName(x)).OrderBy(x => Path.GetFileName(x)).Last();
            propertyFilePath = Path.Combine(cadpPackage, highestPackage, "content", "CADP.NETCore_Properties.xml");

            /* Create a new NAE Session using the username and password */
            session = new NaeSession(user, pass, propertyFilePath);
            Console.WriteLine("NaeSession Created successfully.");

            //Create NaeKeyManagement object
            NaeKeyManagement nkm = new NaeKeyManagement(session);

            //Get keyName from user
            Console.WriteLine("Enter the keyName");
            keyName = Console.ReadLine();

            /*Gets or Generate the key.
            Supported CurveId and KeySize: secp224k1-225, secp224r1- 224, secp256k1-256, secp384r1-384, secp521r1-521, prime256v1-256, brainpoolP224r1-224, brainpoolP224t1-224, brainpoolP256r1-256, brainpoolP256t1-256, brainpoolP384r1-384, brainpoolP384t1-384, brainpoolP512r1-512, brainpoolP512t1-512
            Ref: https://thalesdocs.com/ctp/cm/2.11/reference/xml/supp-key-algo/index.html#ec */
            key = GetOrGenerateKey(nkm, session, keyName, NaeECIESKey.SupportedCurves.brainpoolP256r1_256);

            //If key is null, return. Else proceed with further steps.
            if (key == null)
            {
                return;
            }

            //Read the input data form console
            Console.WriteLine("Please enter the input text");
            string input = Console.ReadLine();
            if (string.IsNullOrEmpty(input))
            {
                Console.WriteLine("Please enter a valid input");
                return;
            }
            inputBytes = Encoding.ASCII.GetBytes(input);

            try
            {
                //Sign Data
                Console.WriteLine("Sign Data:");
                outputBytes = key.SignData(inputBytes, HashAlgorithmName.SHA1);
                Console.WriteLine($"Signed Data Length: {Convert.ToString(outputBytes.Length)} \n Signed Data Bytes (B64 encoded): {Convert.ToBase64String(outputBytes)}");

                //Verify signed bytes
                Console.WriteLine("\n\nVerify Data:");
                bool result = key.VerifyData(inputBytes, 0, inputBytes.Length, outputBytes, HashAlgorithmName.SHA1);

                if (result)
                    Console.WriteLine("Sign/Verify successful");
                else
                    Console.WriteLine("SignVerify failed!");

            }
            catch (Exception e)
            {
                //Display error on console
                Console.WriteLine($"Error in sign/verify {e.Message}");
            }

            //Delete Key after using
            nkm.DeleteKey(keyName);
            Console.WriteLine($"Key {keyName}, deleted successfully.");

        }
        catch (Exception e)
        {
            //Display error on console
            Console.WriteLine($"Error check log file {e.Message}");
        }
    }
    /// <summary>
    /// Gets the keyname if exists, else generate it.
    /// </summary>
    /// <param name="naeKeyManagement">nae Key Management</param>
    /// <param name="session">session</param>
    /// <param name="keyName">keyName to be generated.</param>
    /// <param name="curve">curve from enum NaeECIESKey.SupportedCurves</param>
    /// <returns>The Key Object.</returns>
    private static NaeECIESKey GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName, NaeECIESKey.SupportedCurves curve)
    {
        NaeECIESKey eciesKey = null;
        try
        {
            //Check if key is already created
            eciesKey = (NaeECIESKey)naeKeyManagement.GetKey(keyName);
        }
        catch (Exception e1)
        {
            //Display error on console
            Console.WriteLine($"Error occurred: {e1.Message}");

            //Set NaeECIESKey parameters
            NaeECIESKey naeecieskey = new NaeECIESKey(session, curve);
            {
                naeecieskey.IsDeletable = true;
                naeecieskey.IsExportable = true;
            }
            eciesKey = naeecieskey;

            try
            {
                //If key does not exist, try creating a new EC key
                Console.WriteLine("Generating new key.");
                naeecieskey.GenerateKey(keyName);
            }
            catch (Exception e)
            {
                //Display error on console
                Console.WriteLine($"Error occurred: {e.Message}");
                eciesKey = null;
            }
        }

        //Return EC key object
        return eciesKey;
    }

}
