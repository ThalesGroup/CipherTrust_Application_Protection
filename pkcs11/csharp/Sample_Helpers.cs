/*
 *  Pkcs11Interop - Open-source .NET wrapper for unmanaged PKCS#11 libraries
 *  Copyright (c) 2012-2013 JWC s.r.o.
 *  Author: Jaroslav Imrich
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License version 3
 *  as published by the Free Software Foundation.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program. If not, see <http://www.gnu.org/licenses/>.
 * 
 *  You can be released from the requirements of the license by purchasing
 *  a commercial license. Buying such a license is mandatory as soon as you
 *  develop commercial activities involving the Pkcs11Interop software without
 *  disclosing the source code of your own applications.
 * 
 *  For more information, please contact JWC s.r.o. at info@pkcs11interop.net
 */

using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using System;
//using Net.Pkcs11Interop.LowLevelAPI;
using System.Collections.Generic;
using System.Text;

namespace CADP.Pkcs11Sample
{
    /// <summary>
    /// Helper methods for HighLevelAPI tests.
    /// </summary>
    public class Helpers
    {
        /// <summary>
        /// Finds first slot with token present
        /// </summary>
        /// <param name='pkcs11'>Initialized PKCS11 wrapper</param>
        /// <returns>First slot with token present</returns>
        public static ISlot GetUsableSlot(IPkcs11Library pkcs11Library)
        {
            // Get list of available slots
            List<ISlot> slots = pkcs11Library.GetSlotList(SlotsType.WithOrWithoutTokenPresent);

            if ((null != slots) && (slots.Count > 0))
                // Let's use first slot with token present
                return slots[0];
            else
                return null;
        }

        public static string ParseKeyClass(string keyLabel, ref uint keyClass)
        {
            if (keyLabel.IndexOf(':') == -1 || keyLabel[1] != ':')
            {
                keyClass = (uint)CKO.CKO_SECRET_KEY;
                return keyLabel;
            }
            else
            {
                switch (keyLabel[0])
                {
                    case 's':
                        keyClass = (uint)CKO.CKO_SECRET_KEY;
                        break;
                    case 'c':
                        keyClass = (uint)CKO.CKO_PUBLIC_KEY;
                        break;
                    case 'v':
                        keyClass = (uint)CKO.CKO_PRIVATE_KEY;
                        break;

                    default:
                        return null;
                }
            }
            return keyLabel.Substring(2);
        }

        public static uint ParseFormatType(string sel)
        {
            uint formatType = 0;
            if (string.IsNullOrEmpty(sel))
            {
                Console.WriteLine("Invalid format type.");
                return 0;
            }

            if (StringComparer.OrdinalIgnoreCase.Equals(sel, "pem") == true)
                formatType = (uint)CKA.CKA_THALES_PEM_FORMAT;

            return formatType;
        }

        public static IObjectHandle FindKey(ISession session, string keyLabel)
        {
            IObjectHandle key = null;
            List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_CACHE_CLEAR, true));

            // Initialize searching
            session.FindObjectsInit(objectAttributes);
            // Get search results
            List<IObjectHandle> foundObjects = session.FindObjects(1);

            // Terminate searching
            session.FindObjectsFinal();

            foreach (IObjectHandle handle in foundObjects)
            {
                Console.WriteLine("Found key with label: " + keyLabel + "!");
                return handle;
            }

