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
                    bool needMetaData = Convert.ToBoolean(inputParams[3]); // expects 'true' or 'false'
                    string headerMode = Convert.ToString(inputParams[4]);

                    if(String.IsNullOrEmpty(pathSource))
                        pathSource = Settings.Pkcs11LibraryPath;

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);
                      
                    ObjectHandle foundKey = Helpers.FindKey(session, keyLabel);
                    if (foundKey == null) {
                        uint keySize = 32;
                        foundKey = Helpers.GenerateKey(session, keyLabel, keySize);
                    }
                        

                    byte[] iv = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 };

                    // Specify encryption mechanism with initialization vector as parameter
                    Mechanism encmechanism;
                    Mechanism decmechanism;
                    if (headerMode == null || headerMode.Length < 4) headerMode = "none";
                    switch (headerMode[3])
                    {
                        case '5': encmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD | CKM.CKM_THALES_V15HDR | CKM.CKM_VENDOR_DEFINED, iv); 
                                  decmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD | CKM.CKM_THALES_ALLHDR | CKM.CKM_VENDOR_DEFINED, iv); 
                                  break;
                        case '1': encmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD | CKM.CKM_THALES_V21HDR | CKM.CKM_VENDOR_DEFINED, iv);
                                  decmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD | CKM.CKM_THALES_ALLHDR | CKM.CKM_VENDOR_DEFINED, iv); 
                                  break;
                        case '7': encmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD | CKM.CKM_THALES_V27HDR | CKM.CKM_VENDOR_DEFINED, iv);
                                  decmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD | CKM.CKM_THALES_ALLHDR | CKM.CKM_VENDOR_DEFINED, iv); 
                                  break;
                        case 'e': // last letter of 'none'
                        default:  encmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD, iv); 
                                  decmechanism = new Mechanism(CKM.CKM_AES_CBC_PAD, iv); 
                                  break;
                    }
                    
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
                            session.Encrypt(encmechanism, foundKey, sourceFileStream, cipherSourceStream, metaData);
                        else
                            session.Encrypt(encmechanism, foundKey, sourceFileStream, cipherSourceStream);
                    }
  
                    
                    using (FileStream decipherSourceStream = new FileStream(pathDeCipherSource, FileMode.Create, FileAccess.Write),
                    cipherSourceFileStream = new FileStream(pathCipherSource, FileMode.Open, FileAccess.Read))
                    {
                        Console.WriteLine("Decrypted File: " + pathCipherSource + " into " + pathDeCipherSource);
                        if ( needMetaData )
                            session.Decrypt(decmechanism, foundKey, cipherSourceFileStream, decipherSourceStream, metaData);
                        else
                            session.Decrypt(decmechanism, foundKey, cipherSourceFileStream, decipherSourceStream);
                    }
                    
                    // now do file comparison 
                    Console.WriteLine("Comparing source file and decrypted source file...: " );

                    // Do something interesting with decrypted data
                    if (FilesAreEqual(new FileInfo(pathSource), new FileInfo(pathDeCipherSource)))
                    {
                        Console.WriteLine("Source and Decrypted Data Matches!");
                    }
                    session.Logout();                    
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
