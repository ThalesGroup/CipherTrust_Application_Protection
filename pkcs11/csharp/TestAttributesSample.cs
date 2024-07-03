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
                    string cka_idInput = null;
                    int numberOfHandle = 1;

                    string asymmetricAlgoName = null;
                    string curveOid = null;

                    if (inputParams.Length >= 4) preactive = Convert.ToBoolean(inputParams[3]);
                    if (inputParams.Length >= 5) bAlwSen = Convert.ToBoolean(inputParams[4]);
                    if (inputParams.Length >= 6) bNevExtr = Convert.ToBoolean(inputParams[5]);
                    if (inputParams.Length >= 7 && inputParams[6] != null) asymmetricAlgoName = inputParams[6].ToString();

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

                    // Get search results
                    List<IObjectHandle> privateKeyHandles = new List<IObjectHandle>();

                    // Terminate searching
                    session.FindObjectsFinal();

                    if (foundObjects != null && foundObjects.Count != 0)
                    {
                        keyHandle = foundObjects[0];
                    }
                    else if (symmetric)
                    {
                        // Generate symmetric key object
                        keyHandle = Helpers.GenerateKey(session, keyLabel, keySize, genAction, preactive, bAlwSen, bNevExtr);
                        if (keyHandle != null)
                        {
                            Console.WriteLine(keyLabel + " key generated!");
                            foundObjects.Add(keyHandle);
                        }
                        else
                        {
                            Console.WriteLine("Key: " + keyLabel + " Not generated! ");
                        }
                        
                    }

                    if (!symmetric)
                    {
                        if (keyHandle == null)
                        {
                            if (asymmetricAlgoName == "EC")
                            { curveOid = "06052b81040020"; }

                            Helpers.GenerateKeyPair(session, out keyHandle, out privateKeyHandle, keyLabel, cka_idInput, curveOid);
                            foundObjects.Add(keyHandle);
                            privateKeyHandles.Add(privateKeyHandle);
                        }
                        else
                        {

                            findAttributes = new List<IObjectAttribute>();
                            findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_PRIVATE_KEY));

                            findAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));

                            session.FindObjectsInit(findAttributes);

                            // Get search results
                            privateKeyHandles = session.FindObjects(numberOfHandle);

                            // Terminate searching
                            session.FindObjectsFinal();

                            if (privateKeyHandles != null && privateKeyHandles.Count != 0)
                                privateKeyHandle = privateKeyHandles[0];
                        }
                    }

                    List<CKA> attrNames = new List<CKA>();

                    if (!symmetric)
                    {
                        attrNames.Add(CKA.CKA_LABEL);
                        attrNames.Add(CKA.CKA_CLASS);
                        attrNames.Add(CKA.CKA_KEY_TYPE);
                        attrNames.Add(CKA.CKA_ID);
                        attrNames.Add(CKA.CKA_MODULUS_BITS);
                        if (asymmetricAlgoName == "EC")
                        { attrNames.Add(CKA.CKA_EC_PARAMS); }
                        else
                        {
                            attrNames.Add(CKA.CKA_MODULUS);
                            attrNames.Add(CKA.CKA_PUBLIC_EXPONENT);
                        }
                    }
                    else
                    {
                        attrNames.Add(CKA.CKA_LABEL);
                        attrNames.Add(CKA.CKA_CLASS);
                        attrNames.Add(CKA.CKA_KEY_TYPE);
                        attrNames.Add(CKA.CKA_END_DATE);
                        attrNames.Add(CKA.CKA_THALES_OBJECT_CREATE_DATE_EL);
                        attrNames.Add(CKA.CKA_ID);
                    }

                    bool if_CKA_APP_add = false;

                    foreach (var foundObject in foundObjects)
                    {
                        Console.WriteLine(symmetric ? "Attributes of symmetric key:" : "Attributes of public key:");
                        getAttributes = session.GetAttributeValue(foundObject, attrNames);
                        Helpers.PrintAttributes(getAttributes);

                        Console.WriteLine("\n\nAbout to add ApplicationName attribute with value as {0}...", Settings.ApplicationName);
                        if (!if_CKA_APP_add)
                        {
                            attrNames.Add(CKA.CKA_APPLICATION);
                            if_CKA_APP_add = true;
                        }

                        List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();
                        objAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_APPLICATION, Settings.ApplicationName));
                        session.SetAttributeValue(foundObject, objAttributes);


                        Console.WriteLine(symmetric ? "\n\nAttributes of symmetric key (again):" : "\n\nAttributes of public key (again):");
                        getAttributes = session.GetAttributeValue(foundObject, attrNames);
                        Helpers.PrintAttributes(getAttributes);


                        Console.WriteLine("------------------");
                    }

                    foreach (var privateHandle in privateKeyHandles)
                    {
                        if (asymmetricAlgoName != "EC")
                        {
                            attrNames.Remove(CKA.CKA_PUBLIC_EXPONENT);
                            attrNames.Add(CKA.CKA_PRIVATE_EXPONENT);
                        }

                        Console.WriteLine("Attributes of private key:");
                        getAttributes = session.GetAttributeValue(privateHandle, attrNames);
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
