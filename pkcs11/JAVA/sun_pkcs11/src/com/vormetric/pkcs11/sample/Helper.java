package com.vormetric.pkcs11.sample;

import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_MODIFIABLE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_ALWAYS_SENSITIVE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_APPLICATION;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_CLASS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_DECRYPT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_ENCRYPT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_END_DATE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_ID;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_KEY_TYPE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_LABEL;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_MODULUS_BITS;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_NEVER_EXTRACTABLE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_PRIVATE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_PUBLIC_EXPONENT;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_SENSITIVE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_SIGN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_TOKEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_UNWRAP;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_VALUE;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_VALUE_LEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_VERIFY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKA_WRAP;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKK_AES;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKM_AES_KEY_GEN;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PRIVATE_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_PUBLIC_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKO_SECRET_KEY;
import static sun.security.pkcs11.wrapper.PKCS11Constants.CKU_USER;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
 ***************************************************************************
 * File: Helper.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following common functions shared by other samples
 * 1. Initialization library
 * 2. Startup session
 * 3. Close down session
 * 4. Create key
 * 5. Create Key Object
 * 6. Find Key by Name
 * 7. Find CADP PKCS11 library path
 */
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.HashMap;
import java.util.Map;

import sun.security.pkcs11.wrapper.CK_ATTRIBUTE;
import sun.security.pkcs11.wrapper.CK_DATE;
import sun.security.pkcs11.wrapper.CK_MECHANISM;
import sun.security.pkcs11.wrapper.PKCS11;
import sun.security.pkcs11.wrapper.PKCS11Constants;
import sun.security.pkcs11.wrapper.PKCS11Exception;

class Vpkcs11Session {
   public PKCS11 p11;
   long   sessionHandle;
}

public class Helper {
    public static final String UnixInstallPath = "/opt/CipherTrust/CAP/PKCS11/lib/cipherTrustPKCS11.so";
    public static final String WinX86InstallPath = "C:\\Program Files\\CipherTrust\\CAP\\PKCS11\\cipherTrustPKCS11.dll";
    public static final String WinX64InstallPath = "C:\\Program Files\\CipherTrust\\CAP\\PKCS11\\cipherTrustPKCS11.dll";

    private static Map<Long, String> PKCS11ConstantNames;

    public static final long CKA_THALES_DEFINED  = 0x40000000L;
    public static final long CKA_VORM_DEFINED = 0x70000000L;
    public static final long CKA_VENDOR_DEFINED = 0x80000000L;

    public static final long CKA_THALES_KEY_STATE_START_DATE =  0x0010;
    public static final long CKA_THALES_KEY_STATE_STOP_DATE =  0x0020;
    public static final long CKA_THALES_KEY_STATE_OCCURRENCE_DATE= 0x0030;

    public static final long CKA_THALES_KEY_STATE = ( CKA_THALES_DEFINED | 0x1000L );
    public static final long CKA_THALES_KEY_STATE_PREACTIVATED = ( CKA_THALES_DEFINED | 0x1001L );
    public static final long CKA_THALES_KEY_STATE_ACTIVATED = ( CKA_THALES_DEFINED | 0x1002L );
    public static final long CKA_THALES_KEY_STATE_SUSPENDED = ( CKA_THALES_DEFINED | 0x1003L );
    public static final long CKA_THALES_KEY_STATE_DEACTIVATED = ( CKA_THALES_DEFINED | 0x1004L );

    public static final long CKA_THALES_KEY_STATE_COMPROMISED = ( CKA_THALES_DEFINED | 0x1006L );
    public static final long CKA_THALES_KEY_STATE_DESTROYED = ( CKA_THALES_DEFINED | 0x1007L );

    public static final long CKA_THALES_KEY_STATE_ACTIONS = ( CKA_THALES_DEFINED | 0x0100L );
    public static final long CKA_THALES_OBJECT_CREATE_DATE = ( CKA_THALES_DEFINED | 0x1BL );
    public static final long CKA_THALES_OBJECT_DESTROY_DATE	= ( CKA_THALES_DEFINED | 0x1CL );

    public static final long CKA_THALES_KEY_ACTIVATION_DATE = ( CKA_THALES_KEY_STATE_ACTIVATED | CKA_THALES_KEY_STATE_START_DATE );
    public static final long CKA_THALES_KEY_SUSPENSION_DATE = ( CKA_THALES_KEY_STATE_SUSPENDED | CKA_THALES_KEY_STATE_START_DATE );

