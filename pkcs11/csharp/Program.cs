using Net.Pkcs11Interop.Common;
using System;


namespace CADP.Pkcs11Sample
{
    class Program
    {
        static void Usage()
        {
            Console.WriteLine("Usage: -p pin -t [0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | c | i | d ] [-k|-kp keyname] [-o encryption mode] [-TagLen length of Tag in AES/GCM] [-f input File] ");
            Console.WriteLine("[-c char set]|[-r charset file with range input]|[-l charset file with literal input] [-U utf mode] [-H headermode] [-T tweak] [-w wrappingkeyname] [-n false|true] [-m true|false]) [-I Non-unique searchable ID CKA_ID]");
            Console.WriteLine("\tChoices for the -t option:");
            Console.WriteLine("\t 0. Run all samples. ");
            Console.WriteLine("\t 1. Create key sample.                                     Parameters: -p pin -k keyname [-g gen_key_action] [-n false|true]");
            Console.WriteLine("\t 2. Create key object sample. ");
            Console.WriteLine("\t 3. Find and delete the key sample. ");
            Console.WriteLine("\t 4. Encrypt and decrypt sample. ");
            Console.WriteLine("\t 5. Encrypt and decrypt with different mode (FPE) sample. ");
            Console.WriteLine("\t 6. Create a key pair and sign the message sample. ");
            Console.WriteLine("\t 7. Find and export a key from key manager sample. ");
            Console.WriteLine("\t 8. Encrypt and decrypt a file sample. ");
            Console.WriteLine("\t 9. Encrypt and decrypt a file and log meta data sample. ");
            Console.WriteLine("\t a. Test key attributes sample.                            Parameters: -p pin -k keyname");
            Console.WriteLine("\t b. Compute message digest for the default test string. ");
            Console.WriteLine("\t c. Compute message digest for a given input file. ");
            Console.WriteLine("\t i. Unwrap and import a key into key manager sample. ");
            Console.WriteLine("\t d. Encrypt and decrypt with GCM mode sample. ");
            Console.WriteLine("");
            Console.WriteLine("\tChoices for the -o option:");
            Console.WriteLine("\t ECB ... ECB mode");
            Console.WriteLine("\t CBC ... CBC mode");
            Console.WriteLine("\t GCM ... GCM mode");
            Console.WriteLine("\t CBC_PAD ... CBC_PAD mode");
            Console.WriteLine("\t sha256  ... SHA256 mode");
            Console.WriteLine("\t sha384  ... SHA384 mode");
            Console.WriteLine("\t sha512  ... SHA512 mode");
            Console.WriteLine("\t sha256-HMAC  ... SHA256-HMAC mode");
            Console.WriteLine("\t sha384-HMAC  ... SHA384-HMAC mode");
            Console.WriteLine("\t sha512-HMAC  ... SHA512-HMAC mode");
            Console.WriteLine("");
            Console.WriteLine("\t Choices for the -O option: ");
            Console.WriteLine("\t true    ... Opaque object");
            Console.WriteLine("\t false   ... non Opaque object");
            Console.WriteLine("");
            Console.WriteLine("\t Choices for the -TagLen option: ");
            Console.WriteLine("\t 4 - 16 ... bytes taglength for GCM");
            Console.WriteLine("");
            Console.WriteLine("\tChoices for the -g option:");
            Console.WriteLine("\t 0 ... generate a versioned key");
            Console.WriteLine("\t 1 ... rotate a versioned key");
            Console.WriteLine("\t 2 ... migrate a non-versioned key to a versioned key");
            Console.WriteLine("\t 3 ... generate a non-versioned key");
            Console.WriteLine("");
            Console.WriteLine("\tChoices for the -m (metadata) option:");
            Console.WriteLine("\t false ... don't add metadata");
            Console.WriteLine("\t true  ... add metadata");
            Console.WriteLine("");
            Console.WriteLine("\tChoices for the -n option:");
            Console.WriteLine("\t false ... no-delete is not active, hence delete the key as usual");
            Console.WriteLine("\t true ... no-delete enabled, thus deletion of the key is blocked.");
            Console.WriteLine("");
            Console.WriteLine("\tChoices for the -H option:");
            Console.WriteLine("\t v1.5 ... use version 1.5 header");
            Console.WriteLine("\t v1.5base64 ... use version 1.5 header, then encode everything in the BASE64 code");
            Console.WriteLine("\t v2.1 ... use version 2.1 header");
            Console.WriteLine("\t v2.7 ... use version 2.7 header");
            Console.WriteLine("");          
            Console.WriteLine("Note: In case of success exit value is 0, otherwise -1");
            Environment.Exit(-1);
        }

