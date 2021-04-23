using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;


namespace Vormetric.Pkcs11Sample
{
    class Program
    {
        static void Usage()
        {
            Console.WriteLine("Usage: -p pin -t [0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | d] [-k|-kp keyname] [-o encryption mode] [-f input File] ");
            Console.WriteLine("[-c char set]|[-r charset file with range input]|[-l charset file with literal input] [-u utf mode])");
                Console.WriteLine("\t 0. Run all samples. ");
                Console.WriteLine("\t 1. Create key sample. ");
                Console.WriteLine("\t 2. Create key object sample. ");
                Console.WriteLine("\t 3. Find and delete the key sample. ");
                Console.WriteLine("\t 4. Encrypt and decrypt sample. ");
                Console.WriteLine("\t 5. Encrypt and decrypt with different mode (FPE) sample. ");
                Console.WriteLine("\t 6. Create a key pair and sign the message sample. ");
                Console.WriteLine("\t 7. Find and export a key from DSM sample. ");
                Console.WriteLine("\t 8. Encrypt and decrypt a file sample. ");
                Console.WriteLine("\t 9. Encrypt and decrypt a file and log meta data sample. ");
                Console.WriteLine("\t a. Test key attributes sample. ");
                Console.WriteLine("\t b. Compute message digest for the default test string. ");
                Console.WriteLine("\t c. Compute message digest for a given input file. ");
                Console.WriteLine(" Note: Please make sure to install the Vormetric Key Agent,");
                Console.WriteLine("\t or set the environment variable VPKCS11LIBPATH to the Vormetric PKCS11 library.");
                Console.WriteLine("\t e.g. for 64 bit, VPKCS11LIBPATH=\"c:\\Program Files\\Vormetric\\DataSecurityExpert\\Agent\\pkcs11\bin\\vorpkcs11.dll\".");
                Environment.Exit(-1);
        }

        public static void Main(string[] args)
        {
            if (args.Length%2 != 0)
            {
                Usage();
            }

            string optArg;
            string charSetInput = null;
            char charSetChoc = '\0';
            string utfMode = null;

            string pin = null;
            string inputFileName = null;
            string keyLabel = "vpkcs11_dotnet_sample_key";
            string opName = null;
            string testOpt = null;
            string tweakInput = null;
            bool symmetric = true;
            
            for (int i = 0; i < args.Length; i++) {

                optArg = args[i];
                if (optArg.StartsWith("-"))
                {
                    switch (optArg[1])
                    {
                        case 'p':
                            pin = args[++i];
                            break;
                        case 'k':
                            if (optArg.Length == 3 && optArg[2] == 'p')
                                symmetric = false;
                            else
                                symmetric = true;
                            keyLabel = args[++i];
                            break;                                               
                        case 'o':
                            opName = args[++i];
                            break;
                        case 'c':
                        case 'l':
                        case 'r':                        
                            charSetChoc = optArg[1];
                            charSetInput = args[++i];
                            break;
                        case 'u':
                            utfMode = args[++i];
                            break;
                        case 't':
                            testOpt = args[++i];
                            break;
                        case 'f':
                            inputFileName = args[++i];
                            break;
                        case 'w':
                            tweakInput = args[++i];
                            break;
                        default:
                            Usage();
                            break;
                    }
                }
                else {
                    Usage();
                }
            }

            if ( string.IsNullOrEmpty(pin) || string.IsNullOrEmpty(testOpt) ) 
                Usage();

            string wrappingKeyLabel = "vpkcs11_dotnet_wrapping_key";
            char[] keyValue =  {
            		't','h','i','s',' ','i','s',' ',
        	    	'm','y',' ','s','a','m','p','l',
        		    'e',' ','k','e','y',' ','d','a',
        		    't','a',' ','5','4','3','2','1' };
          
            
            ISample sample;

            switch ( testOpt[0])
            {
                case '0': // run all the samples one bye one
                    {
                        sample = new CreateKeySample();
                        sample.Run(new object[] { pin, keyLabel });
                        sample.Run(new object[] { pin, wrappingKeyLabel });

                        sample = new CreateObjectSample();
                        sample.Run(new object[] { pin, keyValue, keyLabel });

                        sample = new EncryptDecryptSample();
                        sample.Run(new object[] { pin, keyLabel });                       

                        sample = new EncryptDecryptMultiPartSample();
                        sample.Run(new object[] { pin, keyLabel, inputFileName, false });

                        sample = new EncryptDecryptMultiPartSample();
                        sample.Run(new object[] { pin, keyLabel, inputFileName, true });

                        sample = new KeypairSignSample();
                        sample.Run(new object[] { pin, keyLabel });

                        sample = new FindExportKeySample();
                        sample.Run(new object[] { pin, keyValue, keyLabel, wrappingKeyLabel });

                        sample = new FindDeleteKeySample();
                        sample.Run(new object[] { pin, keyLabel });
                        sample.Run(new object[] { pin, wrappingKeyLabel });

                        sample = new DigestSample();
                        sample.Run(new object[] { pin, "sha256" });
                        sample.Run(new object[] { pin, "sha384" });
                        sample.Run(new object[] { pin, "sha512" });

                        sample = new DigestMultiPartSample();
                        sample.Run(new object[] { pin, "sha256", inputFileName });
                        sample.Run(new object[] { pin, "sha384", inputFileName });
                        sample.Run(new object[] { pin, "sha512", inputFileName });

                        break;
                    }
                case '1': // run generate key sample
              
                    sample = new CreateKeySample();
                    sample.Run(new object[] { pin, keyLabel });
                    break;

                case '2':   // run create key object sample
              
                    sample = new CreateObjectSample();
                    sample.Run(new object[] { pin, keyValue, keyLabel });
                    break;

                case '3':       // run find and delete key sample
                    sample = new FindDeleteKeySample();
                    sample.Run(new object[] { pin, keyLabel });
                    break;

                case '4' :   // run encrypt and decrypt a short message sample with CBC_PAD mode
                    sample = new EncryptDecryptSample();
                    sample.Run(new object[] { pin, keyLabel });                    
                    break;

                case '5':   // run encrypt and decrypt a short message with different mode, FPE/FF1 mode requires inputFile and character set

                    sample = new EncryptDecryptSample();
                    sample.Run(new object[] {pin, keyLabel, opName, inputFileName, charSetChoc, charSetInput, utfMode, tweakInput});
                    break;

                case '6':   // run create a keypair and sign the message sample
                   
                    sample = new KeypairSignSample();
                    sample.Run(new object[] { pin, keyLabel });
                    break;

                case '7':   // run Find and Export Key sample
                    
                    sample = new FindExportKeySample();
                    sample.Run(new object[] { pin, keyValue, keyLabel, wrappingKeyLabel });
                    break;

                case '8':   // run Encrypt and Decrypt a file sample
                    
                    sample = new EncryptDecryptMultiPartSample();
                    sample.Run(new object[] { pin, keyLabel, inputFileName, false });
                    break;

                case '9':   // run Encrypt and Decrypt a file and log meta data sample

                    sample = new EncryptDecryptMultiPartSample();
                    sample.Run(new object[] { pin, keyLabel, inputFileName, true });
                    break;

                case 'a':
                    sample = new TestAttributesSample();
                    sample.Run(new object[] { pin, keyLabel, symmetric });
                    break;

                case 'b':
                    sample = new DigestSample();
                    sample.Run(new object[] { pin, opName });
                    break;

                case 'd':
                    sample = new DigestMultiPartSample();
                    sample.Run(new object[] { pin, opName, inputFileName });
                    break;

                default:
                    Usage();
                    break;
            }
            
        }
    }
}
