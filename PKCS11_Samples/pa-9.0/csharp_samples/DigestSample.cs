using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    public class DigestSample: ISample
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
                    Mechanism mechanism = null;
                    string opName = "sha256";

                    if (inputParams.Length >= 2)
                    {
                        opName = Convert.ToString(inputParams[1]);
                    }
                    if (opName.Equals("sha512"))
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA512);
                    }
                    else if (opName.Equals("sha384"))
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA384);
                    }
                    else
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA256);
                        opName = "sha256";
                    }
                    Console.WriteLine("Mechanism is " + opName);

                    string sourceText = "This is the default Source Text.";
                    byte[] sourceData = ConvertUtils.Utf8StringToBytes(sourceText);

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    
                    byte[] digestBytes = session.Digest(mechanism, sourceData);
                    Console.WriteLine("Digest Text: " + ConvertUtils.BytesToHexString(digestBytes));

                    session.Logout();
                    slot.CloseSession(session);
                }
            }
            return true;
        }
 

        public DigestSample()
        {
        }
    }
}
