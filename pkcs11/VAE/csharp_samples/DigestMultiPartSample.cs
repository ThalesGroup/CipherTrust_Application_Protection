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
    public class DigestMultiPartSample: ISample
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
                    string pathSource = null;

                    if (inputParams.Length >= 2)
                    {
                        opName = Convert.ToString(inputParams[1]);
                    }

                    if (inputParams.Length >= 3)
                    {
                        pathSource = Convert.ToString(inputParams[2]);
                    }

                    if (opName.Equals("sha512"))
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA512);
                    }
                    else if (opName.Equals("sha384"))
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA384);
                    }
                    else if (opName.Equals("sha224"))
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA224);
                    }
                    else if (opName.Equals("sha1"))
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA_1);
                    }
                    else if (opName.Equals("md5"))
                    {
                        mechanism = new Mechanism(CKM.CKM_MD5);
                    }
                    else
                    {
                        mechanism = new Mechanism(CKM.CKM_SHA256);
                        opName = "sha256";
                    }
                    Console.WriteLine("Mechanism is " + opName);

                    if (String.IsNullOrEmpty(pathSource))
                    {
                        pathSource = Settings.Pkcs11LibraryPath;
                    }
                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    using (FileStream sourceFileStream = new FileStream(pathSource, FileMode.Open, FileAccess.Read))
                    {
                        byte[] digestBytes = session.Digest(mechanism, sourceFileStream);
                        Console.WriteLine("Digest Text: " + ConvertUtils.BytesToHexString(digestBytes));
                    }

                    session.Logout();                 
                }
            }
            return true;
        }

        public DigestMultiPartSample()
        {
        }
    }
}
