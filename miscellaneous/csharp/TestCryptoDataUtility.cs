using CADP.NetCore.Sessions;
using CryptoDataUtility;
using System;
using System.IO;
using System.Linq;

namespace CADP.NetCoreNaeSamples
{
    class SampleApp
    {
        static void Main(string[] args)
        {
            var errorMessage = @"Please provide command line arguments to use the sample!
 Usage
 Parameter 1 : Key name to be used for crypto operation
 Parameter 2 : Text to encrypt.";

            if(args == null || args.Length != 2)
            {
                Console.WriteLine(errorMessage);
                return;
            }

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
                
                // Reading the command line arguments.
                string keyName = args[0];
                string plaintext = args[1];

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

                // construct NAESession object
                NaeSession session = new NaeSession(user, pass, propertyFilePath);

                // or change to a different NAESession constructor
                // construct encryption utility object
                SymmetricEncryptionUtility utility = new SymmetricEncryptionUtility(session);

                // Encrypt
                byte[] encrypted = utility.Encrypt(System.Text.Encoding.UTF8.GetBytes(plaintext),
                keyName);
                Console.WriteLine("Encrypted: " + Convert.ToBase64String(encrypted));

                // Decrypt
                //Note :- We are not giving any keyname here for decryption, only
                //thing provided is the cipher text.
                byte[] decrypted = utility.Decrypt(encrypted);
                Console.WriteLine("Decrypted: " + System.Text.Encoding.UTF8.GetString(decrypted));
                Console.WriteLine("Done!");
            }
            catch(Exception ex)
            {
                Console.WriteLine($"Error Occurred: {ex.Message}");
            }
        }
    }
}
