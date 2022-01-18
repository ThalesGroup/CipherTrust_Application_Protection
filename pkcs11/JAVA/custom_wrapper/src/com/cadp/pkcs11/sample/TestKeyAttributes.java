package com.cadp.pkcs11.sample;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/


import com.cadp.pkcs11.wrapper.*;
import static com.cadp.pkcs11.wrapper.PKCS11Constants.*;
import java.util.GregorianCalendar;
import java.util.Calendar;
import java.util.Date;
import java.util.UUID;

/*
 ***************************************************************************
 * File: TestKeyAttributes.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Create a connection and logging in.
 * 3. Create an asymmetric key pair on the KeyManager
 * 4. Sign a piece of message with the created private key
 * 5. Verify the message was signed with the created private key
 *    by using public key Id and signed signature.
 * 6. Delete the keypair.
 * 7. Clean up.
 */

public class TestKeyAttributes {

    public static final String DEFAULT_ASYM_KEY_NAME = "ASYMKEY_" + UUID.randomUUID().toString().substring(24);
    public static final String publicKeyname = "java_test_keypair";
    public static final String privateKeyname = "java_test_keypair_private";
    public static final String signText = "The message to be signed.";
    public static final String DEFAULT_SYM_KEY_NAME = "SYMKEY_" + UUID.randomUUID().toString().substring(24);

    public static final int CKA_THALES_DEFINED = 0x40000000;

    public static final int CKA_THALES_CUSTOM_DEFINED = CKA_THALES_DEFINED | 0x8000;
    public static final int CKA_THALES_CUSTOM_1 = CKA_THALES_CUSTOM_DEFINED | 0x01;
    public static final int CKA_THALES_CUSTOM_2 = CKA_THALES_CUSTOM_DEFINED | 0x02;
    public static final int CKA_THALES_CUSTOM_3 = CKA_THALES_CUSTOM_DEFINED | 0x03;
    public static final int CKA_THALES_CUSTOM_4 = CKA_THALES_CUSTOM_DEFINED | 0x04;
    public static final int CKA_THALES_CUSTOM_5 = CKA_THALES_CUSTOM_DEFINED | 0x05;

    public static final String DEFAULT_CUSTOM_VALUE = "default custom value";

    public static final int CKA_THALES_OBJECT_UUID = CKA_THALES_DEFINED | 0x87;
    public static final int CKA_THALES_OBJECT_MUID = CKA_THALES_DEFINED | 0x88;
    public static final int CKA_THALES_OBJECT_IKID = CKA_THALES_DEFINED | 0x89;

    public static final int CKA_THALES_KEY_STATE_START_DATE  = 0x10;
    public static final int CKA_THALES_KEY_STATE_DEACTIVATED = CKA_THALES_DEFINED | 0x1004;
    public static final int CKA_THALES_DATE_OBJECT_CREATE    = CKA_THALES_DEFINED | 0x1B;
    public static final int CKA_THALES_DATE_KEY_DEACTIVATION = CKA_THALES_KEY_STATE_DEACTIVATED | CKA_THALES_KEY_STATE_START_DATE;

    public static void usage()
    {
        System.out.println("usage: java [-cp CLASSPATH] com.cadp.pkcs11.sample.TestKeyAttributes -p pin [-k keyname] [-m module] [-b modulusBits]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-b: ModulusBits");
        System.exit(1);
    }

    public static void main(String[] args)
    {
        String pin = null;
        String libPath = null;
        String keyName = null;
        int modulusBits = 2048;
        int days = 90;
        boolean symmetric = true;

        int i;
        for (i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) {
                keyName = args[i+1];
                symmetric = true;
            }
            else if (args[i].equals("-kp")) {
                keyName = args[i + 1];
                symmetric = false;
            }
            else if (args[i].equals("-b")) modulusBits = Integer.parseInt(args[i+1]);
            else if (args[i].equals("-d")) days = Integer.parseInt(args[i+1]);
            else usage();
        }

