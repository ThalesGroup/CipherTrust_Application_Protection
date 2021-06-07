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

                    uint keySize = (uint)keyValue.Length;
                    DateTime endTime = DateTime.UtcNow.AddDays(31);

                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    Helpers.CleanupKey( session, keyLabel );

                    // Prepare attribute template that defines search criteria
                    List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();                    
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_APPLICATION, Settings.ApplicationName));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_KEY_TYPE, (uint)CKK.CKK_AES));

                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VALUE, keyValue));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VALUE_LEN, keySize));

                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_TOKEN, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ENCRYPT, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DECRYPT, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DERIVE, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_WRAP, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_UNWRAP, true));
                    objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_END_DATE, endTime));

                    // Generate symetric key
                    IObjectHandle createdKey = session.CreateObject(objectAttributes);
                    if (null != createdKey)
                    {
                        Console.WriteLine(keyLabel + " key created!");
                    }

                    List<IObjectAttribute> getAttributes;
                    List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();

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
