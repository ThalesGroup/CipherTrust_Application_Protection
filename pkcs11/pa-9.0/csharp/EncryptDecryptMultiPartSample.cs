using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;


namespace Vormetric.Pkcs11Sample
{
    class EncryptDecryptMultiPartSample : ISample
    {
        public bool Run(object[] inputParams)
        {
            using (Pkcs11 pkcs11 = new Pkcs11(Settings.Pkcs11LibraryPath, false))
            {
                // Find first slot with token present
                Slot slot = Helpers.GetUsableSlot(pkcs11);

                // Open RW session
                using (Session session = slot.OpenSession(false))
                {
                    string pin = Convert.ToString(inputParams[0]);
                    string keyLabel = Convert.ToString(inputParams[1]);
                    string pathSource = Convert.ToString(inputParams[2]); 
                    bool needMetaData = Convert.ToBoolean(inputParams[3]);

                    if(String.IsNullOrEmpty(pathSource))
                        pathSource = Settings.Pkcs11LibraryPath;

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    // Prepare attribute template that defines search criteria
                    List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));

                    // Initialize searching
                    session.FindObjectsInit(objectAttributes);

                    // Get search results
                    List<ObjectHandle> foundObjects = session.FindObjects(1);

                    // Terminate searching
                    session.FindObjectsFinal();

                    if (foundObjects.Count < 1)
                        return false;

                    ObjectHandle foundKey = foundObjects[0];

                    byte[] iv = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A,
                             0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 };

                    // Specify encryption mechanism with initialization vector as parameter
                    Mechanism mechanism = new Mechanism(CKM.CKM_AES_CBC_PAD, iv);
                    // Specify a file to read from and to create. 
                    
                    string pathCipherSource = @".\TestEncryptedResult.dat";
                    string pathDeCipherSource = @".\TestDecryptedResult.dat";
                    // META data string must start with "META:"
                    byte[] metaData = ConvertUtils.Utf8StringToBytes("META: This is the meta data to put into the log");
                    
                    using (FileStream sourceFileStream = new FileStream(pathSource, FileMode.Open, FileAccess.Read),
                    cipherSourceStream = new FileStream(pathCipherSource, FileMode.Create, FileAccess.Write))
                    {
                        // Encrypt data multi part
                        Console.WriteLine("Encrypted File: " + pathSource + " into " + pathCipherSource);
                        if ( needMetaData)
                            session.Encrypt(mechanism, foundKey, sourceFileStream, cipherSourceStream, metaData);
                        else
                            session.Encrypt(mechanism, foundKey, sourceFileStream, cipherSourceStream);
                    }
  
                    
                    using (FileStream decipherSourceStream = new FileStream(pathDeCipherSource, FileMode.Create, FileAccess.Write),
                    cipherSourceFileStream = new FileStream(pathCipherSource, FileMode.Open, FileAccess.Read))
                    {
                        Console.WriteLine("Decrypted File: " + pathCipherSource + " into " + pathDeCipherSource);
                        if ( needMetaData )
                            session.Decrypt(mechanism, foundKey, cipherSourceFileStream, decipherSourceStream, metaData);
                        else
                            session.Decrypt(mechanism, foundKey, cipherSourceFileStream, decipherSourceStream);
                    }
                    
                    // now do file comparison 
                    Console.WriteLine("Comparing source file and decrypted source file...: " );

                    // Do something interesting with decrypted data
                    if (FilesAreEqual(new FileInfo(pathSource), new FileInfo(pathDeCipherSource)))
                    {
                        Console.WriteLine("Source and Decrypted Data Matches!");
                    }
                    session.Logout();

                    slot.CloseSession(session);
                }
            }
            return true;
        }

        public const int BYTES_TO_READ = sizeof(Int64);

        public static bool FilesAreEqual(FileInfo first, FileInfo second)
        {
            if (first.Length != second.Length)
                return false;

            int iterations = (int)Math.Ceiling((double)first.Length / BYTES_TO_READ);

            using (FileStream fs1 = first.OpenRead())
            using (FileStream fs2 = second.OpenRead())
            {
                byte[] one = new byte[BYTES_TO_READ];
                byte[] two = new byte[BYTES_TO_READ];

                for (int i = 0; i < iterations; i++)
                {
                    fs1.Read(one, 0, BYTES_TO_READ);
                    fs2.Read(two, 0, BYTES_TO_READ);

                    if (BitConverter.ToInt64(one, 0) != BitConverter.ToInt64(two, 0))
                        return false;
                }
            }

            return true;
        }
    }
}