        long publickeyID, privatekeyID;
        long[] keyIDArr;
        Vpkcs11Session session = null;
        try
        {
            if (keyName == null) {

                if(symmetric == false) {
                    keyName = DEFAULT_ASYM_KEY_NAME;
                }
                else{
                    keyName = DEFAULT_SYM_KEY_NAME;
                }
            }

            System.out.println ("Start TestKeyAttributes ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            if(symmetric == false) {
            /* Create the keypair */
                CK_MECHANISM mechanism = new CK_MECHANISM(CKM_RSA_PKCS_KEY_PAIR_GEN);
                byte[] publicExponent = {0x01, 0x00, 0x01, 0x00};

                CK_ATTRIBUTE[] publicKeyAttr = new CK_ATTRIBUTE[]{
                        new CK_ATTRIBUTE(CKA_LABEL, keyName)
                        , new CK_ATTRIBUTE(CKA_CLASS, CKO_PUBLIC_KEY)
                        , new CK_ATTRIBUTE(CKA_ENCRYPT, true)
                        , new CK_ATTRIBUTE(CKA_SIGN, true)
                        , new CK_ATTRIBUTE(CKA_VERIFY, true)
                        , new CK_ATTRIBUTE(CKA_WRAP, true)
                        , new CK_ATTRIBUTE(CKA_TOKEN, true)
                        , new CK_ATTRIBUTE(CKA_PUBLIC_EXPONENT, publicExponent)
                        , new CK_ATTRIBUTE(CKA_MODULUS_BITS, modulusBits)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_1, DEFAULT_CUSTOM_VALUE)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_2, DEFAULT_CUSTOM_VALUE)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_3, DEFAULT_CUSTOM_VALUE)
                };

                CK_ATTRIBUTE[] privateKeyAttr = new CK_ATTRIBUTE[]{
                        new CK_ATTRIBUTE(CKA_LABEL, keyName)
                        , new CK_ATTRIBUTE(CKA_CLASS, CKO_PRIVATE_KEY)
                        , new CK_ATTRIBUTE(CKA_TOKEN, true)
                        , new CK_ATTRIBUTE(CKA_PRIVATE, true)
                        , new CK_ATTRIBUTE(CKA_SENSITIVE, true)
                        , new CK_ATTRIBUTE(CKA_DECRYPT, true)
                        , new CK_ATTRIBUTE(CKA_SIGN, true)
                        , new CK_ATTRIBUTE(CKA_UNWRAP, true)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_1, DEFAULT_CUSTOM_VALUE)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_2, DEFAULT_CUSTOM_VALUE)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_3, DEFAULT_CUSTOM_VALUE)
                };
                long asymKeyId[] = session.p11.C_GenerateKeyPair(session.sessionHandle, mechanism, publicKeyAttr, privateKeyAttr);
                System.out.println("-----> Asym Key " + keyName + " successfully Generated. Public Key Handle: " + asymKeyId[0] + ", private key handle: " + asymKeyId[1]);

                CK_ATTRIBUTE[] getAttributesA = new CK_ATTRIBUTE[]{
                        new CK_ATTRIBUTE(CKA_KEY_TYPE)
                        , new CK_ATTRIBUTE(CKA_LABEL)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_1)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_2)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_3)
                        , new CK_ATTRIBUTE(CKA_MODULUS_BITS)
                        , new CK_ATTRIBUTE(CKA_MODULUS)
                        , new CK_ATTRIBUTE(CKA_PUBLIC_EXPONENT)
                        , new CK_ATTRIBUTE(CKA_THALES_DATE_KEY_DEACTIVATION)
                        , new CK_ATTRIBUTE(CKA_THALES_DATE_OBJECT_CREATE)

                };
                System.out.println("-----> Getting custom attributes for public key [" + keyName + "]...");
                session.p11.C_GetAttributeValue(session.sessionHandle, asymKeyId[0], getAttributesA);
                Helper.printAttributes(getAttributesA);

                CK_ATTRIBUTE[] getAttributesB = new CK_ATTRIBUTE[]{
                        new CK_ATTRIBUTE(CKA_KEY_TYPE)
                        , new CK_ATTRIBUTE(CKA_LABEL)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_1)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_2)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_3)
                        , new CK_ATTRIBUTE(CKA_MODULUS)
                        , new CK_ATTRIBUTE(CKA_THALES_DATE_OBJECT_CREATE)
                };

                System.out.println("-----> Getting custom attributes for private key [" + keyName + "]...");
                session.p11.C_GetAttributeValue(session.sessionHandle, asymKeyId[1], getAttributesB);
                Helper.printAttributes(getAttributesB);
            }
            else {
                System.out.println("-----> Creating symmetric key with custom attributes...");
                CK_DATE startDate = generateDate(1);
                CK_DATE endDate = generateDate(61);

                long symKeyId = Helper.findKey(session, keyName) ;

                if(symKeyId == 0) {
                    CK_MECHANISM aesMechanism = new CK_MECHANISM(CKM_AES_KEY_GEN);
                    CK_ATTRIBUTE[] attributes = new CK_ATTRIBUTE[] {
                            new CK_ATTRIBUTE(CKA_LABEL, keyName)
                            , new CK_ATTRIBUTE(CKA_APPLICATION, "JAVA ATTRIBUTE SAMPLE TEST")
                            , new CK_ATTRIBUTE(CKA_CLASS, CKO_SECRET_KEY)
                            , new CK_ATTRIBUTE(CKA_KEY_TYPE, CKK_AES)
                            , new CK_ATTRIBUTE(CKA_VALUE_LEN, 32)
                            , new CK_ATTRIBUTE(CKA_TOKEN, true)
                            , new CK_ATTRIBUTE(CKA_ENCRYPT, true)
                            , new CK_ATTRIBUTE(CKA_DECRYPT, true)
                            , new CK_ATTRIBUTE(CKA_SIGN, false)
                            , new CK_ATTRIBUTE(CKA_VERIFY, false)
                            , new CK_ATTRIBUTE(CKA_WRAP, true)
                            , new CK_ATTRIBUTE(CKA_UNWRAP, true)
                            , new CK_ATTRIBUTE(CKA_EXTRACTABLE, false)
                            , new CK_ATTRIBUTE(CKA_ALWAYS_SENSITIVE, false)
                            , new CK_ATTRIBUTE(CKA_NEVER_EXTRACTABLE, true)
                            , new CK_ATTRIBUTE(CKA_SENSITIVE, true)
                            , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_1, DEFAULT_CUSTOM_VALUE)
                            , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_2, DEFAULT_CUSTOM_VALUE)
                            , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_3, DEFAULT_CUSTOM_VALUE)
                    };
                    symKeyId = session.p11.C_GenerateKey(session.sessionHandle, aesMechanism, attributes);
                    System.out.println("-----> Sym Key successfully Generated. Key Handle: " + symKeyId + ", key name: " + keyName);
                }

                System.out.println("-----> Setting custom attributes for key [" + keyName + "] ...");

                CK_ATTRIBUTE[] setAttributes = new CK_ATTRIBUTE[]{
                        new CK_ATTRIBUTE(CKA_THALES_CUSTOM_1, DEFAULT_CUSTOM_VALUE + 1)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_2, DEFAULT_CUSTOM_VALUE + 2)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_3, DEFAULT_CUSTOM_VALUE + 3)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_4, DEFAULT_CUSTOM_VALUE + 4)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_5, DEFAULT_CUSTOM_VALUE + 5)
                };
                session.p11.C_SetAttributeValue(session.sessionHandle, symKeyId, setAttributes);

                System.out.println("-----> Getting custom attributes for key [" + keyName + "]...");
                CK_ATTRIBUTE[] getAttributes = new CK_ATTRIBUTE[]{
                        new CK_ATTRIBUTE(CKA_KEY_TYPE)
                        , new CK_ATTRIBUTE(CKA_LABEL)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_1)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_2)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_3)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_4)
                        , new CK_ATTRIBUTE(CKA_THALES_CUSTOM_5)
                        , new CK_ATTRIBUTE(CKA_THALES_DATE_KEY_DEACTIVATION)
                        , new CK_ATTRIBUTE(CKA_THALES_DATE_OBJECT_CREATE)
                        , new CK_ATTRIBUTE(Helper.CKA_THALES_DATE_OBJECT_CREATE_EL)
                        , new CK_ATTRIBUTE(Helper.CKA_THALES_DATE_KEY_DEACTIVATION_EL)
                };
                session.p11.C_GetAttributeValue(session.sessionHandle, symKeyId, getAttributes);
                Helper.printAttributes(getAttributes);

                System.out.println("-----> Setting readonly attributes for key [" + keyName + "]... (expected to fail)");

                //String uuid = UUID.randomUUID().toString();
                // String muid = uuid + UUID.randomUUID().toString();
                Date jendDate = genCalDate(days);
                System.out.println("-----> Setting new date/time for deactivation: " + jendDate.getTime()+" milliseconds ");

                setAttributes = new CK_ATTRIBUTE[]{
                        new CK_ATTRIBUTE(Helper.CKA_THALES_DATE_KEY_DEACTIVATION_EL, jendDate.getTime()/1000)
                };
                session.p11.C_SetAttributeValue(session.sessionHandle, symKeyId, setAttributes);

                System.out.println("-----> Getting custom attributes for key [" + keyName + "] after setting attribute CKA_THALES_DATE_KEY_DEACTIVATION_EL ... ");
                session.p11.C_GetAttributeValue(session.sessionHandle, symKeyId, getAttributes);
                Helper.printAttributes(getAttributes);
            }
        } catch (PKCS11Exception e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            Helper.closeDown(session);
            System.out.println ("End TestKeyAttributes." );
        }
    }

    private static Date genCalDate(int daysLater) {
        Calendar cal = new GregorianCalendar();
        cal.setTime(new Date());
        cal.add(Calendar.DAY_OF_MONTH, daysLater);

        String year = String.valueOf(cal.get(Calendar.YEAR));
        String month = String.valueOf(cal.get(Calendar.MONTH)+1); // Calendar is zero based!
        String day = String.valueOf(cal.get(Calendar.DAY_OF_MONTH));

        System.out.println("year/month/day: "+ year + "/"+ month+ "/"+day);
        Date genDate = cal.getTime();
        return genDate;
    }

    private static CK_DATE generateDate(int daysLater) {
        Calendar cal = new GregorianCalendar();
        cal.setTime(new Date());
        cal.add(Calendar.DATE, daysLater);

        String year = String.valueOf(cal.get(Calendar.YEAR));
        String month = String.valueOf(cal.get(Calendar.MONTH)+1); // Calendar is zero based!
        String day = String.valueOf(cal.get(Calendar.DAY_OF_MONTH));

        System.out.println("year/month/day: "+ year + "/"+ month+ "/"+day);
        CK_DATE ckDate = new CK_DATE(year.toCharArray(), month.toCharArray(), day.toCharArray());
        return ckDate;
    }
}
