using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    class FindDeleteKeySample: ISample
    {
        const uint KeyStateDeactivated = 3;

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

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    ObjectHandle foundKey = Helpers.FindKey(session, keyLabel);
                    if (foundKey == null)
                        return false;

                    List<ObjectAttribute> objAttributes = new List<ObjectAttribute>();
                    objAttributes.Add(new ObjectAttribute(CKA.CKA_THALES_KEY_STATE, KeyStateDeactivated));
                    session.SetAttributeValue(foundKey, objAttributes);

                    session.DestroyObject(foundKey);
                    Console.WriteLine(keyLabel + " key deleted!");
                    
                    session.Logout();
                }
            }
            return true;
        }
    }
}
