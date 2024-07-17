using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;

namespace CADP.NetCoreNaeSamples
{
    /// ***************Prerequisites**************************
    /// NAE versioned key should be present on CipherTrust Manager and UUID must be known.
    /// ******************************************************
    /// 
    /// <summary>
    /// This sample shows how to fetch key name, key version and correspondig version header bytes using UUID for NAE versioned key.
    /// For non versioned key, -1 will be returned with Null header bytes.
    /// </summary>
    class NaeGetKeyVersionById
    {
        static void Main(string[] args)
        {
            NaeSession session;
            NaeKeyManagement nkm;


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

                Console.WriteLine("Enter the UUID");
                string uuid = Console.ReadLine();

                nkm = new NaeKeyManagement(session);

                VersionInfo keyDetails = nkm.GetKeyVersionById(uuid, NaeKeyManagement.KeyIdType.UUID);

                Console.WriteLine("Keyname: " + keyDetails.KeyName);

                //For non versioned NAE key, returned version will be -1 and header bytes are null
                if (keyDetails.Version != -1)
                {
                    Console.WriteLine($"Version: {keyDetails.Version}");
                    // For printing to console converting the header bytes to Base64 encoded string
                    Console.WriteLine($"Version Header (B64 encoded): {Convert.ToBase64String(keyDetails.Header)}");
                }
                else
                {
                    Console.WriteLine("Founded Key is non versioned");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in running the code. {ex.Message}");
            }
        }
    }
}
