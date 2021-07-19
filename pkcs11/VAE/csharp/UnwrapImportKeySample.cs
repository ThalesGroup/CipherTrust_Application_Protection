using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Threading.Tasks;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    class UnwrapImportKeySample : ISample
    {
        byte[] iv = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A,
                                    0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 };

        char[] defKeyValue =  {
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
                    uint keySize = 32;                    
                    
                    string keyLabel = Convert.ToString(inputParams[1]);
                    uint keyClass = Convert.ToUInt32(inputParams[2]);

                    string wrappingKeyLabel = Convert.ToString(inputParams[3]);
                    uint wrappingKeyClass = Convert.ToUInt32(inputParams[4]);

                    uint formatType = Convert.ToUInt32(inputParams[5]);
                    string wrappedFileName = Convert.ToString(inputParams[6]);

                    uint mechType = (uint)CKM.CKM_AES_CBC_PAD;

                    FileStream fs = new FileStream(wrappedFileName, FileMode.Open, FileAccess.Read);
                    int flength = (int)fs.Length;
                    int readCnt;
                    int sumRead = 0;
                    IMechanism mechanism;

                    byte[] wrappedKey = new byte[flength];

                    while( (readCnt = fs.Read(wrappedKey, sumRead, flength-sumRead)) > 0)
                    {
                        sumRead += readCnt;
                    }
                    fs.Close();

                    // Login as normal user
                    uint wrappedKeyLen = (uint)wrappedKey.Length;

                    session.Login(CKU.CKU_USER, pin);

                    IObjectHandle srcKey = Helpers.FindKey(session, keyLabel, keyClass);
                    if (srcKey != null)
                    {
                        Console.WriteLine("Found existing key on DSM! Please use new key name.");
                        session.Logout();
                        return false;
                    }

                    IObjectHandle unwrappingKey = Helpers.FindKey(session, wrappingKeyLabel, wrappingKeyClass);
                    
                    List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();

                    if (wrappingKeyClass != (uint)CKO.CKO_SECRET_KEY && unwrappingKey != null)
                    {
                        mechType = (uint)CKM.CKM_RSA_PKCS | (uint)CKA.CKA_THALES_DEFINED;        
                    }

                    if(keyClass == (uint)CKO.CKO_SECRET_KEY)
                    {
                        // Prepare attribute template that defines search criteria
                        
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_APPLICATION, Settings.ApplicationName));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_KEY_TYPE, (uint)CKK.CKK_AES));

                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VALUE_LEN, keySize));

                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_TOKEN, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ENCRYPT, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DECRYPT, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DERIVE, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_WRAP, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_UNWRAP, true));
                        
                    }
                    else if(formatType != 0)
                    {
                        mechType |= (uint)formatType | (uint)CKA.CKA_THALES_DEFINED;

                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_APPLICATION, Settings.ApplicationName));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, keyClass));

                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_KEY_TYPE, (ulong)CKK.CKK_RSA));

                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_TOKEN, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ENCRYPT, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DECRYPT, true));                       
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_WRAP, true));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_UNWRAP, true));
                    }

                    mechanism = session.Factories.MechanismFactory.Create(mechType, iv);

                    if (wrappedKeyLen != 0) {

                        if (null == unwrappingKey)
                            unwrappingKey = session.Factories.ObjectHandleFactory.Create();
                        IObjectHandle importKey = session.UnwrapKey(mechanism, unwrappingKey, wrappedKey, objectAttributes);

                        Console.WriteLine("Successfully unwrapped and imported key into DSM!! Key handle: " + importKey.ObjectId);
                    }
                    session.Logout();
                }
            }
            return true;
        }
    }
}
