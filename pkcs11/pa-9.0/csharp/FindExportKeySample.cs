using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    class FindExportKeySample : ISample
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

                    string keyValue = new string((char[])inputParams[1]);
                    string keyLabel = Convert.ToString(inputParams[2]);              
                    string wrappingKeyLabel = Convert.ToString(inputParams[3]);
                    // Login as normal user
                    uint keySize = (uint)keyValue.Length;

                    session.Login(CKU.CKU_USER, pin);

                    ObjectHandle srcKey = Helpers.FindKey(session, keyLabel);
                    if (srcKey == null)
                    {
                        srcKey = Helpers.CreateKeyObject(session, keyLabel, keyValue, keySize);
                    }

                    ObjectHandle wrappingKey = Helpers.FindKey(session, wrappingKeyLabel);
                    if (wrappingKey == null)
                    {
                        wrappingKey = Helpers.CreateKeyObject(session, wrappingKeyLabel, keyValue, keySize);
                    }

                    if ((null != srcKey) && (null != wrappingKey))
                    {
                        byte[] iv = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A,
                                    0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 };

                        Mechanism mechanism = new Mechanism(CKM.CKM_AES_CBC_PAD, iv);
                        byte[] wrappedKeyValue = session.WrapKey(mechanism, wrappingKey, srcKey);

                        Console.WriteLine("Successfully wrapped key!");
                    }
                    session.Logout();
                    slot.CloseSession(session);
                }
            }
            return true;
        }
    }
}
