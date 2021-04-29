using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;

namespace Vormetric.Pkcs11Sample
{
    class CreateObjectSample : ISample
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
                    string keyValue = new string((char[])inputParams[1]);
                    string keyLabel = Convert.ToString(inputParams[2]);

                    uint keySize = (uint)keyValue.Length;
                    DateTime endTime = DateTime.UtcNow.AddDays(31);

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    Helpers.CleanupKey( session, keyLabel );

                    // Prepare attribute template that defines search criteria
                    List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();                    
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_APPLICATION, Settings.ApplicationName));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_KEY_TYPE, (uint)CKK.CKK_AES));

                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_VALUE, keyValue));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_VALUE_LEN, keySize));

                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_TOKEN, true));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_ENCRYPT, true));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_DECRYPT, true));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_DERIVE, true));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_WRAP, true));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_UNWRAP, true));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_END_DATE, endTime));

                    // Generate symetric key
                    ObjectHandle createdKey = session.CreateObject(objectAttributes);
                    if (null != createdKey)
                    {
                        Console.WriteLine(keyLabel + " key created!");
                    }

                    List<ObjectAttribute> getAttributes;
                    List<ObjectAttribute> objAttributes = new List<ObjectAttribute>();

                    List<CKA> attrNames = new List<CKA>();

                    attrNames.Add(CKA.CKA_LABEL);
                    attrNames.Add(CKA.CKA_CLASS);
                    attrNames.Add(CKA.CKA_KEY_TYPE);
                    attrNames.Add(CKA.CKA_END_DATE);

                    getAttributes = session.GetAttributeValue(createdKey, attrNames);

                    Helpers.PrintAttributes(getAttributes);

                    session.Logout();           
                }
            }
            return true;
        }
    }
}
