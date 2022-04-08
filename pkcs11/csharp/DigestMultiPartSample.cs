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
                    else if (opName.Equals("sha1"))
                    {
                        mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_SHA_1);
                    }
                    else if (opName.Equals("md5"))
                    {
                        mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_MD5);
                    }
                    else
                    {
                        mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_SHA256);
                        opName = "sha256";
                    }
                    Console.WriteLine("Mechanism is " + opName);

                    if (String.IsNullOrEmpty(pathSource))
                    {
                        pathSource = "FileInput.txt";
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

       
    }
}
