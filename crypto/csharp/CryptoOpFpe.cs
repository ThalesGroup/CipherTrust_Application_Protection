﻿using CADP.NetCore.Crypto;
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
    /// This sample shows how to encrypt and decrypt data using FPE.
    /// </summary>
    class NaeCryptoOpFpe
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
            string pass = Console.ReadLine();

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

                Console.WriteLine("Enter the keyName");
                string keyName = Console.ReadLine();
                if (!GetOrGenerateKey(session, keyName))
                    return;
				
				nkm = new NaeKeyManagement(session);

                try
                {
                    UserSpec userSpec = new UserSpec();
                    userSpec.TweakAlgo = "SHA1";
                    userSpec.TweakData = "SampleTweakData";

                    key = new NaeFpe(session, keyName, NaeFpe.Cardinality.CARD10, userSpec);
                }
                catch (Exception e)
                {
                   Console.WriteLine($"Error occurred: {e.Message}");
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


                /*Set IV only when data size is more than 56 Bytes */
                if (inputBytes.Length > 56)
                {
                    byte[] iv = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5 };
                    key.IV = iv;
                }

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
                            Console.WriteLine($"Encrypted Data: {new String(new UTF8Encoding().GetChars(encrBytes))}");
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
                    Console.Write($"Error in encrypting/decrypting the data \n{e.Message}");
                    Console.ReadLine();
                    return;
                }

                //Delete Key
                nkm.DeleteKey(keyName);
                Console.WriteLine($"Key {keyName}, deleted successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in running the code. {ex.Message}");
            }
        }
        private static bool GetOrGenerateKey(NaeSession session, string keyName)
        {
            bool result = false;
            SymmetricAlgorithm key;
            /* Try to get the key. If the key does not exist, we will create a new AES key
            */
            try
            {
                NaeKeyManagement nkm = new NaeKeyManagement(session);
                key = (NaeRijndaelKey)nkm.GetKey(keyName);
                result = true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in getting key {keyName}");

                NaeRijndaelKey rijndaelkey = new NaeRijndaelKey(session);
                {
                    rijndaelkey.IsDeletable = true;
                    rijndaelkey.IsExportable = true;
                    rijndaelkey.KeySize = 256;
                }
                key = rijndaelkey;
                try
                {
                    /* If key does not exist, try creating a new AES key */
                    Console.WriteLine("Generating a new key.");
                    rijndaelkey.GenerateKey(keyName);
                    result =  true;
                }
                catch (Exception e)
                {
                    Console.WriteLine($"Error occurred: {e.Message}");
                }

            }
            return result;
        }
    }
}
