using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    class TestAttributesSample : ISample
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
                    // Login as normal user
                    string pin = Convert.ToString(inputParams[0]);
                    string keyLabel = Convert.ToString(inputParams[1]);                    
                    bool symmetric = Convert.ToBoolean(inputParams[2]);
                    uint keySize = 32;

                    session.Login(CKU.CKU_USER, pin);
                    // Generate key pair
                    ObjectHandle keyHandle = null;
                    ObjectHandle privateKeyHandle = null;                   

                    List<ObjectAttribute> getAttributes;

                    List<ObjectAttribute> findAttributes = new List<ObjectAttribute>();
                    
                    findAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));

                    if(symmetric == false)
                        findAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_PUBLIC_KEY));
                    else
                        findAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));

                    // Initialize searching
                    session.FindObjectsInit(findAttributes);

                    // Get search results
                    List<ObjectHandle> foundObjects = session.FindObjects(1);

                    // Terminate searching
                    session.FindObjectsFinal();

                    if (foundObjects != null && foundObjects.Count != 0)
                        keyHandle = foundObjects[0];
                    else if (symmetric == true)
                    { 
                        // Generate symmetric key object
                        keyHandle = Helpers.GenerateKey(session, keyLabel, keySize);
                        if (keyHandle != null)
                        {
                            Console.WriteLine(keyLabel + " key generated!");
                        }
                        else {
                            Console.WriteLine("Key: " + keyLabel +" Not generated! ");
                        }
                    }
                    else if (!String.IsNullOrEmpty(keyLabel))
                    {
                        findAttributes = new List<ObjectAttribute>();
                        findAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_PRIVATE_KEY));
                        findAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));

                        // Initialize searching
                        session.FindObjectsInit(findAttributes);

                        // Get search results
                        foundObjects = session.FindObjects(1);

                        // Terminate searching
                        session.FindObjectsFinal();

                        if (foundObjects != null && foundObjects.Count != 0)
                            privateKeyHandle = foundObjects[0];
                    }

                    if(keyHandle == null && privateKeyHandle == null && symmetric == false)
                        Helpers.GenerateKeyPair(session, out keyHandle, out privateKeyHandle, keyLabel);

                    List<CKA> attrNames = new List<CKA>();

                    if (symmetric == false)
                    {
                        attrNames.Add(CKA.CKA_LABEL);
                        attrNames.Add(CKA.CKA_KEY_TYPE);
                        attrNames.Add(CKA.CKA_MODULUS_BITS);
                        attrNames.Add(CKA.CKA_MODULUS);
                        attrNames.Add(CKA.CKA_PRIVATE_EXPONENT);
                        attrNames.Add(CKA.CKA_PUBLIC_EXPONENT);
                    }
                    else {
                        attrNames.Add(CKA.CKA_LABEL);
                        attrNames.Add(CKA.CKA_CLASS);
                        attrNames.Add(CKA.CKA_KEY_TYPE);
                        attrNames.Add(CKA.CKA_END_DATE);
                    }

                    if (keyHandle != null)
                    {
                        getAttributes = session.GetAttributeValue(keyHandle, attrNames);
                        Helpers.PrintAttributes(getAttributes);
                       
                        DateTime endTime = DateTime.UtcNow.AddDays(15);

                        List<ObjectAttribute> objAttributes = new List<ObjectAttribute>();
                        objAttributes.Add(new ObjectAttribute(CKA.CKA_END_DATE, endTime));

                        session.SetAttributeValue(keyHandle, objAttributes);

                        getAttributes = session.GetAttributeValue(keyHandle, attrNames);
                        Helpers.PrintAttributes(getAttributes);
                    }

                    if (privateKeyHandle != null)
                    {
                        getAttributes = session.GetAttributeValue(privateKeyHandle, attrNames);
                        Helpers.PrintAttributes(getAttributes);
                    }                    

                    session.Logout();
                    slot.CloseSession(session);
                }
            }
            return true;
        }

        
    }
}
