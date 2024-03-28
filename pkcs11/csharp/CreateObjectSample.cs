using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using System;
using System.Collections.Generic;

namespace CADP.Pkcs11Sample
{
    class CreateObjectSample : ISample
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
                    string keyValue = new string((char[])inputParams[1]);
                    string keyLabel = Convert.ToString(inputParams[2]);
                    bool isOpaqueObj = inputParams.Length > 2 ? Convert.ToBoolean(inputParams[3]) : false;
                    int version = inputParams.Length > 3 ? Convert.ToInt32(inputParams[4]) : 0;
                    uint keySize = (uint)keyValue.Length;
                    DateTime endTime = DateTime.UtcNow.AddDays(31);
                    string cka_idInput = inputParams.Length > 4 ? Convert.ToString(inputParams[5]) : null;
                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    Helpers.CleanupKey(session, keyLabel, isOpaqueObj);

                    // Prepare attribute template that defines search criteria
                    List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_APPLICATION, Settings.ApplicationName));

                    if(isOpaqueObj)
                    {
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_THALES_OPAQUE_OBJECT));
                    }
                    else
                    {
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_KEY_TYPE, (uint)CKK.CKK_AES));

                    }
                    if (!isOpaqueObj && version<3)
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_VERSIONED_KEY, true));


                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VALUE, keyValue));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VALUE_LEN, keySize));

                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_TOKEN, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ENCRYPT, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DECRYPT, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DERIVE, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_WRAP, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_UNWRAP, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_END_DATE, endTime));

                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_MODIFIABLE, true));
                    // To add the CKA_ID attribute if the input is passed
                    if (!string.IsNullOrEmpty(cka_idInput))
                    {
                        objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ID, cka_idInput));
                    }

                    // Generate symetric key
                    IObjectHandle createdKey = session.CreateObject(objectAttributes);

                    if (null != createdKey)
                    {
                        Console.WriteLine(keyLabel + " key created!");
                    }
                    List<IObjectAttribute> objAttributes_exp = new List<IObjectAttribute>();
                    objAttributes_exp.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_EXTRACTABLE, true));
                    session.SetAttributeValue(createdKey, objAttributes_exp);


                    List<IObjectAttribute> getAttributes;
                    List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();

                    List<CKA> attrNames = new List<CKA>();

                    attrNames.Add(CKA.CKA_LABEL);
                    attrNames.Add(CKA.CKA_CLASS);
                    attrNames.Add(CKA.CKA_KEY_TYPE);                  

                    getAttributes = session.GetAttributeValue(createdKey, attrNames);

                    Helpers.PrintAttributes(getAttributes);


                    session.Logout();
                }
            }
            return true;
        }
    }
}
