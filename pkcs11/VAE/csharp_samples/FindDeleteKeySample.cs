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
            using (IPkcs11Library pkcs11Library = Settings.Factories.Pkcs11LibraryFactory.LoadPkcs11Library(Settings.Factories, Settings.Pkcs11LibraryPath, Settings.AppType))
            {
                // Find first slot with token present
                ISlot slot = Helpers.GetUsableSlot(pkcs11Library);

                // Open RW session
                using (ISession session = slot.OpenSession(SessionType.ReadWrite))
                {
                    string pin = Convert.ToString(inputParams[0]);
                    string keyLabel = Convert.ToString(inputParams[1]);                   
                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    IObjectHandle foundKey = Helpers.FindKey(session, keyLabel);
                    
                    if (foundKey == null)
                        return false;

                    List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();
                    objAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_KEY_STATE, KeyStateDeactivated));
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
