package com.vormetric.pkcs11.sample;


import com.vormetric.pkcs11.wrapper.PKCS11Exception;

/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/

/*
 ***************************************************************************
 * File: GenerateRandom.java
 ***************************************************************************
 ***************************************************************************
 * This file demonstrates the following:
 * 1. Initialization.
 * 2. Create a connection and log in.
 * 3. Seed the Random Generator and generate the random bytes.
 * 4. Clean up.
 ***************************************************************************
 */

public class GenerateRandom {



    public static void usage()
    {
        System.out.println ("usage: java [-cp CLASSPATH] com.vormetric.pkcs11.sample.GenerateRandom -p pin -d seed -z random_output_size [-m module]");
        System.out.println("-p: Username:Password of Keymanager");
        System.out.println("-d: Seed");
        System.out.println("-z: Any random output size");
        System.out.println("-m: Path of directory where dll is deployed/installed");        
        System.exit (1);
    }

    public static void main ( String[] args) throws Exception
    {
        String pin = null;
        String libPath = null;
        String seed = "";
        int outputSize = 0;
        Vpkcs11Session session = null;

        for (int i=0; i<args.length; i+=2)
        {
            if (args[i].equals("-p")) pin = args[i+1];
            else if (args[i].equals("-m")) libPath = args[i+1];
            else if (args[i].equals("-d")) seed = args[i+1];
            else if (args[i].equals("-z")) outputSize = Integer.parseInt(args[i+1]);
            else usage();
        }

        try
        {
            System.out.println ("Start GenerateRandom ..." );
            session = Helper.startUp(Helper.getPKCS11LibPath(libPath), pin);

            if (seed != null && !seed.isEmpty()) {
                byte[] seedBytes = seed.getBytes();
                session.p11.C_SeedRandom(session.sessionHandle, seedBytes);
            }
            byte[] outputBytes = new byte[outputSize];
            session.p11.C_GenerateRandom(session.sessionHandle, outputBytes);

            System.out.println("Seed\t\t: " + seed);
            System.out.println("Output Length\t: " + outputSize);
            System.out.println("Output\t\t: " + toHexString(outputBytes));

        }
        catch(PKCS11Exception pe){
            pe.printStackTrace();
            System.out.println("The Cause is " + pe.getMessage() + ".");
            throw pe;
        }
        catch (Exception e)
        {
            e.printStackTrace();
            System.out.println("The Cause is " + e.getMessage() + ".");
            throw e;
        }
        finally {
            Helper.closeDown(session);
            System.out.println ("... End GenerateRandom");
        }
    }

    /*
    final private static char[] HEX_ARRAY = "0123456789ABCDEF".toCharArray();

    private static String bytesToHex(byte[] bytes) {
        char[] hexChars = new char[bytes.length * 2];
        for ( int j = 0; j < bytes.length; j++ ) {
            int v = bytes[j] & 0xFF;
            hexChars[j * 2] = HEX_ARRAY[v >>> 4];
            hexChars[j * 2 + 1] = HEX_ARRAY[v & 0x0F];
        }
        return new String(hexChars);
    }
    */

    private static String toHexString(byte[] bytes) {
        StringBuilder buffer = new StringBuilder(bytes.length * 2);
        for(int i=0; i < bytes.length; i++){
            buffer.append(Character.toUpperCase(Character.forDigit((bytes[i] >> 4) & 0xF, 16)));
            buffer.append(Character.toUpperCase(Character.forDigit((bytes[i] & 0xF), 16)));
        }
        return buffer.toString();
    }

}
