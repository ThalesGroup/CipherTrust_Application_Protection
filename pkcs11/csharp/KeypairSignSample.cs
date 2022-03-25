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
        const uint KeyStateDeactivated = 3;

        public bool Run(object[] inputParams)
        {
            string pin          = Convert.ToString(inputParams[0]);
            string keyPairLabel = Convert.ToString(inputParams[1]);

            string opName = "RSA";
            string headermode = null;
            bool nodelete = false;
            if (inputParams.Length >= 3)
                opName       = Convert.ToString(inputParams[2]);

            if (inputParams.Length >= 4)
                headermode   = Convert.ToString(inputParams[3]);

            if (inputParams.Length >= 5)
                nodelete     = Convert.ToBoolean(inputParams[4]);

            using (IPkcs11Library pkcs11Library = Settings.Factories.Pkcs11LibraryFactory.LoadPkcs11Library(Settings.Factories, Settings.Pkcs11LibraryPath, Settings.AppType))
            {
                // Find first slot with token present
                ISlot slot = Helpers.GetUsableSlot(pkcs11Library);

                // Open RW session
                using (ISession session = slot.OpenSession(SessionType.ReadWrite))
                {
                    // Login as normal user
                    IMechanism mechanismSgn, mechanismVfy;
                    IObjectHandle publicKeyHandle;
                    IObjectHandle privateKeyHandle;
                    Net.Pkcs11Interop.Common.CKM ulHeaderSgn = 0;
                    Net.Pkcs11Interop.Common.CKM ulHeaderVfy = 0;

                    if      (headermode==null)             ulHeaderSgn = ulHeaderVfy = 0;
                    else if (headermode.Equals("v2.1"))    {ulHeaderSgn = CKM.CKM_THALES_V21HDR|CKM.CKM_VENDOR_DEFINED; ulHeaderVfy = CKM.CKM_THALES_ALLHDR|CKM.CKM_VENDOR_DEFINED;}
                    else if (headermode.Equals("v2.7"))    {ulHeaderSgn = CKM.CKM_THALES_V27HDR|CKM.CKM_VENDOR_DEFINED; ulHeaderVfy = CKM.CKM_THALES_ALLHDR|CKM.CKM_VENDOR_DEFINED;}

                    if (string.IsNullOrEmpty(opName))
                        opName = "RSA";

                    if      (opName.Equals("SHA512-HMAC")) {mechanismSgn = session.Factories.MechanismFactory.Create(ulHeaderSgn|CKM.CKM_SHA512_HMAC); mechanismVfy = session.Factories.MechanismFactory.Create(ulHeaderVfy|CKM.CKM_SHA512_HMAC);}
                    else if (opName.Equals("SHA384-HMAC")) {mechanismSgn = session.Factories.MechanismFactory.Create(ulHeaderSgn|CKM.CKM_SHA384_HMAC); mechanismVfy = session.Factories.MechanismFactory.Create(ulHeaderVfy|CKM.CKM_SHA384_HMAC);}
                    else if (opName.Equals("SHA256-HMAC")) {mechanismSgn = session.Factories.MechanismFactory.Create(ulHeaderSgn|CKM.CKM_SHA256_HMAC); mechanismVfy = session.Factories.MechanismFactory.Create(ulHeaderVfy|CKM.CKM_SHA256_HMAC);}
                    else if (opName.Equals("SHA224-HMAC")) {mechanismSgn = session.Factories.MechanismFactory.Create(ulHeaderSgn|CKM.CKM_SHA224_HMAC); mechanismVfy = session.Factories.MechanismFactory.Create(ulHeaderVfy|CKM.CKM_SHA224_HMAC);}
                    else if (opName.Equals("SHA1-HMAC"))   {mechanismSgn = session.Factories.MechanismFactory.Create(ulHeaderSgn|CKM.CKM_SHA_1_HMAC);  mechanismVfy = session.Factories.MechanismFactory.Create(ulHeaderVfy|CKM.CKM_SHA_1_HMAC); }
                    else if (opName.Equals("RSA"))         mechanismSgn = mechanismVfy = session.Factories.MechanismFactory.Create(CKM.CKM_RSA_PKCS);
                    else {
                        Console.WriteLine("Only SHA512-HMAC, SHA384-HMAC, SHA256-HMAC, SHA224-HMAC, SHA1-HMAC, and RSA are supported"); 
                        return false;
                    }

		            session.Login(CKU.CKU_USER, pin);

                    try
                    {
                        if (opName.Equals("RSA"))
                        {
                            if (!string.IsNullOrEmpty(headermode))
                                return false;

                            publicKeyHandle = Helpers.FindKey(session, keyPairLabel, (uint)CKO.CKO_PUBLIC_KEY);
                            privateKeyHandle = Helpers.FindKey(session, keyPairLabel, (uint)CKO.CKO_PRIVATE_KEY);
                            if (publicKeyHandle != null)
                            {
                                Console.WriteLine(keyPairLabel + " public key found! Key handle: "+ publicKeyHandle.ObjectId);
                                Console.WriteLine(keyPairLabel + " private key found! Key handle: " + privateKeyHandle.ObjectId);
                            }
                            else
                            {
                                // Generate key pair
                                Helpers.GenerateKeyPair(session, out publicKeyHandle, out privateKeyHandle, keyPairLabel); // password has been removed
                                Console.WriteLine("Asymmetric key " + keyPairLabel + " generated!");
                            }
                        }
                        else
                        {
                            publicKeyHandle = privateKeyHandle = Helpers.FindKey(session, keyPairLabel);
                            if (publicKeyHandle != null)
                                Console.WriteLine(keyPairLabel + " key found!");
                            else
                            {
                                // generate a symmetric key, assign it to both publicKeyHandle and privateKeyHandle
                                uint keySize = 32; // 32-byte AES key
                                publicKeyHandle = privateKeyHandle = Helpers.GenerateKey(session, keyPairLabel, keySize);
                                if (null != publicKeyHandle)
                                {
                                    Console.WriteLine("Symmetric key " + keyPairLabel + " generated!");
                                }
                                else
                                {
                                    Console.WriteLine("Failed to generate " + keyPairLabel + " !");
                                    return false;
                                }
                            }
                        }

                        if ((null != publicKeyHandle) && (null != privateKeyHandle) /*&& !opName.Equals("RSA")*/)
                        {
                            string message = "This is the message which will be signed.";
                            byte[] signature = session.Sign(mechanismSgn, privateKeyHandle, Encoding.UTF8.GetBytes(message));
                            Console.WriteLine("Message has been signed.");
                            bool isSigValid = false;
                            session.Verify(mechanismVfy, publicKeyHandle, Encoding.UTF8.GetBytes(message), signature, out isSigValid);
                            if (isSigValid)
                                Console.WriteLine("Signature is valid.");
                            else
                                Console.WriteLine("Signature is NOT valid!");
                        }
                        
                        if (publicKeyHandle == privateKeyHandle)
                        {
                            List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();
                            objAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_KEY_STATE, KeyStateDeactivated));
                            session.SetAttributeValue(publicKeyHandle, objAttributes);
                        }

                        //delete the key[pair] so that the sample can be re-run
                        if (nodelete == false)
                        {
                            session.DestroyObject(publicKeyHandle);
                            Console.WriteLine("KeyPair "+ keyPairLabel + " has been deleted from DSM.");
                        }                        
                        session.Logout();
                    }
                    catch (Pkcs11Exception pke) {
                        Console.WriteLine(pke.Message);
                    }
                }
            }
            return true;
        }
    }
}
