using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using System;
using System.Collections.Generic;
using System.Linq;

namespace CADP.Pkcs11Sample
{
    class FindKeysByCkaSample : ISample
    {
        //  Pre-requisites: keys should be created on CM
        //  Find keys using CKA_KeyType and print attributes sample

        public int max_keys = 50;
        public const int cka_id_handle_max_keys = 1000;
        public bool Run(object[] inputParams)
        {
            using (IPkcs11Library pkcs11Library = Settings.Factories.Pkcs11LibraryFactory.LoadPkcs11Library(Settings.Factories, Settings.Pkcs11LibraryPath, Settings.AppType))
            {
                // Find first slot with token present
                ISlot slot = Helpers.GetUsableSlot(pkcs11Library);
                

                using (ISession session = slot.OpenSession(SessionType.ReadWrite))
                { 
                    string pin = Convert.ToString(inputParams[0]);
                    string keyType = Convert.ToString(inputParams[1]).ToUpper().Trim();
                    string cka_idInput = null;
                    if (inputParams.Length > 2 && inputParams[2] != null)
                    {
                        cka_idInput = Convert.ToString(inputParams[2]);
                    }

                    CKK cka_keyType;

                    switch (keyType)
                    {
                        case "AES":
                            cka_keyType = CKK.CKK_AES;
                            
                            break;
                        case "RSA":
                            cka_keyType = CKK.CKK_RSA;
                            break;
                        case "EC":
                            cka_keyType = CKK.CKK_EC;
                            break;
                        case "SHA1-HMAC":
                            cka_keyType = CKK.CKK_SHA_1_HMAC;
                            break;
                        case "SHA224-HMAC":
                            cka_keyType = CKK.CKK_SHA224_HMAC;
                            break;
                        case "SHA256-HMAC":
                            cka_keyType = CKK.CKK_SHA256_HMAC;
                            break;
                        case "SHA384-HMAC":
                            cka_keyType = CKK.CKK_SHA384_HMAC;
                            break;
                        case "SHA512-HMAC":
                            cka_keyType = CKK.CKK_SHA512_HMAC;
                            break;
                        default:
                            Console.WriteLine("Invalid key type provided...");
                            return false;
                    }

                   
                    
                    session.Login(CKU.CKU_USER, pin);
                    var symmetricList =  new[] { CKK.CKK_AES, CKK.CKK_SHA_1_HMAC, CKK.CKK_SHA224_HMAC, CKK.CKK_SHA256_HMAC, CKK.CKK_SHA384_HMAC, CKK.CKK_SHA512_HMAC };

                    List<IObjectAttribute> getAttributes;

                    List<IObjectAttribute> findAttributes = new List<IObjectAttribute>();

                    // Add the CKA_ID attribute if the cka id input has value.
                    if (!string.IsNullOrEmpty(cka_idInput))
                    {
                        findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ID, cka_idInput));
                        max_keys = cka_id_handle_max_keys;
                    }
                    else
                    {
                        findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_KEY_TYPE, cka_keyType));
                    }

                    // Initialize searching
                    session.FindObjectsInit(findAttributes);

                    List<IObjectHandle> foundObjects = session.FindObjects(max_keys);


                    // Terminate searching
                    session.FindObjectsFinal();

                    if (foundObjects == null || foundObjects.Count == 0)
                    {
                        Console.WriteLine("No key matching the provided attribute. Please create key first");
                        return false;
                    }

                    Console.WriteLine("Fetched {0} keys", foundObjects.Count.ToString());
                    List<CKA> attrNames = new List<CKA>
                    {
                        CKA.CKA_LABEL,
                        CKA.CKA_CLASS,
                        CKA.CKA_KEY_TYPE,
                        CKA.CKA_ID
                    };

                    if (!symmetricList.Contains(cka_keyType))
                    {
                        attrNames.Add(CKA.CKA_MODULUS_BITS);
                        if (cka_keyType == CKK.CKK_EC)
                        { attrNames.Add(CKA.CKA_EC_PARAMS); }
                        else
                        {
                            attrNames.Add(CKA.CKA_MODULUS);
                            attrNames.Add(CKA.CKA_PUBLIC_EXPONENT);
                            attrNames.Add(CKA.CKA_PRIVATE_EXPONENT);
                        }
                    }
                    else
                    {
                        attrNames.Add(CKA.CKA_END_DATE);
                        attrNames.Add(CKA.CKA_THALES_OBJECT_CREATE_DATE_EL);
                    }


                    foreach (var foundObject in foundObjects)
                    {
                        
                        Console.WriteLine("Attributes of key:");
                        getAttributes = session.GetAttributeValue(foundObject, attrNames);
                        Helpers.PrintAttributes(getAttributes);

                        Console.WriteLine("------------------");
                    }

                    session.Logout();
                }
            }
            return true;
        }


    }
}
