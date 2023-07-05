package com.vormetric.pkcs11.sample;

import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_ALWAYS_SENSITIVE;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_CLASS;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_DECRYPT;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_ENCRYPT;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_EXTRACTABLE;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_KEY_TYPE;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_LABEL;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_NEVER_EXTRACTABLE;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_SENSITIVE;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_SIGN;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_TOKEN;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_UNWRAP;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_VALUE_LEN;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_VERIFY;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKA_WRAP;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKK_AES;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKM_AES_KEY_GEN;
import static com.vormetric.pkcs11.wrapper.PKCS11Constants.CKO_SECRET_KEY;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
 ***************************************************************************
 * File: KeyStateTransition.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following
 * 1. Initialization
 * 2. Creating a connection and logging in.
 * 3. Creating a symmetric key with key transition dates specified, or
 * 4. Setting the key transition dates of an existing symmetric key, or
 * 5. Setting the key state of an existing symmetric key, and
 * 6, Getting the key attributes of the created or existing key
 * 7. Clean up.
 */
import java.util.ArrayList;
import java.util.Arrays;

import com.vormetric.pkcs11.wrapper.CK_ATTRIBUTE;
import com.vormetric.pkcs11.wrapper.CK_DATE;
import com.vormetric.pkcs11.wrapper.CK_MECHANISM;
import com.vormetric.pkcs11.wrapper.PKCS11Exception;

public class KeyStateTransition {
    public static final String defKeyName = "pkcs11_java_test_key";
    public static final String app = "PKCS11_SAMPLE";
    public static final String keyValue = "This is my sample key data 54321";


    public static void usage() {
        System.out.println("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.KeyStatesTransition -p pin [-m module] [-k keyName] [-ks keystate] [-da Key activation date] [-ds Key suspension date] [-dd Key deactivation date] [-dp Key compromised date]"
        		+ " [-dc Key Creation date] [-dt Key destroy date] [-ps Key process start date] [-pt Key protect stop date]" );
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-m: Path of directory where dll is deployed/installed");
        System.out.println("-k: Keyname on Keymanager");
        System.out.println("-ks: Keystate");
        System.out.println("-da: Key activation date");
        System.out.println("-ds: Key suspension date");
        System.out.println("-dd: Key deactivation date");
        System.out.println("-dp: Key compromised date");
        System.out.println("-dc: Key Creation date");
        System.out.println("-dt: Key destroy date");
        System.out.println("-ps: Key process start date");
        System.out.println("-pt: Key protect stop date");
        System.exit(1);
    }

    public static long createKeywDates(Vpkcs11Session session, String keyName, ArrayList dateList, int genAction) {
        long keyID = 0;
        /*String year, month, day;
         Create an AES 256 key on the DSM without pass in key value */
        try {
            /* Date date = new Date();
            Calendar cal = new GregorianCalendar();
            cal.setTime(date);
            cal.add(Calendar.DATE, 180);

            year = String.valueOf(cal.get(Calendar.YEAR));
            month = String.valueOf(cal.get(Calendar.MONTH) + 1); // Calendar is zero based!
            day = String.valueOf(cal.get(Calendar.DAY_OF_MONTH));

            System.out.println("To be set End Date: year: " + year + " month: " + month + " day: " + day);
            CK_DATE endDate = new CK_DATE(year.toCharArray(), month.toCharArray(), day.toCharArray()); */

            CK_MECHANISM mechanism = new CK_MECHANISM(CKM_AES_KEY_GEN);

            CK_ATTRIBUTE[] attrs = new CK_ATTRIBUTE[]
                    {
                            new CK_ATTRIBUTE(CKA_LABEL, keyName),
                            new CK_ATTRIBUTE(CKA_CLASS, CKO_SECRET_KEY),
                            new CK_ATTRIBUTE(CKA_KEY_TYPE, CKK_AES),
                            new CK_ATTRIBUTE(CKA_VALUE_LEN, 32),
                            new CK_ATTRIBUTE(CKA_TOKEN, true),
                            new CK_ATTRIBUTE(CKA_ENCRYPT, true),
                            new CK_ATTRIBUTE(CKA_DECRYPT, true),
                            new CK_ATTRIBUTE(CKA_SIGN, false),
                            new CK_ATTRIBUTE(CKA_VERIFY, false),
                            new CK_ATTRIBUTE(CKA_WRAP, true),
                            new CK_ATTRIBUTE(CKA_UNWRAP, true),
                            new CK_ATTRIBUTE(CKA_EXTRACTABLE, false),
                            new CK_ATTRIBUTE(CKA_ALWAYS_SENSITIVE, false),
                            new CK_ATTRIBUTE(CKA_NEVER_EXTRACTABLE, true),
                            new CK_ATTRIBUTE(CKA_SENSITIVE, true),
                            new CK_ATTRIBUTE(Helper.CKA_KEY_CACHE_ON_HOST, true),
                            new CK_ATTRIBUTE(Helper.CKA_KEY_CACHED_TIME, 44640),
                            new CK_ATTRIBUTE(Helper.CKA_THALES_KEY_VERSION_ACTION, genAction)
                    };

            ArrayList attrsList = new ArrayList(Arrays.asList(attrs));
            attrsList.addAll(dateList);

            CK_ATTRIBUTE[] attrsFull = (CK_ATTRIBUTE[]) attrsList.toArray(attrs);

            System.out.println("Before generating Key. Key Handle: " + keyID);
            keyID = session.p11.C_GenerateKey(session.sessionHandle, mechanism, attrsFull);
            System.out.println("Successfully Generated key. Key label: "+keyName+"; Key handle: " + keyID);
        } catch (PKCS11Exception e) {
            e.printStackTrace();
        }
        return keyID;
    }


