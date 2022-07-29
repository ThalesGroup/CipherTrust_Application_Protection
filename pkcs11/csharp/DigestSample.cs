using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using System;

namespace CADP.Pkcs11Sample
{
    public class DigestSample : ISample
    {
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
                    IMechanism mechanism = null;
                    string opName = "sha256";

                    if (inputParams.Length >= 2)
                    {
                        opName = Convert.ToString(inputParams[1]);
                    }
                    if (opName.Equals("sha512"))
                    {
                        mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_SHA512);
                    }
                    else if (opName.Equals("sha384"))
                    {
                        mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_SHA384);
                    }
                    else if (opName.Equals("sha224"))
                    {
                        mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_SHA224);
                    }
                    
                    else if (opName.Equals("sha256"))
                    {
                        mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_SHA256);
                        opName = "sha256";
                    }
                    else
                    {
                        Console.WriteLine("Only sha224/256/384/512 allowed. This input is case sensitive. hmac not supported in C#.");
                        return false;
                    }

                    Console.WriteLine("Mechanism is " + opName);

                    string sourceText = "This is the default Source Text.";
                    byte[] sourceData = ConvertUtils.Utf8StringToBytes(sourceText);

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    byte[] digestBytes = session.Digest(mechanism, sourceData);
                    Console.WriteLine("Digest Text: " + ConvertUtils.BytesToHexString(digestBytes));

                    session.Logout();
                }
            }
            return true;
        }

        public DigestSample()
        {
        }
    }
}