        public static void Main(string[] args)
        {
            string optArg;
            string charSetInput = null;
            char charSetChoc = '\0';
            string utfMode = null;
            uint genAction = 0; // create a versioned key
            string pin = null;
            string fileName = null;
            string keyLabel = "vpkcs11_dotnet_sample_key";
            string opName = null;
            string testOpt = "0";
            string tweakInput = null;
            string headerMode = null;
            string cka_idInput = null;
            bool symmetric = true;
            bool genWrappingKey = false;
            bool nodelete = false;
            string wrappingKeyLabel = null;
            string keyFilename = "wrapped-key.dat";

            uint keyType = (uint)CKO.CKO_SECRET_KEY;
            uint wrappingKeyType = (uint)CKO.CKO_SECRET_KEY;
            uint formatType = 0;

            bool needmetadata = false;
            bool preactive = false;
            bool newkeyfile = false;
            bool bAlwSen = false;
            bool bNevExtr = false;
            string newkeyLabel = keyLabel + "_imp";
            bool bOpaqueObj = false;
            int tagLen = 12;

            for (int i = 0; i < args.Length; i++)
            {
                optArg = args[i];
                if (optArg.StartsWith("-"))
                {
                    switch (optArg[1])
                    {                      
                        case 'n':

                            if (optArg.Length > 2)
                            {
                                if (optArg[2] == 'e' || optArg[2] == 'p')
                                    bNevExtr = true;
                            }
                            else if (i + 1 < args.Length && !args[i + 1].StartsWith("-"))
                                nodelete = Convert.ToBoolean(args[++i]);
                            else
                                nodelete = true;
                            break;
                        case 'O':
                            bOpaqueObj= Convert.ToBoolean(args[++i]);
                            break;                            
                        case 'g':

                            if (i < args.Length - 1 && uint.TryParse(args[i + 1], out genAction))
                                i++;
                            else
                                genWrappingKey = true;
                            break;
                        case 'p':
                            pin = args[++i];
                            break;
                        case 'a':
                            if (optArg.Length > 2)
                            {
                                if (optArg[2] == 's')
                                    bAlwSen = true;
                            }
                            else if (i < args.Length - 1)
                                preactive = Convert.ToBoolean(args[++i]);
                            break;
                        case 'k':
                            if (optArg.Length == 3 && optArg[2] == 'p')
                                symmetric = false;
                            else
                                symmetric = true;
                            if (i < args.Length - 1)
                                keyLabel = args[++i];
                            break;

                        case 'u':
                        case 'w':
                            if (i < args.Length - 1)
                                wrappingKeyLabel = Helpers.ParseKeyClass(args[++i], ref wrappingKeyType);
                            break;
                        //Changes option "c" to "S" according to V6.4.3.4
                        case 'S':
                            keyType = (uint)CKO.CKO_PUBLIC_KEY;
                            formatType = (uint)CKA.CKA_THALES_PEM_FORMAT;
                            if (i < args.Length - 1)
                                keyLabel = args[++i];
                            break;
                        case 'v':
                            keyType = (uint)CKO.CKO_PRIVATE_KEY;
                            formatType = (uint)CKA.CKA_THALES_PEM_FORMAT;
                            if (i < args.Length - 1)
                                keyLabel = args[++i];
                            break;

                        case 'F':
                            if (i < args.Length - 1)
                                formatType = Helpers.ParseFormatType(args[++i]);
                            break;
                        case 'o':
                            if (i < args.Length - 1)
                                opName = args[++i];
                            break;
                        //Changes option "S" to "c" according to V6.4.3.4
                        case 'c':
                        case 'l':
                        case 'r':
                            charSetChoc = optArg[1];
                            if (i < args.Length - 1)
                                charSetInput = args[++i];
                            break;
                        case 'U':
                            if (i < args.Length - 1)
                                utfMode = args[++i];
                            break;
                        case 't':
                            if (i < args.Length - 1)
                                testOpt = args[++i];
                            break;
                        case 'f':
                            if (i < args.Length - 1)
                                fileName = args[++i];
                            newkeyfile = true;
                            break;
                        case 'T':
                            if(optArg == "-TagLen")
                            {
                                tagLen = Convert.ToInt32(args[++i]);
                            }
                            else if (i < args.Length - 1)
                                tweakInput = args[++i];
                            break;
                        case 'H':
                            if (i < args.Length - 1)
                                headerMode = args[++i]; // v1.5, v2.1, v2.7
                            break;
                        case 'm':
                            if (i < args.Length - 1)
                                needmetadata = Convert.ToBoolean(args[++i]); // true or false
                            break;
                        case 'I':
                            if (i < args.Length - 1)
                                cka_idInput = args[++i];
                            break;
                        case 'h':
                        default:
                            Usage();
                            break;
                    }
                }
                else
                {
                    Usage();
                }
            }

            if (string.IsNullOrEmpty(pin))
                Usage();

            char[] keyValue =  {
                 't','h','i','s',' ','i','s',' ',
                    'm','y',' ','s','a','m','p','l',
                 'e',' ','k','e','y',' ','d','a',
                    't','a',' ','5','4','3','2','1' };


            ISample sample;
            // Used to check properly execution of test case and set Environment.ExitCode
            Environment.ExitCode = 0;

            try
            {
                switch (testOpt[0])
                {
                    case '0': // run all the samples one bye one

                        if (string.IsNullOrEmpty(wrappingKeyLabel))
                            wrappingKeyLabel = "vpkcs11_dotnet_wrapping_key";

                        sample = new CreateKeySample();
                        sample.Run(new object[] { pin, keyLabel, 0, preactive, nodelete, bAlwSen, bNevExtr });
                        sample.Run(new object[] { pin, wrappingKeyLabel, 0, preactive, nodelete, bAlwSen, bNevExtr });

                        sample = new CreateObjectSample();
                        sample.Run(new object[] { pin, keyValue, keyLabel, bOpaqueObj, genAction });

                        sample = new EncryptDecryptSample();
                        sample.Run(new object[] { pin, keyLabel });

                        sample = new EncryptDecryptMultiPartSample();
                        sample.Run(new object[] { pin, keyLabel, fileName, needmetadata, headerMode });

                        sample = new KeypairSignSample();                       
                        sample.Run(new object[] { pin, keyLabel, "SHA512-HMAC", "" });
                        sample.Run(new object[] { pin, keyLabel, "SHA384-HMAC", "" });
                        sample.Run(new object[] { pin, keyLabel, "SHA256-HMAC", "" });
                        sample.Run(new object[] { pin, keyLabel, "SHA224-HMAC", "" });

                        sample = new FindExportKeySample();
                        sample.Run(new object[] { pin, keyLabel, keyType, wrappingKeyLabel, wrappingKeyType, formatType, keyFilename, genWrappingKey });

                        sample = new UnwrapImportKeySample();
                        sample.Run(new object[] { pin, newkeyLabel, keyType, wrappingKeyLabel, wrappingKeyType, formatType, keyFilename });

                        sample = new FindDeleteKeySample();
                        sample.Run(new object[] { pin, keyLabel });
                        sample.Run(new object[] { pin, wrappingKeyLabel });

                        sample = new DigestSample();
                        sample.Run(new object[] { pin, "sha256" });
                        sample.Run(new object[] { pin, "sha384" });
                        sample.Run(new object[] { pin, "sha512" });

                        sample = new DigestMultiPartSample();
                        sample.Run(new object[] { pin, "sha256", fileName });
                        sample.Run(new object[] { pin, "sha384", fileName });
                        sample.Run(new object[] { pin, "sha512", fileName });

                        break;

                    case '1':   // run generate key sample
                        sample = new CreateKeySample();
                        sample.Run(new object[] { pin, keyLabel, genAction, preactive, nodelete, bAlwSen, bNevExtr, cka_idInput });
                        break;

                    case '2':   // run create key object sample
                        sample = new CreateObjectSample();
                        sample.Run(new object[] { pin, keyValue, keyLabel, bOpaqueObj, genAction, cka_idInput });
                        break;

                    case '3':   // run find and delete key sample
                        sample = new FindDeleteKeySample();
                        sample.Run(new object[] { pin, keyLabel });
                        break;

                    case '4':   // run encrypt and decrypt a short message sample with CBC_PAD mode
                        sample = new EncryptDecryptSample();
                        sample.Run(new object[] { pin, keyLabel, opName });
                        break;

                    case '5':   // run encrypt and decrypt a short message with different mode, FPE/FF1 mode requires inputFile and character set
                        sample = new EncryptDecryptSample();
                        sample.Run(new object[] { pin, keyLabel, opName, headerMode, fileName, charSetChoc, charSetInput, utfMode, tweakInput });
                        break;
                    case 'd':   // run encrypt and decrypt a short message with GCM
                        sample = new EncryptDecryptSample();
                        sample.Run(new object[] { pin, keyLabel, opName, tagLen });
                        break;
                    case '6':   // run create a key (or key pair) and sign the message sample
                        sample = new KeypairSignSample();
                        sample.Run(new object[] { pin, keyLabel, opName, headerMode, nodelete });
                        break;

                    case '7':   // run Find and Export Key sample
                        if (newkeyfile == true)
                            keyFilename = fileName;

                        sample = new FindExportKeySample();
                        sample.Run(new object[] { pin, keyLabel, keyType, wrappingKeyLabel, wrappingKeyType, formatType, keyFilename, genWrappingKey });
                        break;

                    case '8':   // run Encrypt and Decrypt a file sample
                        sample = new EncryptDecryptMultiPartSample();
                        sample.Run(new object[] { pin, keyLabel, fileName, needmetadata, headerMode });
                        break;

                    case '9':   // run Encrypt and Decrypt a file and log meta data sample
                        sample = new EncryptDecryptMultiPartSample();
                        sample.Run(new object[] { pin, keyLabel, fileName, needmetadata, headerMode });
                        break;

                    case 'a':
                        sample = new TestAttributesSample();
                        sample.Run(new object[] { pin, keyLabel, symmetric, preactive, bAlwSen, bNevExtr });
                        break;

                    case 'b':
                        sample = new DigestSample();
                        sample.Run(new object[] { pin, opName });
                        break;

                    case 'c':
                        sample = new DigestMultiPartSample();
                        sample.Run(new object[] { pin, opName, fileName });
                        break;

                    case 'i': // run Unwrap and Import Key sample
                        if (newkeyfile == true)
                            keyFilename = fileName;

                        sample = new UnwrapImportKeySample();
                        sample.Run(new object[] { pin, keyLabel, keyType, wrappingKeyLabel, wrappingKeyType, formatType, keyFilename });
                        break;
                    default:
                        Usage();
                        break;
                }
            }
            catch (Exception ex)
            {
                // Something went wrong during the test execution
                Console.WriteLine(ex.Message);
                Console.WriteLine(ex.StackTrace);
                Environment.ExitCode = -1;
            }
        }
    }
}