    public static void main ( String[] args) throws Exception
    {
        String pin = null;
        String libPath = null;

        ArrayList dateList = new ArrayList();
        CK_DATE curDate;
        int genAction = 0;
        String keyName = null;

        Helper.KeyState kstate = Helper.KeyState.PreActive;
        boolean bKeyState = false;
        long  lepoch;
        long  attrType;
        Vpkcs11Session session = null;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-k")) keyName = args[i+1];
            else if (args[i].equals("-g")) genAction = Integer.parseInt(args[i+1]);
            else if (args[i].equals("-ks")) {
                kstate = Helper.KeyState.valueOf(args[i+1]);
                bKeyState = true;
            }
            else if (args[i].startsWith("-da")) {
                attrType = Helper.CKA_THALES_KEY_ACTIVATION_DATE;

                if(args[i].equals("-dal")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }
            else if (args[i].startsWith("-ds")) {
                attrType = Helper.CKA_THALES_KEY_SUSPENSION_DATE;
                if(args[i].equals("-dsl")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }
            else if (args[i].equals("-dd")) {
                attrType = Helper.CKA_THALES_KEY_DEACTIVATION_DATE;
                if(args[i].equals("-ddl")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }
            else if (args[i].equals("-dp")) {
                attrType = Helper.CKA_THALES_KEY_COMPROMISED_DATE;
                if(args[i].equals("-dpl")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }
            else if (args[i].equals("-dt")) {
                attrType = Helper.CKA_THALES_OBJECT_DESTROY_DATE;
                if(args[i].equals("-dtl")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }
            else if (args[i].equals("-dc")) {
                attrType = Helper.CKA_THALES_OBJECT_CREATE_DATE;
                if(args[i].equals("-dcl")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }
            else if (args[i].equals("-ps")) {
                attrType = Helper.CKA_THALES_KEY_PROCESS_START_DATE;
                if(args[i].equals("-psl")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }
            else if (args[i].equals("-pt")) {
                attrType = Helper.CKA_THALES_KEY_PROTECT_STOP_DATE;
                if(args[i].equals("-ptl")) {
                    try {
                        lepoch = Long.valueOf(args[i + 1]);
                        attrType = (attrType & 0x0FFFFFFF) | 0x80000000;
                        dateList.add(new CK_ATTRIBUTE(attrType, lepoch));
                    }
                    catch(NumberFormatException nfe) {
                    }
                }
                else {
                    curDate = Helper.parseDate(args[i + 1]);
                    dateList.add(new CK_ATTRIBUTE(attrType, curDate));
                }
            }

            else usage();
        }

        try
        {
            System.out.println ("Start KeyStatesTransition ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath),pin );

            if(keyName == null)
                keyName = defKeyName;

            long keyID = Helper.findKey(session, keyName) ;

            if (keyID == 0)
            {
                System.out.println ("the key not found, creating it..." );
                keyID = createKeywDates(session, keyName, dateList, genAction);
				if (!dateList.isEmpty())
                    Helper.setKeyTransitionDates(session, keyID, dateList);
            }
            else
            {
                System.out.println ("The key is found on DSM:" + keyName);

                if(bKeyState == true) {
                    Helper.setKeyState(session, keyID, kstate);
                }
                else if(!dateList.isEmpty()) {
                    Helper.setKeyTransitionDates(session, keyID, dateList);
                }
            }

            System.out.println("-----> Getting attributes for key: " + keyName + " ...");

            CK_ATTRIBUTE[] getAttrs = new CK_ATTRIBUTE[] {
                    new CK_ATTRIBUTE(CKA_KEY_TYPE)
                    ,new CK_ATTRIBUTE(CKA_LABEL)
            };

            ArrayList attrsList = new ArrayList(Arrays.asList(getAttrs));
            attrsList.addAll(dateList);

            CK_ATTRIBUTE[] attrsFull = (CK_ATTRIBUTE[]) attrsList.toArray(getAttrs);

            session.p11.C_GetAttributeValue(session.sessionHandle, keyID, attrsFull);

            Helper.printAttributes(attrsFull);
        }
        catch (Exception e)
        {
            e.printStackTrace();
            System.out.println("The Cause is " + e.getMessage() + ".");
            throw e;
        }
        finally {
            Helper.closeDown(session);
            System.out.println ("End KeyStateTransition." );
        }
    }
}