    public static final long CKA_THALES_KEY_DEACTIVATION_DATE = ( CKA_THALES_KEY_STATE_DEACTIVATED | CKA_THALES_KEY_STATE_START_DATE );
    public static final long CKA_THALES_KEY_COMPROMISED_DATE = ( CKA_THALES_KEY_STATE_COMPROMISED | CKA_THALES_KEY_STATE_START_DATE );
    public static final long CKA_THALES_KEY_COMPROMISE_OCCURRENCE_DATE = ( CKA_THALES_KEY_STATE_COMPROMISED | CKA_THALES_KEY_STATE_OCCURRENCE_DATE );

    public static final long CKA_THALES_KEY_ACTION_PROTECT_PROCESS = ( CKA_THALES_DEFINED | 0x0101L );
    public static final long CKA_THALES_KEY_ACTION_PROTECT_ONLY = ( CKA_THALES_DEFINED | 0x0102L );
    public static final long CKA_THALES_KEY_ACTION_PROCESS_ONLY = ( CKA_THALES_DEFINED | 0x0103L );

    public static final long CKA_THALES_KEY_PROTECT_STOP_DATE = ( CKA_THALES_KEY_ACTION_PROTECT_ONLY | CKA_THALES_KEY_STATE_STOP_DATE );
    public static final long CKA_THALES_KEY_PROCESS_START_DATE = ( CKA_THALES_KEY_ACTION_PROCESS_ONLY | CKA_THALES_KEY_STATE_START_DATE );

    public static final long CKA_KEY_CACHE_ON_HOST = ( CKA_VENDOR_DEFINED | 0x00000061L );
    public static final long CKA_KEY_CACHED_TIME = ( CKA_VENDOR_DEFINED | 0x00000063L );
    public static final long CKA_THALES_CACHE_CLEAR = ( CKA_VENDOR_DEFINED | 0x00000066L );;

    public static final long CKA_THALES_KEY_CACHED_TIME =  ( CKA_THALES_DEFINED | 0x63L );
    public static final long CKA_THALES_KEY_VERSION     =  ( CKA_THALES_DEFINED | 0x81L );
    public static final long CKA_THALES_KEY_VERSION_ACTION =   ( CKA_THALES_DEFINED | 0x82L );
    public static final long CKA_THALES_KEY_VERSION_LIFE_SPAN = ( CKA_THALES_DEFINED | 0x83L );

    public static final long CKA_THALES_DATE_OBJECT_CREATE  = CKA_THALES_DEFINED | 0x1BL;

    public static final long CKA_THALES_VERSIONED_KEY  =  ( CKA_THALES_DEFINED | 0x85L );
    public static final long CKA_THALES_OBJECT_ALIAS   =  ( CKA_THALES_DEFINED | 0x86L );
    public static final long CKA_THALES_OBJECT_UUID    =  ( CKA_THALES_DEFINED | 0x87L );
    public static final long CKA_THALES_OBJECT_MUID    =  ( CKA_THALES_DEFINED | 0x88L );
    public static final long CKA_THALES_OBJECT_IKID    =  ( CKA_THALES_DEFINED | 0x89L );

    public static final long CKA_THALES_CUSTOM_DEFINED = CKA_THALES_DEFINED | 0x8000L;
    public static final long CKA_THALES_CUSTOM_1 = CKA_THALES_CUSTOM_DEFINED | 0x01L;
    public static final long CKA_THALES_CUSTOM_2 = CKA_THALES_CUSTOM_DEFINED | 0x02L;
    public static final long CKA_THALES_CUSTOM_3 = CKA_THALES_CUSTOM_DEFINED | 0x03L;
    public static final long CKA_THALES_CUSTOM_4 = CKA_THALES_CUSTOM_DEFINED | 0x04L;
    public static final long CKA_THALES_CUSTOM_5 = CKA_THALES_CUSTOM_DEFINED | 0x05L;

