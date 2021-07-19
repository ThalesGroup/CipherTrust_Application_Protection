using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    class CreateKeySample: ISample
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
                    uint keySize = 32;
                    string pin = Convert.ToString(inputParams[0]);
                    string keyLabel = Convert.ToString(inputParams[1]);

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    Helpers.CleanupKey(session, keyLabel);

                    // Generate symetric key
                    ObjectHandle generatedKey = Helpers.GenerateKey(session, keyLabel, keySize);
                    if (null != generatedKey)
                    {
                        Console.WriteLine(keyLabel + " key generated!");
                    }
                    session.Logout();

                    slot.CloseSession(session);
                }
            }
            return true;
        }
    }
}
