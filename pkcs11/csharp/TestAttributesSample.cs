using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using System;
using System.Collections.Generic;

namespace CADP.Pkcs11Sample
{
    class TestAttributesSample : ISample
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
                    // Login as normal user
                    string pin = Convert.ToString(inputParams[0]);
                    string keyLabel = Convert.ToString(inputParams[1]);
                    bool symmetric = Convert.ToBoolean(inputParams[2]);

                    uint genAction = 0; // 0, 1, 2, or 3.  versionCreate...0, versionRotate...1, versionMigrate...2, nonVersionCreate...3
                    bool preactive = false;
                    bool bAlwSen = false;
                    bool bNevExtr = false;

                    if (inputParams.Length >= 4) preactive = Convert.ToBoolean(inputParams[3]);
                    if (inputParams.Length >= 5) bAlwSen = Convert.ToBoolean(inputParams[4]);
                    if (inputParams.Length >= 6) bNevExtr = Convert.ToBoolean(inputParams[5]);

                    uint keySize = 32;

                    session.Login(CKU.CKU_USER, pin);
                    // Generate key pair
                    IObjectHandle keyHandle = null;
                    IObjectHandle privateKeyHandle = null;

                    List<IObjectAttribute> getAttributes;

                    List<IObjectAttribute> findAttributes = new List<IObjectAttribute>();
                    findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));

                    if (symmetric == false)
                        findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_PUBLIC_KEY));
                    else
                        findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));

                    // Initialize searching
                    session.FindObjectsInit(findAttributes);

                    // Get search results
                    List<IObjectHandle> foundObjects = session.FindObjects(1);

                    // Terminate searching
                    session.FindObjectsFinal();

                    if (foundObjects != null && foundObjects.Count != 0)
                    {
                        keyHandle = foundObjects[0];
                    }
                    else if (symmetric == true)
                    {
                        // Generate symmetric key object
                        keyHandle = Helpers.GenerateKey(session, keyLabel, keySize, genAction, preactive, bAlwSen, bNevExtr);
                        if (keyHandle != null)
                        {
                            Console.WriteLine(keyLabel + " key generated!");
                        }
                        else
                        {
                            Console.WriteLine("Key: " + keyLabel + " Not generated! ");
                        }
                    }

                    if (symmetric == false)
                    {
                        if (keyHandle == null)
                            Helpers.GenerateKeyPair(session, out keyHandle, out privateKeyHandle, keyLabel);
                        else
                        {

                            findAttributes = new List<IObjectAttribute>();
                            findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_PRIVATE_KEY));
                            findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));

                            session.FindObjectsInit(findAttributes);

                            // Get search results
                            foundObjects = session.FindObjects(1);

                            // Terminate searching
                            session.FindObjectsFinal();

                            if (foundObjects != null && foundObjects.Count != 0)
                                privateKeyHandle = foundObjects[0];
                        }
                    }

                    List<CKA> attrNames = new List<CKA>();

                    if (symmetric == false)
                    {
                        attrNames.Add(CKA.CKA_LABEL);
                        attrNames.Add(CKA.CKA_CLASS);
                        attrNames.Add(CKA.CKA_KEY_TYPE);
                        attrNames.Add(CKA.CKA_MODULUS_BITS);
                        attrNames.Add(CKA.CKA_MODULUS);
                        attrNames.Add(CKA.CKA_PRIVATE_EXPONENT);
                        attrNames.Add(CKA.CKA_PUBLIC_EXPONENT);
                    }
                    else
                    {
                        attrNames.Add(CKA.CKA_LABEL);
                        attrNames.Add(CKA.CKA_CLASS);
                        attrNames.Add(CKA.CKA_KEY_TYPE);
                        attrNames.Add(CKA.CKA_END_DATE);
                        attrNames.Add(CKA.CKA_ALWAYS_SENSITIVE);
                        attrNames.Add(CKA.CKA_NEVER_EXTRACTABLE);

                        attrNames.Add(CKA.CKA_THALES_OBJECT_CREATE_DATE_EL);
                        attrNames.Add(CKA.CKA_THALES_KEY_DEACTIVATION_DATE_EL);
                    }

                    if (keyHandle != null)
                    {
                        Console.WriteLine(symmetric ? "Attributes of symmetric key:" : "Attributes of public key:");
                        getAttributes = session.GetAttributeValue(keyHandle, attrNames);
                        Helpers.PrintAttributes(getAttributes);

                        if (symmetric == true)
                        {
                            Console.WriteLine("\n\nAbout to set the end time to a new value...");
                            DateTime endTime = DateTime.UtcNow.AddDays(30);
                            List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();
                            objAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_KEY_DEACTIVATION_DATE, endTime));
                            session.SetAttributeValue(keyHandle, objAttributes);

                            Console.WriteLine(symmetric ? "\n\nAttributes of symmetric key (again):" : "\n\nAttributes of public key (again):");
                            getAttributes = session.GetAttributeValue(keyHandle, attrNames);
                            Helpers.PrintAttributes(getAttributes);
                        }
                    }

                    if (privateKeyHandle != null)
                    {
                        Console.WriteLine("Attributes of private key:");
                        getAttributes = session.GetAttributeValue(privateKeyHandle, attrNames);
                        Helpers.PrintAttributes(getAttributes);
                    }

                    session.Logout();
                }
            }
            return true;
        }


    }
}
