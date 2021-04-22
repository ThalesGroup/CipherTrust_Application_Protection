using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    class KeypairSignSample : ISample
    {
        string keyPairLabel = "vpkcs11_dotnet_sample_keypair";        

        public bool Run(object[] inputParams)
        {
            using (Pkcs11 pkcs11 = new Pkcs11(Settings.Pkcs11LibraryPath, false))
            {
                // Find first slot with token present
                Slot slot = Helpers.GetUsableSlot(pkcs11);

                // Open RW session
                using (Session session = slot.OpenSession(false))
                {
                    // Login as normal user
                    string pin = Convert.ToString(inputParams[0]);                    
                    session.Login(CKU.CKU_USER, pin);

                    // Generate key pair
                    ObjectHandle publicKeyHandle;
                    ObjectHandle privateKeyHandle;
                    Helpers.GenerateKeyPair(session, out publicKeyHandle, out privateKeyHandle, keyPairLabel);
                    if ((null != publicKeyHandle) && (null != privateKeyHandle))
                    {
                        string message = "Message to be signed.";
                        Mechanism mechanism = new Mechanism(CKM.CKM_RSA_PKCS);
                        byte[] signature = session.Sign(mechanism, privateKeyHandle, Encoding.UTF8.GetBytes(message));
                        Console.WriteLine("Message has been signed.");
                        bool isSigValid = false;
                        session.Verify(mechanism, publicKeyHandle, Encoding.UTF8.GetBytes(message), signature, out isSigValid);
                        if (isSigValid)
                            Console.WriteLine("Signature is valid.");
                        else
                            Console.WriteLine("Signature is NOT valid!");


                        //delete the keypair so that the sample can be re-run
                        session.DestroyObject(publicKeyHandle);
                    }
                    session.Logout();
                    slot.CloseSession(session);
                }
            }
            return true;
        }
    }
}