    public static final long CKM_THALES_PEM_FORMAT =  0x00100000L;
    public static final long CKA_THALES_DATE_OBJECT_CREATE_EL  = CKA_VORM_DEFINED | 0x1BL;
    public static final long CKA_THALES_DATE_KEY_DEACTIVATION_EL = ( CKA_THALES_KEY_DEACTIVATION_DATE & 0X0FFFFFFFL ) | CKA_VORM_DEFINED;

    public static final long CKM_VENDOR_DEFINED = 0x80000000L;
    public static final long CKM_THALES_V27HDR = 0x04000000L;
    public static final long CKM_THALES_V21HDR = 0x02000000L;
    public static final long CKM_THALES_V15HDR = 0x01000000L;
    public static final long CKM_THALES_ALLHDR = 0x07000000L;
    public static final long CKM_THALES_BASE64 = 0x08000000L;
    public static final long CKM_THALES_FPE = 0x80004001L;
    public static final long CKM_THALES_FF1 = 0x80004002L;


    public enum KeyState {
        PreActive,
        Active,
        Suspended,
        Deactivated ,
        Compromised ,
        Destroyed
    }

    public static void saveKey(byte[] keyValue, String keyFileName)
    {
        FileOutputStream out = null;
        try {
            out = new FileOutputStream(keyFileName);
            out.write(keyValue);
            out.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        finally {

        }
    }

    public static byte[] readKey(String keyFileName)
    {
        FileInputStream in = null;
        int keyLength = 0;
        byte[] fileContent = new byte[4096];
        byte[] keyValue = null;

        try {
            in = new FileInputStream(keyFileName);
            keyLength = in.read(fileContent);
            keyValue = Arrays.copyOf(fileContent, keyLength);

            in.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
        finally {
            return keyValue;
        }

    }

    public static boolean isFileExist(String filePath)
    {
        File f = new File(filePath);
        return f.exists();
    }

    public static boolean isKeySymmetric(long keyHandle)
    {
        return (keyHandle & 0xF0000000L) == 0x20000000L;
    }

    public static long findKey(Vpkcs11Session session, String keyName)
    {
        /* Find the key on the KeyManager */
        CK_ATTRIBUTE[] attrs = new CK_ATTRIBUTE[]
        	{
                new CK_ATTRIBUTE (CKA_LABEL, keyName),
                new CK_ATTRIBUTE (CKA_CLASS, CKO_SECRET_KEY),
                new CK_ATTRIBUTE (CKA_THALES_CACHE_CLEAR, true)
            };

        try
        {
            /* Call C_FindObjectsFinal in case there is another find objects going on  */
            session.p11.C_FindObjectsFinal (session.sessionHandle);
            session.p11.C_FindObjectsInit (session.sessionHandle, attrs);
            long[] keyID = session.p11.C_FindObjects (session.sessionHandle, 1);
            session.p11.C_FindObjectsFinal (session.sessionHandle);
            if (keyID.length > 0)
            {
                return keyID[0];
            }
            else
            {
                /* System.out.println ("The key: " + keyName + " is not found."); */
                return 0;
            }
        }
        catch (PKCS11Exception e)
        {
            if(e.getErrorCode() == PKCS11Constants.CKR_OBJECT_HANDLE_INVALID)
                return 0;
            System.out.println (e.getMessage());
            e.printStackTrace();
        }
        catch (Exception e)
        {
            System.out.println ("Exception thrown.");
            System.out.println (e.getMessage());
            e.printStackTrace();
        }
        return 0;
    }

    public static long findKey(Vpkcs11Session session, String keyName, long keyClass)
    {
        /* Find the key on the KeyManager */
        CK_ATTRIBUTE[] attrs = new CK_ATTRIBUTE[]
            {
                new CK_ATTRIBUTE (CKA_LABEL, keyName),
                new CK_ATTRIBUTE (CKA_CLASS, keyClass),
                new CK_ATTRIBUTE (CKA_THALES_CACHE_CLEAR, true)
            };

        try
        {
            /* Call C_FindObjectsFinal in case there is another find objects going on  */
            session.p11.C_FindObjectsFinal (session.sessionHandle);
            session.p11.C_FindObjectsInit (session.sessionHandle, attrs);
            long[] keyID = session.p11.C_FindObjects (session.sessionHandle, 1);
            session.p11.C_FindObjectsFinal (session.sessionHandle);
            if (keyID.length > 0)
            {
                return keyID[0];
            }
            else
            {
                /* System.out.println ("The key: " + keyName + " is not found."); */
                return 0;
            }
        }
        catch (PKCS11Exception e)
        {
            System.out.println (e.getMessage());
            e.printStackTrace();
        }
        catch (Exception e)
        {
            System.out.println ("Exception thrown.");
            System.out.println (e.getMessage());
            e.printStackTrace();
        }
        return 0;
    }

    public static String getPKCS11LibPath(String libPath)
    {
      String path = null;
      if (( libPath != null ) && (!libPath.equals("")))
      {
          path = libPath;
      }
      else
      {
    	  path = System.getenv("VPKCS11LIBPATH");
    	  
          if ((path == null) || (path.equals("")))
          {
              String osName = System.getProperty("os.name");
              if (osName.contains("Windows"))
              {
                  if (isFileExist(WinX64InstallPath))
                  {
                      path = WinX64InstallPath;
                  }else if ( isFileExist(WinX86InstallPath))
                  {
                      path = WinX86InstallPath;
                  }
              }
              else
              {
                  if (isFileExist(UnixInstallPath))
                  {
                      path = UnixInstallPath;
                  }
              }

              if ((path == null )|| (path.equals("")))
              {
                  System.out.println ("Cannot find CADP PKCS11 library, please install CADP key agent. " );
                  System.exit(4);
              }
          }
          else
          {
              if ( isFileExist(path))
              {
                  // this is okay
              }
              else
              {
                  System.out.println ("VPKCS11LIBPATH point to a file that does not exist: " + path);
                  System.exit(4);
              }
          }
      }
      System.out.println ("Loading the CADP PKCS11 library from : " + path);
      return  path;
    }

    public static void setKeyState(Vpkcs11Session session, long keyID, Helper.KeyState kstate) {

        int lkeyState = 0;

        try {
            switch(kstate) {
                case PreActive:
                    lkeyState = 0x0;
                    break;
                case Active:
                    lkeyState = 0x1;
                    break;
                case Suspended:
                    lkeyState = 0x2;
                    break;
                case Deactivated:
                    lkeyState = 0x3;
                    break;
                case Compromised:
                    lkeyState = 0x4;
                    break;
                case Destroyed:
                    lkeyState = 0x5;
                    break;
            }

            CK_ATTRIBUTE[] keyStateAttrs = new CK_ATTRIBUTE[] {
                    new CK_ATTRIBUTE(Helper.CKA_THALES_KEY_STATE, lkeyState),
            };

            session.p11.C_SetAttributeValue(session.sessionHandle, keyID, keyStateAttrs);

            System.out.println ("Successfully set key state to "+ lkeyState +" for key: " + keyID);
        }
        catch (PKCS11Exception e)
        {
            e.printStackTrace();
        }
    }

    public static void setKeyTransitionDates(Vpkcs11Session session, long keyID, ArrayList dateList) {

        try {
            CK_ATTRIBUTE[] attrs = {};
            CK_ATTRIBUTE[] keyDateAttrs = (CK_ATTRIBUTE[])dateList.toArray(attrs);

            session.p11.C_SetAttributeValue(session.sessionHandle, keyID, keyDateAttrs);
            System.out.println("Successfully set key transition date for key Handle: " + keyID);
        }
        catch (PKCS11Exception e)
        {
            e.printStackTrace();
        }
    }

    // compare two binary files return true if the content is equal false otherwise
    public static boolean CompareTwoFiles(String pathA, String pathB)
    {
        boolean match = false;
        FileInputStream inputStreamA = null;
        FileInputStream inputStreamB = null;
        try
        {
          int BLOCK_SIZE = 4096;
          int bytesReadA, bytesReadB;
          // assume inputStreamA and inputStreamB are streams from your two files.
          byte[] streamABlock = new byte[BLOCK_SIZE];
          byte[] streamBBlock = new byte[BLOCK_SIZE];
          inputStreamA = new FileInputStream(pathA);
          inputStreamB = new FileInputStream(pathB);

          do
          {
            bytesReadA = inputStreamA.read(streamABlock);
            bytesReadB = inputStreamB.read(streamBBlock);
            match = ((bytesReadA == bytesReadB) && Arrays.equals( streamABlock, streamBBlock));
          } while (match && (bytesReadA > -1));
        }
        catch (Exception e)
        {
            System.out.println ("Exception thrown.");
            System.out.println (e.getMessage());
        }
        finally {
        	try {
        	if(inputStreamA!=null) inputStreamA.close();
        	if(inputStreamB!=null) inputStreamB.close();
        	}
        	catch(IOException e) {}
        }

        return match;
    }

    public static long[] createKeyPair(Vpkcs11Session session, String keyName, CK_MECHANISM mechanism, int modulusBits)
    {
        long[] keyIDArr = null;
        byte[] publicExponent = { 0x01, 0x00, 0x01, 0x00 };
        String year, month, day;
        Date date = new Date();
        Calendar cal = new GregorianCalendar();
        cal.setTime(date);
        cal.add(Calendar.DATE, 30);

        year = String.valueOf(cal.get(Calendar.YEAR));
        month = String.valueOf(cal.get(Calendar.MONTH)+1); // Calendar is zero based!
        day = String.valueOf(cal.get(Calendar.DAY_OF_MONTH));

        System.out.println("Current End Date: year: "+ year+ " month: "+ month+ " day: "+day);
        //CK_DATE endDate = new CK_DATE(year.toCharArray(), month.toCharArray(), day.toCharArray());

        CK_ATTRIBUTE[] publicKeyAttr = new CK_ATTRIBUTE[]
                {
                        new CK_ATTRIBUTE (CKA_LABEL, keyName),
                        new CK_ATTRIBUTE (CKA_CLASS, CKO_PUBLIC_KEY),
                        new CK_ATTRIBUTE (CKA_ENCRYPT, true),
                        new CK_ATTRIBUTE (CKA_SIGN, true),
                        new CK_ATTRIBUTE (CKA_VERIFY, true),
                        new CK_ATTRIBUTE (CKA_WRAP, true),
                        new CK_ATTRIBUTE (CKA_TOKEN, true),
                        new CK_ATTRIBUTE (CKA_PUBLIC_EXPONENT, publicExponent),
                        new CK_ATTRIBUTE (CKA_MODULUS_BITS, modulusBits)
                };

        CK_ATTRIBUTE[] privateKeyAttr = new CK_ATTRIBUTE[]
                {
                        new CK_ATTRIBUTE (CKA_CLASS, CKO_PRIVATE_KEY),
                        new CK_ATTRIBUTE (CKA_TOKEN, true),
                        new CK_ATTRIBUTE (CKA_PRIVATE, true),
                        new CK_ATTRIBUTE (CKA_SENSITIVE, true),
                        new CK_ATTRIBUTE (CKA_DECRYPT, true),
                        new CK_ATTRIBUTE (CKA_SIGN, true),
                        new CK_ATTRIBUTE (CKA_UNWRAP, true)
                };
        try {
            keyIDArr = session.p11.C_GenerateKeyPair(session.sessionHandle, mechanism, publicKeyAttr, privateKeyAttr);
        }
        catch(PKCS11Exception pkex) {
            pkex.printStackTrace();
        }
        return keyIDArr;
    }

    public static CK_DATE parseDate(String dateStr) {
        CK_DATE date;
        String year, month, day;
        String[] dateParts = dateStr.split("[-/]", 3);

        if(dateParts[0].length()==2) {
            month = dateParts[0];
            day = dateParts[1];
            year = dateParts[2];
        }
        else if (dateParts[0].length()==4) {
            year = dateParts[0];
            month = dateParts[1];
            day = dateParts[2];
        }
        else {
            year = "1900";
            month = "1";
            day = "1";
        }

        date = new CK_DATE(year.toCharArray(), month.toCharArray(), day.toCharArray());
        return date;
    }

    public static long parseKeyName(String keyName) {

        long objClass = 0;
        if(keyName.length() > 0 && keyName.charAt(1)==':') {
            switch (keyName.charAt(0)) {
                case 'v':
                    objClass = CKO_PRIVATE_KEY;
                    break;
                case 'c':
                    objClass = CKO_PUBLIC_KEY;
                    break;
                case 'k':
                default:
                    objClass = CKO_SECRET_KEY;
                    break;
            }
        }
        return objClass;
    }

    public static long createKey(Vpkcs11Session session, String keyName, long genAction, int ls_days)
    {
        return createKey(session, keyName, genAction, ls_days, false, false);
    }

    public static long createKey(Vpkcs11Session session, String keyName, long genAction, int ls_days, boolean bAlwSens, boolean bNevExtr)
    {
        long keyID = 0;
        String year, month, day;
        /* Create an AES 256 key on the KeyManager without pass in key value */
        try {
            Date date = new Date();
            Calendar cal = new GregorianCalendar();
            cal.setTime(date);
            cal.add(Calendar.DATE, 30);

            year = String.valueOf(cal.get(Calendar.YEAR));
            month = String.valueOf(cal.get(Calendar.MONTH)+1); // Calendar is zero based!
            day = String.valueOf(cal.get(Calendar.DAY_OF_MONTH));

            System.out.println("Current End Date: year: "+ year+ " month: "+ month+ " day: "+day);
            CK_DATE endDate = new CK_DATE(year.toCharArray(), month.toCharArray(), day.toCharArray());
            CK_MECHANISM mechanism = new CK_MECHANISM (CKM_AES_KEY_GEN);

            CK_ATTRIBUTE[] attrs = new CK_ATTRIBUTE[]
                    {
                            new CK_ATTRIBUTE (CKA_LABEL, keyName),
                            new CK_ATTRIBUTE (CKA_CLASS, CKO_SECRET_KEY),
                            new CK_ATTRIBUTE (CKA_KEY_TYPE, CKK_AES),
                            new CK_ATTRIBUTE (CKA_VALUE_LEN, 32),
                            new CK_ATTRIBUTE (CKA_TOKEN, true),
                            new CK_ATTRIBUTE (CKA_ENCRYPT, true),
                            new CK_ATTRIBUTE (CKA_DECRYPT, true),
                            new CK_ATTRIBUTE (CKA_SIGN, false),
                            new CK_ATTRIBUTE (CKA_VERIFY, false),
                            new CK_ATTRIBUTE (CKA_WRAP, true),
                            new CK_ATTRIBUTE (CKA_UNWRAP, true),
                            new CK_ATTRIBUTE (CKA_ALWAYS_SENSITIVE, bAlwSens),
                            new CK_ATTRIBUTE (CKA_NEVER_EXTRACTABLE, bNevExtr),
                            new CK_ATTRIBUTE (CKA_KEY_CACHE_ON_HOST, true),
                            new CK_ATTRIBUTE (CKA_KEY_CACHED_TIME, 44640L),
                            new CK_ATTRIBUTE (CKA_END_DATE, endDate),
                            new CK_ATTRIBUTE (Helper.CKA_THALES_KEY_VERSION_ACTION, genAction),
                            new CK_ATTRIBUTE (CKA_MODIFIABLE, true)
                    };

            if(ls_days != 0){
                attrs = Arrays.copyOf(attrs, attrs.length + 1);
                attrs[attrs.length-1] = new CK_ATTRIBUTE (Helper.CKA_THALES_KEY_VERSION_LIFE_SPAN, ls_days);
            }

            System.out.println ("Before generating Key. Key Handle: " + keyID);
            keyID = session.p11.C_GenerateKey (session.sessionHandle, mechanism, attrs);
            System.out.println ("Successfully Generated key. Key Label: "+keyName+". Key Handle: " + keyID);
        }
        catch (PKCS11Exception e)
        {
            e.printStackTrace();
        }
        return keyID;
    }

    public static long createKeyObject(Vpkcs11Session session, String keyName, String appName, byte[] keyValue, boolean bAlwSens, boolean bNevExtr) {
        long keyID = 0;
        try {
            /* Create an AES 256 key on the KeyManager */

            /* AES key template.
	         * CKA_LABEL is the name of the key and will be displayed on the KeyManager
	         * CKA_VALUE is the bytes that make up the AES key.
	        */

            CK_ATTRIBUTE[] attrs = new CK_ATTRIBUTE[]
                    {
                            new CK_ATTRIBUTE(CKA_LABEL, keyName),
                            new CK_ATTRIBUTE(CKA_APPLICATION, appName),
                            new CK_ATTRIBUTE(CKA_CLASS, CKO_SECRET_KEY),
                            new CK_ATTRIBUTE(CKA_KEY_TYPE, CKK_AES),
                            new CK_ATTRIBUTE(CKA_VALUE, keyValue),
                            new CK_ATTRIBUTE(CKA_VALUE_LEN, keyValue.length),
                            new CK_ATTRIBUTE(CKA_TOKEN, true),
                            new CK_ATTRIBUTE(CKA_ENCRYPT, true),
                            new CK_ATTRIBUTE(CKA_DECRYPT, true),
                            new CK_ATTRIBUTE(CKA_SIGN, false),
                            new CK_ATTRIBUTE(CKA_VERIFY, false),
                            new CK_ATTRIBUTE(CKA_WRAP, true),
                            new CK_ATTRIBUTE(CKA_UNWRAP, true),
                            new CK_ATTRIBUTE(CKA_ALWAYS_SENSITIVE, bAlwSens),
                            new CK_ATTRIBUTE(CKA_NEVER_EXTRACTABLE, bNevExtr),
                    };

            keyID = session.p11.C_CreateObject(session.sessionHandle, attrs);
            System.out.println("Object successfully created. Object Handle: " + keyID);
        } catch (PKCS11Exception e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }
        return keyID;
    }

    public static Vpkcs11Session startUp(String libPath, String pin)
    {
        try
        {
            Vpkcs11Session session = new Vpkcs11Session();

            /* Initialization of the PKCS11 instance, open session and login */
            session.p11 = PKCS11.getInstance(libPath, "C_GetFunctionList", null, false);
            long[] slots = session.p11.C_GetSlotList (false);
            loadConstantNames();

            session.sessionHandle = session.p11.C_OpenSession (slots[0], 0,  null, null);
            System.out.println ("Session successfully opened. Handle: " + session.sessionHandle);
            session.p11.C_Login (session.sessionHandle, CKU_USER, pin.toCharArray());
            System.out.println ("Successfully Logged in");
        return session;
      }
      catch (PKCS11Exception e)
      {
        System.out.println (e.getMessage());
        e.printStackTrace();
      }
      catch (Exception e)
      {
        System.out.println ("Exception thrown.");
        System.out.println (e.getMessage());
      }
      return null;
    }

    public static void closeDown(Vpkcs11Session session)
    {
        /* Logout and close session */
        try
        {
            session.p11.C_Logout(session.sessionHandle);
            System.out.println ("Successfully logged out.");
            session.p11.C_CloseSession (session.sessionHandle);
            System.out.println ("Successfully closed session.");
        }
        catch (PKCS11Exception e)
        {
            System.out.println (e.getMessage());
            e.printStackTrace();
        }
        catch (Exception e)
        {
            System.out.println ("Exception thrown.");
            System.out.println (e.getMessage());
        }
    }

    static void printAttributes(CK_ATTRIBUTE[] getAttrs) {
        int i, j;
        CK_ATTRIBUTE attr;
        byte[] valArray;
        CK_DATE date ;
        Date ep_date;
        String s, year, month, day;
        StringBuilder buf;
        String typeLabel = "";
        long lTime;

        for (i = 0; i < getAttrs.length; i++) {
            attr = getAttrs[i];

            if(attr!= null && attr.pValue != null) {
                System.out.println("***** i = " + i + ", " + getAttrs[i].toString());

                try {
                    switch ((int) attr.type) {
                        case (int) CKA_CLASS:
                        case (int) CKA_KEY_TYPE:
                        case (int) CKA_MODULUS_BITS:
                        case (int) CKA_ID:
                            System.out.println("\tAttr type: " + attr.type + " Value: " + (attr.getLong() & 0xFFFFL));
                            break;

                        case (int) CKA_THALES_KEY_VERSION_LIFE_SPAN:

                            System.out.println("\tAttr type: " + attr.type + " Value: " + attr.toString());
                            j = attr.toString().indexOf('=');
                            s = attr.toString().substring(j + 1).trim();

                            j = Integer.valueOf(flip(s), 16);
                            System.out.println("CKA_THALES_KEY_VERSION_LIFE_SPAN: " + j + " days.");
                            break;
                        case (int) CKA_LABEL:
                            System.out.println("\tAttr type: " + attr.type + " Value: " + new String(attr.getCharArray()));
                            break;

                        case (int) CKA_THALES_DATE_OBJECT_CREATE:
                        case (int) CKA_THALES_KEY_DEACTIVATION_DATE:
                            System.out.println("\tAttr type: " + attr.type + " Value: " + attr.toString());

                            j = attr.toString().indexOf('=');
                            s = attr.toString().substring(j + 1).trim();

                            if (s.length() == 16) {
                                year = hexToString(s.substring(0, 8));
                                month = hexToString(s.substring(8, 12));
                                day = hexToString(s.substring(12, 16));

                                System.out.println("Year: " + year + " Month: " + month + " Day: " + day);
                                date = new CK_DATE(year.toCharArray(), month.toCharArray(), day.toCharArray());

                                if (attr.type == CKA_THALES_DATE_OBJECT_CREATE)
                                    typeLabel = "CKA_THALES_DATE_OBJECT_CREATE";
                                else if (attr.type == CKA_THALES_KEY_DEACTIVATION_DATE)
                                    typeLabel = "CKA_THALES_KEY_DEACTIVATION_DATE";

                                System.out.println(typeLabel + ": " + date.toString());
                            }
                            break;

                        case (int) CKA_THALES_CUSTOM_1:
                        case (int) CKA_THALES_CUSTOM_2:
                        case (int) CKA_THALES_CUSTOM_3:
                        case (int) CKA_THALES_CUSTOM_4:
                        case (int) CKA_THALES_CUSTOM_5:
                            valArray = attr.getByteArray();
                            buf = new StringBuilder(valArray.length);
                            for (byte b : valArray) {
                                buf.append(String.format("%c", b & 0xff));
                            }
                            System.out.println("\tAttr type: " + attr.type + " Value: " + buf.toString());
                            break;
                        case (int) CKA_THALES_DATE_OBJECT_CREATE_EL:
                        case (int) CKA_THALES_DATE_KEY_DEACTIVATION_EL:
                            valArray = attr.getByteArray();
                            lTime = bytesToLongRev(valArray);
                            System.out.println("\tAttr type: " + attr.type + " Value: " + lTime);

                            if (attr.type == CKA_THALES_DATE_OBJECT_CREATE_EL)
                                typeLabel = "CKA_THALES_DATE_OBJECT_CREATE_EL";
                            else if (attr.type == CKA_THALES_DATE_KEY_DEACTIVATION_EL)
                                typeLabel = "CKA_THALES_KEY_DEACTIVATION_DATE_EL";

                            ep_date = new Date(lTime * 1000);
                            System.out.println(typeLabel + ": " + ep_date.toString());
                            break;
                        default:
                            System.out.println("\tAttr type: " + attr.type + " Value: " + attr.toString());
                            break;
                    }
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        }
    }

    public static long bytesToLongRev(byte[] b) {
        long result = 0;
        for (int i = 0; i < b.length; i++) {
            result <<= 8;
            result |= (b[b.length-1-i] & 0xFF);
        }
        return result;
    }

    public static String flip(final String hex){
        final StringBuilder builder = new StringBuilder(hex.length());
        for(int i = hex.length(); i > 1; i-=2)
            builder.append(hex.substring(i-2, i));
        return builder.toString();
    }

    public static String hexToString(String hex){

        StringBuilder sb = new StringBuilder();

        for( int i=0; i<hex.length()-1; i+=2 ){
            String output = hex.substring(i, (i + 2));
            //convert hex to decimal
            int decimal = Integer.parseInt(output, 16);
            //convert the decimal to character
            sb.append((char)decimal);
        }
        return sb.toString();
    }

    public static String getConstantName(long constVal) {
        if (PKCS11ConstantNames == null) {
            loadConstantNames();
        }
        return PKCS11ConstantNames.get(constVal);
    }

    public static void loadConstantNames() {
        Map<Long, String> cNames = new HashMap<Long, String>();
        String fieldName;

        for (Field field : PKCS11Constants.class.getDeclaredFields()) {
            // ((field.getModifiers() & (Modifier.FINAL | Modifier.STATIC)) != 0)
            fieldName = field.getName();
            if (long.class == field.getType() && fieldName.startsWith("CKA")) {
                try {
                    // only record final static int fields
                cNames.put(Long.parseLong(field.get(null).toString()), fieldName);
                // System.out.println("Putting: "+fieldName+" with "+field.get(null));
            } catch(IllegalAccessException iae)
            {
                System.out.println(iae.getMessage());
            }
            }
        }
        PKCS11ConstantNames = cNames;
    }
}
