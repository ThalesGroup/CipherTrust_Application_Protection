using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.Text;
using System.Security.Cryptography;
using System.IO;
using System.Linq;
using System.Collections.Generic;


namespace CADP.NetCoreNaeSamples
{
    //Keys Should be available in CM with the provided custem attributes.

    /// <summary>
    /// This sample shows how to get the list key names using GetKeyNmaes.
    /// </summary>
    class GetKeyNames
    {
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

               
                session = new NaeSession(user, pass, propertyFilePath);
                Console.WriteLine("NaeSession created successfully.");
				
				// Adding the custom attributes on the basis of which the keys would be fetched. 
                NaeCustomAttr customAttribute1 = new NaeCustomAttr();
                customAttribute1.attrKey = "KeyType";
                customAttribute1.attrValue = "AES";

                NaeCustomAttr customAttribute2 = new NaeCustomAttr();
                customAttribute2.attrKey = "KeyType";
                customAttribute2.attrValue = "RSA";

                List<NaeCustomAttr> lst = new List<NaeCustomAttr>();
                lst.Add(customAttribute1);
                lst.Add(customAttribute2);
                
                NaeKeyNameAttr attr = new NaeKeyNameAttr();
                attr.ConjunctiveOpr = NaeKeyNameAttr.ConjunctiveOperator.OR;
                attr.CustomAttributes = lst;
                attr.maxKeys = 10;
                attr.keyOffset = 0;
                attr.fingerprint = "";
                
                nkm = new NaeKeyManagement(session);

                string[] keyNames = nkm.GetKeyNames(attr);

                Console.WriteLine("Keynames : ");
                if (keyNames.Length != 0)
                {
                    foreach (string keyName in keyNames)
                    {
                        Console.WriteLine(keyName);
                    }

                    Console.WriteLine();

                    Console.WriteLine("TotalKeyCount = " + attr.totalKeyCount);
                    Console.WriteLine("KeyCount = " + attr.keyCount);
                }
                else 
                    Console.WriteLine("No Keys Found with the provided Attributes");
                    
                string[] keyNamesTotal = nkm.GetKeyNames();
                //print the total number of keys accessible by the user
                Console.WriteLine($"Number of keys accessible by the user: {user}: {keyNamesTotal.Length}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in running the code. {ex.Message}");
            }
        }

    }
}