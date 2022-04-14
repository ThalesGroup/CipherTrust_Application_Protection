using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using System;
using System.IO;

namespace CADP.Pkcs11Sample
{
    class FindExportKeySample : ISample
    {
        byte[] iv = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A,
                                    0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 };

        string defWrappedFilename = "wrapped-key.dat";

        char[] keyValue =  {
                 't','h','i','s',' ','i','s',' ',
                    'm','y',' ','s','a','m','p','l',
                 'e',' ','k','e','y',' ','d','a',
                    't','a',' ','5','4','3','2','1' };
        public bool Run(object[] inputParams)
        {
            using (IPkcs11Library pkcs11Library = Settings.Factories.Pkcs11LibraryFactory.LoadPkcs11Library(Settings.Factories, Settings.Pkcs11LibraryPath, Settings.AppType))
            {
                // Find first slot with token present
                ISlot slot = Helpers.GetUsableSlot(pkcs11Library);

                // Open RW session
                using (ISession session = slot.OpenSession(SessionType.ReadWrite))
                {
                    string pin = Convert.ToString(inputParams[0]);

                    string keyLabel = Convert.ToString(inputParams[1]);
                    uint keyType = Convert.ToUInt32(inputParams[2]);

                    string wrappingKeyLabel = Convert.ToString(inputParams[3]);
                    uint wrappingKeyType = Convert.ToUInt32(inputParams[4]);
                    uint formatType = Convert.ToUInt32(inputParams[5]);

                    String wrappedFileName = Convert.ToString(inputParams[6]);
                    Boolean genWrappingKey = Convert.ToBoolean(inputParams[7]);

                    byte[] wrappedKeyValue = null;

                    if (string.IsNullOrEmpty(wrappedFileName))
                    {
                        wrappedFileName = defWrappedFilename;
                    }

                    if (string.IsNullOrEmpty(wrappingKeyLabel) && genWrappingKey)
                    {
                        wrappingKeyLabel = "vpkcs11_dotnet_wrapping_key";
                    }

                    // Login as normal user
                    uint keySize = (uint)keyValue.Length;
                    uint genAction = 3;
                    uint mechType = (uint)CKM.CKM_AES_CBC_PAD;
                    IMechanism mechanism;

                    session.Login(CKU.CKU_USER, pin);

                    IObjectHandle srcKey = Helpers.FindKey(session, keyLabel, keyType);
                    if (srcKey == null && keyType == (uint)CKO.CKO_SECRET_KEY)
                    {
                        srcKey = Helpers.CreateKeyObject(session, keyLabel, new string(keyValue), keySize);
                    }

                    IObjectHandle wrappingKey = Helpers.FindKey(session, wrappingKeyLabel, wrappingKeyType);
                    if (wrappingKey == null)
                    {
                        if (genWrappingKey == true)
                            wrappingKey = Helpers.GenerateKey(session, wrappingKeyLabel, keySize, genAction);
                        else
                        {
                            Console.WriteLine("Use no wrapping key!");
                            wrappingKey = session.Factories.ObjectHandleFactory.Create();
                        }
                    }

                    if (wrappingKeyType != (uint)CKO.CKO_SECRET_KEY && wrappingKey != null)
                    {
                        mechType = (uint)CKM.CKM_RSA_PKCS | (uint)CKA.CKA_THALES_DEFINED;
                    }
                    else if (formatType != 0)
                    {
                        mechType |= (uint)formatType | (uint)CKA.CKA_THALES_DEFINED;
                    }

                    mechanism = session.Factories.MechanismFactory.Create(mechType, iv);

                    if (srcKey != null)
                    {
                        wrappedKeyValue = session.WrapKey(mechanism, wrappingKey, srcKey);

                        if (wrappingKey.ObjectId != 0)
                        {
                            Console.WriteLine("Successfully wrapped key " + keyLabel + " !! ");
                        }
                        else
                            Console.WriteLine("Successfully exported key " + keyLabel + " !!");
                    }
                    else
                    {
                        Console.WriteLine("Key handle doesn't exist; or no wrapping key: " + keyLabel + " !! ");
                    }

                    if (null != wrappedKeyValue)
                    {
                        FileStream fs = new FileStream(wrappedFileName, FileMode.Create, FileAccess.Write);
                        fs.Write(wrappedKeyValue, 0, wrappedKeyValue.Length);
                        fs.Close();
                    }
                    session.Logout();
                }
            }
            return true;
        }
    }
}
