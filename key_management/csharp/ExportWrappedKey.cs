using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.Text;
using System.Security.Cryptography;
using CADP.NetCore.ExceptionHandler;
using System.IO;
using System.Linq;

namespace CADP.NetCoreNaeSamples
{
    /// <summary>
    /// This sample shows how to export an AES key wrapped using an RSA key.
    /// </summary>
    class ExportWrappedKey
    {
        private enum KeyType
        {
            RSA,
            AES
        }

        static void Main(string[] args)
        {
            SymmetricAlgorithm key = null;
            NaeRsaKey rsakey = null;

            NaeSession session = null;
            NaeKeyManagement nkm = null;

            string public_keyname = null;
            byte[] exportedpublicBytes = null;
            string aesKeyName = null;
            byte[] exportedFinalBytes = null;


            /*Read Username and password*/
            Console.Write("Enter username: ");
            string user = Console.ReadLine();
            Console.Write("Enter password: ");
            string pass = Console.ReadLine();
            string errorMsg = "";

            try
            {
                /*Reads the CADP.NETCore_Properties.xml from the nuget folder.
                  In case, of multiple versions available it will take the latest one.
                  Please update the code in case of below requirement:
                    1. latest version is not required to be picked.
                    2. custom location for the property file.
                */
                var propertyFilePath = string.Empty;
                string path = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                var cadpPackage = Path.Combine(path, ".nuget", "packages", "cadp.netcore");
                var highestPackage = Directory.GetDirectories(cadpPackage).Select(x => Path.GetFileName(x)).OrderByDescending(e => new Version(e)).First();
                propertyFilePath = Path.Combine(cadpPackage, highestPackage, "content", "CADP.NETCore_Properties.xml");

                // check again try catch why again?
                /* Create a new NAE Session using the username and password */
                try
                {
                    session = new NaeSession(user, pass, propertyFilePath);
                    Console.WriteLine("NaeSession created successfully.");
                    errorMsg = "Unable to create session.";
                }
                catch (NaeException e)
                {
                    Console.Write(errorMsg + e);
                    return;
                }
                catch (Exception ex)
                {
                    Console.Write(errorMsg + ex);
                    return;
                }

                while (true)
                {
                    Console.WriteLine("Enter the keyname (AES) to be wrapped");
                    aesKeyName = Console.ReadLine();
                    if (!string.IsNullOrEmpty(aesKeyName))
                        break;
                }
                /* Check if the key to be wrapped exists else create it. */
                nkm = new NaeKeyManagement(session);

                key = (NaeRijndaelKey)GetOrGenerateKey(nkm, session, aesKeyName, KeyType.AES);

                if(key == null)
                {
                    return;
                }

                /* Check if the wrapping key exists else create it. */

                while (true)
                {
                    Console.WriteLine("Enter the wrapping keyname(RSA)");
                    public_keyname = Console.ReadLine();
                    if (!string.IsNullOrEmpty(public_keyname))
                        break;
                }

                rsakey = (NaeRsaKey)GetOrGenerateKey(nkm, session, public_keyname, KeyType.RSA);
                if (rsakey == null)
                {
                    return;
                }


                try
                {
                    /*Export public key bytes*/
                    errorMsg = "Error in exporting RSA key.";
                    exportedpublicBytes = nkm.ExportKey(public_keyname, NaeKeyManagement.KeyType.Public);

                    /*Send AES keyName and RSA public key bytes to Key Manager for wrapping the AES key*/
                    errorMsg = "Error in exporting wrapped key.";
                    exportedFinalBytes = nkm.ExportWrappedKey(aesKeyName, exportedpublicBytes, NaeKeyManagement.KeyWrapFormat.PKCS1v15);

                    ///* To verify the wrapping result uncomment this code */

                    ///*************Verify result**************/
                    ///*Decrypt with the RSA key the exported wrapped bytes and match them with exported bytes of AES key.*/

                    ///*Export AES key Bytes*/
                    //errorMsg = "Error in exporting AES key bytes for verification.";
                    //byte[] symmbytes = nkm.ExportKey(aesKeyName, NaeKeyManagement.KeyType.None);

                    ///*Decrypt the wrapped AES bytes with RSA Key*/
                    //errorMsg = "Error in unwrapping key bytes.";
                    //NaeRsaKey n = new NaeRsaKey(session, public_keyname);
                    //byte[] decrypted = n.Decrypt(exportedFinalBytes, RSAEncryptionPadding.Pkcs1);
                }
                catch (Exception e)
                {
                    Console.WriteLine(errorMsg + e.Message);
                }

                /**Delete Key**/
                nkm.DeleteKey(aesKeyName);
                Console.WriteLine($"Key {aesKeyName}, deleted successfully.");
                nkm.DeleteKey(public_keyname);
                Console.WriteLine($"Key {public_keyname}, deleted successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error occurred. {ex.Message}");
            }
        }

        /// <summary>
        /// Gets the keyname if exists, else generate it.
        /// </summary>
        /// <param name="naeKeyManagement">nae Key Management</param>
        /// <param name="session">session</param>
        /// <param name="keyName">keyName to be generated.</param>
        /// <returns>The Key Object.</returns>
        private static INaeKey GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName, KeyType keyType)
        {
            INaeKey naeKey = null;
            try 
            { 
                if (keyType.Equals(KeyType.AES))
                {
                    naeKey = (NaeRijndaelKey)naeKeyManagement.GetKey(keyName);
                }
                else
                {
                    naeKey = (NaeRsaKey)naeKeyManagement.GetKey(keyName);
                }
            }
            catch (Exception e1)
            {
                Console.WriteLine($"Error occurred: {e1.Message}");
                if (keyType.Equals(KeyType.AES))
                {
                    NaeRijndaelKey rijndaelkey = new NaeRijndaelKey(session);
                    {
                        rijndaelkey.IsDeletable = true;
                        rijndaelkey.IsExportable = true;
                        rijndaelkey.KeySize = 128;
                    }
                    naeKey = rijndaelkey;
                }
                else
                {
                    NaeRsaKey naersakey = new NaeRsaKey(session);
                    {
                        naersakey.IsDeletable = true;
                        naersakey.IsExportable = true;
                        naersakey.KeySize = 1024;
                    }

                    naeKey = naersakey;
                }

                try
                {
                    /* If key does not exist, try creating a new RSA key */
                    Console.WriteLine($"Generating new {keyType} key.");
                    naeKey.GenerateKey(keyName);
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error occurred in generating {keyType} key: {e.Message}");
                    naeKey = null;
                }
            }

            return naeKey;
        }
    }
}