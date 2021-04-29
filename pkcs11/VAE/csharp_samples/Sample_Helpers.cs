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

using System;
using System.Text;
using Net.Pkcs11Interop.HighLevelAPI;
using Net.Pkcs11Interop.LowLevelAPI;
using System.Collections.Generic;
using Net.Pkcs11Interop.Common;

namespace Vormetric.Pkcs11Sample
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
        public static Slot GetUsableSlot(Net.Pkcs11Interop.HighLevelAPI.Pkcs11 pkcs11)
        {
            // Get list of available slots
            List<Slot> slots = pkcs11.GetSlotList(false);

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
            else {
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
            if (string.IsNullOrEmpty(sel)) {
                Console.WriteLine("Invalid format type.");
                return 0;
            }

            if (StringComparer.OrdinalIgnoreCase.Equals(sel, "pem") == true)
                formatType = (uint)CKA.CKA_THALES_PEM_FORMAT;

            return formatType;
        }

        public static ObjectHandle FindKey(Session session, string keyLabel)
        {            
            ObjectHandle key = null;
            List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_THALES_CACHE_CLEAR, true));

            // Initialize searching
            session.FindObjectsInit(objectAttributes);

            // Get search results
            List<ObjectHandle> foundObjects = session.FindObjects(1);

            // Terminate searching
            session.FindObjectsFinal();

            foreach (ObjectHandle handle in foundObjects)
            {
                Console.WriteLine("Found key with label: " + keyLabel + "!");
                return handle;
            }

            return key;
        }

        public static ObjectHandle FindKey(Session session, string keyLabel, uint keyType)
        {
            ObjectHandle key = null;
            List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, keyType));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_THALES_CACHE_CLEAR, true));

            // Initialize searching
            session.FindObjectsInit(objectAttributes);

            // Get search results
            List<ObjectHandle> foundObjects = session.FindObjects(1);

            // Terminate searching
            session.FindObjectsFinal();

            foreach (ObjectHandle handle in foundObjects)
            {
                Console.WriteLine("Found key with label: " + keyLabel + "!");
                return handle;
            }

            return key;
        }

        public static ObjectHandle CreateKeyObject(Session session, string keyLabel, string keyValue, uint keySize)
        {
            ObjectHandle key = null;
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

            // Import symetric key object          

            key = session.CreateObject(objectAttributes);
            if (null != key)
            {
                Console.WriteLine(keyLabel + " key created!");
            }
            return key;
        }

        public static void CleanupKey(Session session, string keyLabel)
        {
            
            List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));

            // Initialize searching
            session.FindObjectsInit(objectAttributes);

            // Get search results
            List<ObjectHandle> foundObjects = session.FindObjects(2);

            // Terminate searching
            session.FindObjectsFinal();

            foreach (ObjectHandle handle in foundObjects)
            {
                const uint KeyStateDeactivated = 3;
                List<ObjectAttribute> objAttributes = new List<ObjectAttribute>();
                objAttributes.Add(new ObjectAttribute(CKA.CKA_THALES_KEY_STATE, KeyStateDeactivated));
                session.SetAttributeValue(handle, objAttributes);

                session.DestroyObject(handle);
                Console.WriteLine("Existing " + keyLabel + " key deleted!");
            }
        }

        /// <summary>
        /// Migrate symmetric key.
        /// </summary>
        /// <param name='session'>Read-write session with user logged in</param>
        public static bool MigrateKey(Session session, string keyLabel, uint genAction)
        {
            // genAction: versionMigrate...2

            List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));

            // Initialize searching
            session.FindObjectsInit(objectAttributes);

            // Get search results
            List<ObjectHandle> foundObjects = session.FindObjects(2);

            // Terminate searching
            session.FindObjectsFinal();

            // No Objects find...(and no key found)
            if (foundObjects.Count == 0) {
                return false;
            }
            foreach (ObjectHandle handle in foundObjects)
            {
              List<ObjectAttribute> objectAttributesNew = new List<ObjectAttribute>();
              objectAttributesNew.Add(new ObjectAttribute(CKA.CKA_THALES_KEY_VERSION_ACTION, genAction));

              session.SetAttributeValue(handle, objectAttributesNew);
            }
            return true;
        }

        /// <summary>
        /// Generates symmetric key.
        /// </summary>
        /// <param name='session'>Read-write session with user logged in</param>
        /// <returns>Object handle</returns>
        public static ObjectHandle GenerateKey(Session session, string keyLabel, uint keySize, uint genAction = 0, bool preActive = false, bool bAlwSen = false, bool bNevExtr = false)
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
            Console.WriteLine("...end time is " + endTime.ToString() );

            List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_KEY_TYPE, (uint)CKK.CKK_AES));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_VALUE_LEN, keySize));

            objectAttributes.Add(new ObjectAttribute(CKA.CKA_TOKEN, true));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_ENCRYPT, true));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_DECRYPT, true));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_DERIVE, true));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_ALWAYS_SENSITIVE, bAlwSen));
            objectAttributes.Add(new ObjectAttribute(CKA.CKA_NEVER_EXTRACTABLE, bNevExtr));

            objectAttributes.Add(new ObjectAttribute(CKA.CKA_END_DATE, endTime));

            if (preActive == true)
                objectAttributes.Add(new ObjectAttribute(CKA.CKA_THALES_KEY_ACTIVATION_DATE, activateTime));
                       
            if (genAction < 3)
                objectAttributes.Add(new ObjectAttribute(CKA.CKA_THALES_KEY_VERSION_ACTION, genAction));

            // Specify key generation mechanism

            Mechanism mechanism = new Mechanism(CKM.CKM_AES_KEY_GEN);

            // Generate key
            return session.GenerateKey(mechanism, objectAttributes);
        }

        /// <summary>
        /// Generates asymmetric key pair.
        /// </summary>
        /// <param name='session'>Read-write session with user logged in</param>
        /// <param name='publicKeyHandle'>Output parameter for public key object handle</param>
        /// <param name='privateKeyHandle'>Output parameter for private key object handle</param>
        public static void GenerateKeyPair(Session session, out ObjectHandle publicKeyHandle, out ObjectHandle privateKeyHandle, string keyPairLabel)
        {
            // The CKA_ID attribute is intended as a means of distinguishing multiple key pairs held by the same subject
            // byte[] ckaId = session.GenerateRandom(20);
            
            // Prepare attribute template of new public key
            List<ObjectAttribute> publicKeyAttributes = new List<ObjectAttribute>();
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_TOKEN, true));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_PRIVATE, false));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyPairLabel));
            //publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_ID, ckaId));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_ENCRYPT, true));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_VERIFY, true));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_VERIFY_RECOVER, true));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_WRAP, true));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_MODULUS_BITS, 2048));
            publicKeyAttributes.Add(new ObjectAttribute(CKA.CKA_PUBLIC_EXPONENT, new byte[] { 0x01, 0x00, 0x01, 0x00}));
      
            // Prepare attribute template of new private key
            List<ObjectAttribute> privateKeyAttributes = new List<ObjectAttribute>();
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_TOKEN, true));
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_PRIVATE, true));
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyPairLabel));
            //privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_ID, ckaId));
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_SENSITIVE, true));
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_DECRYPT, true));
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_SIGN, true));
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_SIGN_RECOVER, true));
            privateKeyAttributes.Add(new ObjectAttribute(CKA.CKA_UNWRAP, true));

            // Specify key generation mechanism
            Mechanism mechanism = new Mechanism(CKM.CKM_RSA_PKCS_KEY_PAIR_GEN);
            
            // Generate key pair
            session.GenerateKeyPair(mechanism, publicKeyAttributes, privateKeyAttributes, out publicKeyHandle, out privateKeyHandle);
        }      

        public static void PrintAttributes(List<ObjectAttribute> objectAttributes)
        {
            byte[] valArray;
            string str, name;
            long epoch_time;
            bool bval;
            DateTime?  date;

            foreach (ObjectAttribute attr in objectAttributes)
            {
                try
                {
                    name = Enum.GetName(typeof(CKA), (CKA)attr.Type);

                    switch (attr.Type)
                    {
                        case (uint)CKA.CKA_CLASS: // converting its value to an uint fails for inexplicable reasons
                            break;
                        case (uint)CKA.CKA_KEY_TYPE:
                            switch(attr.GetValueAsUint()) {
                              case  0: Console.WriteLine(name + " : RSA"); break;
                              case 31: Console.WriteLine(name + " : AES"); break;
                              default: Console.WriteLine(name + " : " + attr.GetValueAsUint() ); break;
                            }
                            break;
                        case (uint)CKA.CKA_MODULUS_BITS:
                        case (uint)CKA.CKA_ID:
                            Console.WriteLine(name + " : " + attr.GetValueAsUint());
                            break;
                        case (uint)CKA.CKA_LABEL:
                            Console.WriteLine(name + " : " + attr.GetValueAsString());
                            break;
                        case (uint)CKA.CKA_END_DATE:
                            date = attr.GetValueAsDateTime();                            
                            Console.WriteLine(name + " : " + date.ToString());
                            break;

                        case (uint)CKA.CKA_ALWAYS_SENSITIVE:
                        case (uint)CKA.CKA_NEVER_EXTRACTABLE:
                            bval = attr.GetValueAsBool();
                            Console.WriteLine(name + " : " + bval.ToString());
                            break;

                        case (uint)CKA.CKA_THALES_OBJECT_CREATE_DATE_EL:
                        case (uint)CKA.CKA_THALES_KEY_DEACTIVATION_DATE_EL:
                            epoch_time = attr.GetValueAsUint();
                            date = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddMilliseconds(epoch_time*1000);
                            Console.WriteLine(name + " : " + date.ToString());
                            break;

                        default:
                            valArray = attr.GetValueAsByteArray();
                            str = BitConverter.ToString(valArray);
                            StringBuilder sb = new StringBuilder();
                            foreach (var c in str)
                                if (c != '-') sb.Append(c);

                            Console.WriteLine(name + " : " + sb.ToString().ToLower());

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