            return key;
        }

        public static IObjectHandle FindKey(ISession session, string keyLabel, uint keyType)
        {
            IObjectHandle key = null;
            List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, keyType));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));
			
			//The RSA keys handle which is retrieved in first findkey (privatekeyhandle) is internally saved by pcks11 in map and 
			//when again findkey (publickeyhandle) is applied on it these values get overrides.
			//So commenting below code which was added a special case for one specific customer.
            //objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_CACHE_CLEAR, true));

            // Initialize searching
            session.FindObjectsInit(objectAttributes);

            // Get search results
            List<IObjectHandle> foundObjects = session.FindObjects(1);

            // Terminate searching
            session.FindObjectsFinal();

            foreach (IObjectHandle handle in foundObjects)
            {
                Console.WriteLine("Found key with label: " + keyLabel + "!");
                return handle;
            }

            return key;
        }

        public static IObjectHandle CreateKeyObject(ISession session, string keyLabel, string keyValue, uint keySize)
        {
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
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_MODIFIABLE, true));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_EXTRACTABLE, true));

            // Import symetric key object          

            IObjectHandle key = session.CreateObject(objectAttributes);
            if (null != key)
            {
                Console.WriteLine(keyLabel + " key created!");
            }
            return key;
        }

        public static void CleanupKey(ISession session, string keyLabel, bool isOpaqueObj =false)
        {

            List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();

            if (isOpaqueObj)
            {
                objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_THALES_OPAQUE_OBJECT));
            }
            else
            {
                objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
               
            }
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));

            // Initialize searching
            session.FindObjectsInit(objectAttributes);

            // Get search results
            List<IObjectHandle> foundObjects = session.FindObjects(2);

            // Terminate searching
            session.FindObjectsFinal();

            foreach (IObjectHandle handle in foundObjects)
            {
                if (!isOpaqueObj)
                {
                const uint KeyStateDeactivated = 3;
                List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();
                objAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_KEY_STATE, KeyStateDeactivated));
                session.SetAttributeValue(handle, objAttributes);
                }
                session.DestroyObject(handle);
                Console.WriteLine("Existing " + keyLabel + " key deleted!");
            }
        }

        /// <summary>
        /// Generates symmetric key.
        /// </summary>
        /// <param name='session'>Read-write session with user logged in</param>
        /// <returns>Object handle</returns>
        public static IObjectHandle GenerateKey(ISession session, string keyLabel, uint keySize, uint genAction = 0, bool preActive = false, bool bAlwSen = false, bool bNevExtr = false, string cka_idInput = null)
        {
            // genAction: 0, 1, 2, or 3.  versionCreate...0, versionRotate...1, versionMigrate...2, nonVersionCreate...3 (default)

            // Prepare attribute template of new key
            DateTime endTime = DateTime.UtcNow;
            DateTime activateTime = DateTime.UtcNow;
            Console.WriteLine("GenerateKey invoked - start time is " + endTime.ToString() + " and...");
            endTime = endTime.AddDays(31);

            if (preActive == true)
            {
                activateTime = activateTime.AddDays(7);
                Console.WriteLine("PreActive Key: ...activation time is " + activateTime.ToString());
            }
            Console.WriteLine("...end time is " + endTime.ToString());

            List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyLabel));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_KEY_TYPE, (uint)CKK.CKK_AES));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VALUE_LEN, keySize));

            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_TOKEN, true));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ENCRYPT, true));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DECRYPT, true));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DERIVE, true));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_EXTRACTABLE, true));

            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_END_DATE, endTime));
            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_MODIFIABLE, true));

            objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_OBJECT_ALIAS, keyLabel));

	    // Add the CKA_ID attribute if the cka id input has value.
            if (!string.IsNullOrEmpty(cka_idInput))
            {
                objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ID, cka_idInput));
            } 
            if (preActive == true)
                objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_KEY_ACTIVATION_DATE, activateTime));

            if (genAction < 3)
                objectAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_KEY_VERSION_ACTION, genAction));

            // Specify key generation mechanism

            IMechanism mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_KEY_GEN);

            // Generate key
            return session.GenerateKey(mechanism, objectAttributes);
        }

        /// <summary>
        /// Generates asymmetric key pair.
        /// </summary>
        /// <param name='session'>Read-write session with user logged in</param>
        /// <param name='publicKeyHandle'>Output parameter for public key object handle</param>
        /// <param name='privateKeyHandle'>Output parameter for private key object handle</param>
        public static void GenerateKeyPair(ISession session, out IObjectHandle publicKeyHandle, out IObjectHandle privateKeyHandle, string keyPairLabel)
        {
            // The CKA_ID attribute is intended as a means of distinguishing multiple key pairs held by the same subject
            // byte[] ckaId = session.GenerateRandom(20);

            // Prepare attribute template of new public key
            List<IObjectAttribute> publicKeyAttributes = new List<IObjectAttribute>();
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_TOKEN, true));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_PUBLIC_KEY));
            //publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ALWAYS_SENSITIVE, true));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_PRIVATE, false));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyPairLabel));
            //publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ID, ckaId));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ENCRYPT, true));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VERIFY, true));
            //publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_VERIFY_RECOVER, true));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_WRAP, true));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_MODULUS_BITS, 2048));
            publicKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_PUBLIC_EXPONENT, new byte[] { 0x01, 0x00, 0x01, 0x00 }));
            
            // Prepare attribute template of new private key
            List<IObjectAttribute> privateKeyAttributes = new List<IObjectAttribute>();
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_TOKEN, true));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_PRIVATE, true));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_LABEL, keyPairLabel));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_CLASS, (uint)CKO.CKO_PRIVATE_KEY));
            //privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_ID, ckaId));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_SENSITIVE, true));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_DECRYPT, true));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_SIGN, true));
            //privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_SIGN_RECOVER, true));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_UNWRAP, true));
            //privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_OBJECT_ALIAS, keyPairLabel));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_EXTRACTABLE, true));
            privateKeyAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_MODIFIABLE, true));

            // Specify key generation mechanism
            IMechanism mechanism = session.Factories.MechanismFactory.Create(CKM.CKM_RSA_PKCS_KEY_PAIR_GEN);

            // Generate key pair
            session.GenerateKeyPair(mechanism, publicKeyAttributes, privateKeyAttributes, out publicKeyHandle, out privateKeyHandle);
        }

        public static void PrintAttributes(List<IObjectAttribute> objectAttributes)
        {
            byte[] valArray;
            string str, name;
            long epoch_time;
            DateTime? date;

            foreach (IObjectAttribute attr in objectAttributes)
            {
                try
                {
                    name = Enum.GetName(typeof(CKA), (CKA)attr.Type);

                    switch (attr.Type)
                    {

                        case (uint)CKA.CKA_APPLICATION:
                            Console.WriteLine("CKA_APPLICATION" + " : " + attr.GetValueAsString());
                            break;
                        case (uint)CKA.CKA_CLASS: // converting its value to an uint fails for inexplicable reasons
                            break;
                        case (uint)CKA.CKA_KEY_TYPE:
                            switch (attr.GetValueAsUlong())
                            {
                                case 0: Console.WriteLine(name + " : RSA"); break;
                                case 31: Console.WriteLine(name + " : AES"); break;
                                case 19: Console.WriteLine(name + " : Opaque"); break;
                                default: Console.WriteLine(name + " : " + attr.GetValueAsUlong()); break;
                            }
                            break;
                        case (uint)CKA.CKA_MODULUS_BITS:
                        case (uint)CKA.CKA_ID:
                            Console.WriteLine(name + " : " + attr.GetValueAsUlong());
                            break;
                        case (uint)CKA.CKA_LABEL:
                            Console.WriteLine(name + " : " + attr.GetValueAsString());
                            break;
                        case (uint)CKA.CKA_END_DATE:
                            date = attr.GetValueAsDateTime();
                            Console.WriteLine(name + " : " + date.ToString());
                            break;

                        case (uint)CKA.CKA_THALES_OBJECT_CREATE_DATE_EL:
                        case (uint)CKA.CKA_THALES_KEY_DEACTIVATION_DATE_EL:
                            epoch_time = (long)attr.GetValueAsUlong();
                            date = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddMilliseconds(epoch_time * 1000);
                            Console.WriteLine(name + " : " + date.ToString());
                            break;

                        case (uint)CKA.CKA_KEY_CACHE_ON_HOST:
                            if (attr.GetValueAsByteArray().Length == 0)
                                Console.WriteLine(name + " : No");
                            else
                                Console.WriteLine(name + " : " + attr.GetValueAsBool().ToString());
                            break;

                        case (uint)CKA.CKA_THALES_CUSTOM_1:
                        case (uint)CKA.CKA_THALES_CUSTOM_2:
                        case (uint)CKA.CKA_THALES_CUSTOM_3:
                        case (uint)CKA.CKA_THALES_CUSTOM_4:
                        case (uint)CKA.CKA_THALES_CUSTOM_5:
                            Console.WriteLine(name + " : " + attr.GetValueAsString());
                            break;

                        default:
                            valArray = attr.GetValueAsByteArray();
			    if (valArray.Length == 0)
                            {
                                Console.WriteLine(name + " : " + valArray.Length);
                            }
                            else
                            {
                                str = BitConverter.ToString(valArray);
                                StringBuilder sb = new StringBuilder();
                                foreach (var c in str)
                                    if (c != '-') sb.Append(c);

                                Console.WriteLine(name + " : " + sb.ToString().ToLower());
                            }

                            break;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                }
            }
        }
    }
}
