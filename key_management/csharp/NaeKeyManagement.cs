using System;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace CADP.NetCoreNaeSamples
{
    /// <summary>
    /// This sample shows how to access the GetKeyAttributes of any key.
    /// </summary>
    class NaeKeyManagementSample
    {
        public enum AttrType
        {
            System,
            Custom
        }
        public static void PrintKeyAttributes(Dictionary<string, object> attributes, AttrType attrType)
        {
            if (attrType == AttrType.System)
            {
                Console.WriteLine("Printing System Attribute(s) : ");

                foreach (var attr in attributes)
                {
                    if (attr.Key.Contains("Algorithm"))
                    {
                        Console.WriteLine(attr.Key + " : " );
                        List<string> algorithms = (List<string>)attr.Value;
                        foreach (var algo in algorithms)
                        {
                            Console.WriteLine(algo);
                        }
                    }
                    else
                    {
                        Console.WriteLine(attr.Key + " : " + attr.Value.ToString());
                    }
                }
            }
            else
            {
                Console.WriteLine("Printing Custom Attribute(s) : ");
                try
                {
                    foreach (var attr in attributes)
                    {
                        Console.WriteLine( attr.Key + " : "+ attr.Value.ToString());
                    }
                }
                catch(Exception ex)
                {
                    Console.WriteLine($"Custom Attribute is not present : {ex.Message}");
                }
            }
        }

        static void Main(string[] args)
        {
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

                nkm = new NaeKeyManagement(session);
                Console.WriteLine("Enter the keyname");
                string keyname = Console.ReadLine();

                Dictionary<string, object> SystemAttr = new Dictionary<string, object>();
                Dictionary<string, object> CustomAttr = new Dictionary<string, object>();

				/* Get the key attributes of the keyname */
                bool status = nkm.GetKeyAttributes(keyname, SystemAttr, CustomAttr);

                if (status)
                {
                    PrintKeyAttributes(SystemAttr, AttrType.System);
                    PrintKeyAttributes(CustomAttr, AttrType.Custom);
                }
                else
                {
                    Console.WriteLine("Error in getting Key Attribute.");
                }
            }
            catch(Exception ex)
            {
                Console.WriteLine($"Error occurred: {ex.Message}");
                return;
            }
            Console.Read();
        }
    }
}
