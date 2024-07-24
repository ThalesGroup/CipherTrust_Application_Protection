using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;


namespace CADP.NetCoreNaeSamples
{
    /// <summary>
    /// This sample shows how to perform crypto-operations(Encrypt and Decrypt) using file encryption with AES.
    /// </summary>
    class CryptoOpFileEncryptionDecryption
    {
        static void Main(string[] args)
        {
            NaeRijndaelKey key = null;
            byte[] inputBytes = { };
            byte[] encrBytes = null;
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
                var highestPackage = Directory.GetDirectories(cadpPackage).Select(x => Path.GetFileName(x)).OrderBy(x => Path.GetFileName(x)).Last();
                propertyFilePath = Path.Combine(cadpPackage, highestPackage, "content", "CADP.NETCore_Properties.xml");

                /* Create a new NAE Session using the username and password */
                session = new NaeSession(user, pass, propertyFilePath);
                Console.WriteLine("NaeSession created successfully.");

                nkm = new NaeKeyManagement(session);
                Console.WriteLine("Enter the keyname");
                string keyname = Console.ReadLine();

                // Gets or Generate the key.
                key = GetOrGenerateKey(nkm, session, keyname);

                // If key is null, return. Else proceed with further steps.
                if (key == null)
                {
                    return;
                }

                Console.WriteLine("Enter the plain file path : ");
                string fileInPath = Console.ReadLine().Trim();

                if (!File.Exists(fileInPath))
                {
                    Console.WriteLine("File does not exist or invalid file path.");
                    return;
                }

                string fileInName = Path.GetFileName(fileInPath);
                string encryptedFilePath = Path.Combine(Directory.GetCurrentDirectory(), "Encrypted_" + fileInName);
                string decryptedFilePath = Path.Combine(Directory.GetCurrentDirectory(), "Decrypted_" + fileInName);

                /*Set IV , Padding and Mode*/
                byte[] iv = { 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35 };
                key.IV = iv;
                key.Padding = PaddingMode.PKCS7;
                key.Mode = CipherMode.CBC;

                try
                {
                    EncryptFile(fileInPath, encryptedFilePath, key);
                    DecryptFile(encryptedFilePath, decryptedFilePath, key);

                    bool isMatch = AreEqual(fileInPath, decryptedFilePath);
                    if (isMatch) { Console.WriteLine("input file and decrypted file contents are matching"); }
                    else
                    {
                        throw new Exception("Decrypted file contents are not matching with input file ");
                    }
                }

                catch (Exception e)
                {
                    Console.Write("Error in encrypting/decrypting the data \n{0}", e.Message);
                    Console.ReadLine();
                    return;
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
        /// <param name="naeKeyManagement">nae Key Management</param>
        /// <param name="session">session</param>
        /// <param name="keyName">keyName to be generated.</param>
        /// <returns>The Key Object.</returns>
        private static NaeRijndaelKey GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName)
        {
            NaeRijndaelKey naeRijndaelKey = null;
            try
            {

                naeRijndaelKey = (NaeRijndaelKey)naeKeyManagement.GetKey(keyName);

                /* Other way to get key is:
                 *  NaeRijndaelKey rijndaelkey = new NaeRijndaelKey(session, keyname);
                 */
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error occurred: {e.Message}");
                NaeRijndaelKey rijndaelkey = new NaeRijndaelKey(session);
                {
                    rijndaelkey.IsDeletable = true;
                    rijndaelkey.IsExportable = true;
                    rijndaelkey.KeySize = 128;
                }
                naeRijndaelKey = rijndaelkey;
                try
                {
                    /* If key does not exist, try creating a new AES key */
                    Console.WriteLine("Generating a new key.");
                    rijndaelkey.GenerateKey(keyName);
                }
                catch (Exception excp)
                {
                    Console.WriteLine($"Error occurred: {excp.Message}");
                    naeRijndaelKey = null;
                }
            }

            return naeRijndaelKey;
        }
        private static void EncryptFile(string fileIn, string fileOut, NaeRijndaelKey key)
        {
            char[] _fileIn = fileIn.ToCharArray();
            char[] _fileOut = fileOut.ToCharArray();

            using (FileStream fsIn = new FileStream(string.Concat(_fileIn), FileMode.Open, FileAccess.Read))
            {
                using (FileStream fsOut = new FileStream(string.Concat(_fileOut), FileMode.OpenOrCreate, FileAccess.Write))
                {

                    ICryptoTransform encryptor = key.CreateEncryptor(fsIn);
                    using (CryptoStream cs = new CryptoStream(fsOut, encryptor, CryptoStreamMode.Write))
                    {
                        try
                        {

                            int bufferLen = 81920;
                            byte[] buffer = new byte[bufferLen];

                            int bytesRead;
                            do
                            {   // read a chunk of data from the input file
                                bytesRead = fsIn.Read(buffer, 0, bufferLen);                          // encrypt it
                                cs.Write(buffer, 0, bytesRead);
                            }
                            while (bytesRead != 0);
                            Array.Clear(buffer, 0, buffer.Length);
                            buffer = null;
                            encryptor.Dispose();
                        }
                        catch (Exception e)


                        { throw new Exception("Error occurred while encrypting file: " + e.Message); }
                    }
                    fsOut.Close();
                }
                fsIn.Close();
            }
        }
        private static void DecryptFile(string fileIn, string fileOut, NaeRijndaelKey key)
        {
            char[] _fileIn = fileIn.ToCharArray();
            char[] _fileOut = fileOut.ToCharArray();

            using (FileStream fsIn = new FileStream(string.Concat(_fileIn), FileMode.Open, FileAccess.Read))
            {
                using (FileStream fsOut = new FileStream(string.Concat(_fileOut), FileMode.OpenOrCreate, FileAccess.Write))
                {
                    ICryptoTransform decryptor = key.CreateDecryptor(fsIn);
                    using (CryptoStream cs = new CryptoStream(fsOut, decryptor, CryptoStreamMode.Write))
                    {
                        try
                        {

                            int bufferLen = 81920;
                            byte[] buffer = new byte[bufferLen];

                            int bytesRead;
                            do
                            {
                                bytesRead = fsIn.Read(buffer, 0, bufferLen);
                                cs.Write(buffer, 0, bytesRead);
                            }
                            while (bytesRead != 0);
                            Array.Clear(buffer, 0, buffer.Length);
                            buffer = null;
                            decryptor.Dispose();
                        }
                        catch (Exception e)


                        { throw new Exception("Error occurred while decrypting file: " + e.Message); }
                    }
                    fsOut.Close();
                }
                fsIn.Close();
            }
        }

        public static bool AreEqual(string expFilepath, string actFilePath)
        {
            int bytesRead;
            int BufferSize = 81920;
            using (var expectFs = new FileStream(expFilepath, FileMode.Open, FileAccess.Read))
            {
                using (var actFs = new FileStream(actFilePath, FileMode.Open, FileAccess.Read))
                {
                    if (expectFs.Length != actFs.Length)
                    {
                        return false;
                    }

                    byte[] expBuffer, actBuffer = new byte[BufferSize];
                    expBuffer = new byte[BufferSize];

                    do
                    {
                        bytesRead = expectFs.Read(expBuffer);
                        actFs.Read(actBuffer);

                        if (!expBuffer.SequenceEqual(actBuffer))
                        { return false; }

                    } while (bytesRead != 0);

                    return true;
                }
            }
        }
    }
}