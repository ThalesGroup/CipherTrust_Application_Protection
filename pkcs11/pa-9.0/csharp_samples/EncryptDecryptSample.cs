using System;
using System.Collections.Generic;
using System.Collections;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using System.IO;

namespace Vormetric.Pkcs11Sample
{
    public class EncryptDecryptSample: ISample
    {
        static void Usage()
        {
            Console.WriteLine("Usage: -p pin -k keyname [-o encryption_mode] [-f inputFile] ([-c char set] ");
            Console.WriteLine("|[-r range charset file]|[-l literal charset file]) [-u utf mode (UTF-8 UTF-16LE/BE UTF-32LE/BE)]");
            Console.WriteLine("Operation mode supported: ECB, CTR, CBC, CBC_PAD, FPE");
        }

        public bool Run(object[] inputParams)
        {
            using (Pkcs11 pkcs11 = new Pkcs11(Settings.Pkcs11LibraryPath, false))
            {
                // Find first slot with token present
                Slot slot = Helpers.GetUsableSlot(pkcs11);                

                // Open RW session
                using (Session session = slot.OpenSession(false))
                {
                    string pin = Convert.ToString(inputParams[0]);
                    string keyLabel = Convert.ToString(inputParams[1]);

                    string opName = null;
                    ObjectHandle generatedKey = null;
                    string inputFileName = null;
                    string encryptedFileName = "encrypted.txt";
                    string decryptedFileName = "decrypted.txt";

                    string charSet = null;
                    byte[] charSetArray = null;
                    string charsetFileName = null;
                    string tweakStr = null;
                    Encoding encoding = null;
                    string utfmode = "ASCII";
                    byte umode = 0;
                    ushort radix = 0;
                    Encoding csFileEncoding = null;
                    bool csRangeInput = false;

                    if (inputParams.Length >= 3)
                    {
                        opName = Convert.ToString(inputParams[2]);

                        if (inputParams.Length >= 7)
                        {
                            inputFileName = Convert.ToString(inputParams[3]);
                            char cset = Convert.ToChar(inputParams[4]);

                            if (cset == 'c')
                                charSet = Convert.ToString(inputParams[5]);
                            else if (cset == 'r')
                            {
                                charsetFileName = Convert.ToString(inputParams[5]);
                                csFileEncoding = Encoding.ASCII;
                                csRangeInput = true;
                                utfmode = Convert.ToString(inputParams[6]);
                            }
                            else if (cset == 'l')
                            {
                                charsetFileName = Convert.ToString(inputParams[5]);
                                csRangeInput = false;
                                utfmode = Convert.ToString(inputParams[6]);
                            }
                            else
                            {
                                charsetFileName = Convert.ToString(inputParams[5]);
                                csRangeInput = false;
                                utfmode = Convert.ToString(inputParams[6]);
                                encoding = getUTFEncoding(utfmode, out umode);
                            }

                            if (inputParams.Length == 8)
                                tweakStr = Convert.ToString(inputParams[7]);
                        }
                        else
                        {
                            Usage();
                            return false;
                        }

                        if (String.IsNullOrEmpty(opName))
                        {
                            Usage();
                            return false;
                        }
                    }
                    else
                    {
                        Console.WriteLine("Default Encrypt/Decrypt Sample Test, AES_CBC_PAD mode selected.");
                        opName = "CBC_PAD";
                    }
                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    // Prepare attribute template that defines search criteria
                    List<ObjectAttribute> objectAttributes = new List<ObjectAttribute>();
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_CLASS, (uint)CKO.CKO_SECRET_KEY));
                    objectAttributes.Add(new ObjectAttribute(CKA.CKA_LABEL, keyLabel));

                    // Initialize searching
                    session.FindObjectsInit(objectAttributes);

                    // Get search results
                    List<ObjectHandle> foundObjects = session.FindObjects(1);
                    ObjectHandle foundKey = null;
                    Mechanism mechanism = null;

                    // Terminate searching
                    session.FindObjectsFinal();

                    if (foundObjects.Count < 1)
                    {
                        uint keySize = 32;
                        generatedKey = Helpers.GenerateKey(session, keyLabel, keySize);
                        if (null != generatedKey)
                        {
                            Console.WriteLine(keyLabel + " key generated!");
                            foundKey = generatedKey;
                        }
                        else
                        {
                            Console.WriteLine("Fail to generate " + keyLabel + " !");
                            return false;
                        }
                    }
                    else
                    {
                        foundKey = foundObjects[0];
                    }

                    byte[] iv = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A,
                             0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 };
                    string sourceText = "This is Unencrypted Source Text.";
                    byte[] sourceData = ConvertUtils.Utf8StringToBytes(sourceText);

                    if (String.IsNullOrEmpty(inputFileName))
                    {
                        if (!opName.Equals("FPE") && !opName.Equals("FF1"))
                        {
                            Console.WriteLine("Source Text: " + sourceText);
                        }
                        else
                        {
                            Console.WriteLine("FPE/FF1 operation need input text file.");
                            session.Logout();
                            slot.CloseSession(session);
                            return false;
                        }
                    }                    

                    if (opName.Equals("FPE") || opName.Equals("FF1"))
                    {
                        if (charSet != null) /* -c option, assume ASCCI encoding */
                        {
                            //  String orderCharset = new string(charSet.OrderBy(c => c).Distinct().ToArray());
                            encoding = getUTFEncoding(utfmode, out umode);
                            charSetArray = encoding.GetBytes(charSet);
                            radix = Convert.ToUInt16(charSetArray.Length);
                        }
                        else if (charsetFileName == null)
                        {
                            Console.WriteLine("No character set or charset input file specified.");
                            Usage();
                            return false;
                        }
                        else
                        {
                            FileStream csfs = new System.IO.FileStream(charsetFileName, FileMode.Open, FileAccess.Read);
                            String content;
                            StreamReader sr;

                            if (csRangeInput == true)
                            {
                                sr = new StreamReader(csfs, Encoding.ASCII);
                            }
                            else
                            {
                                sr = new StreamReader(csfs, true);
                            }

                            content = sr.ReadToEnd();
                            encoding = getUTFEncoding(utfmode, out umode);

                            // if (content.Any(x => delimiters.Contains(x)))
                            if (csRangeInput == true)
                            {
                                String[] ranges = content.Split(',');
                                ArrayList charSetList = new ArrayList();
                                Int32 cp, cp_end, i;

                                string s;
                                try
                                {
                                    foreach (String r in ranges)
                                    {
                                        String pattern = @"([\dA-F]{1,4})(\s)*\-(\s)*([\dA-F]{1,4})";

                                        if (Regex.IsMatch(r, pattern))
                                        {
                                            Match m = Regex.Match(r, pattern);
                                            {
                                                cp = Int32.Parse(m.Groups[1].Value, System.Globalization.NumberStyles.HexNumber);

                                                cp_end = Int32.Parse(m.Groups[4].Value, System.Globalization.NumberStyles.HexNumber);

                                                for (i = cp; i <= cp_end; i++)
                                                {
                                                    try
                                                    {
                                                        s = Char.ConvertFromUtf32(i);
                                                        charSetList.AddRange(encoding.GetBytes(s));
                                                        radix++;
                                                    }
                                                    catch
                                                    {
                                                    }
                                                }
                                            }
                                        }
                                        else
                                        {
                                            try
                                            {
                                                i = Int32.Parse(r.Trim(), System.Globalization.NumberStyles.HexNumber);
                                                s = Char.ConvertFromUtf32(i);
                                                charSetList.AddRange(encoding.GetBytes(s));
                                                radix++;
                                            }
                                            catch (Exception ex)
                                            {
                                                Console.WriteLine(ex.Message);
                                            }
                                        }

                                    }
                                    charSetArray = charSetList.OfType<byte>().ToArray();
                                }
                                catch (Exception aex)
                                {
                                    Console.WriteLine(aex.StackTrace);
                                }
                            }
                            else
                            {
                                charSet = content.Trim(new char[] { '\n', '\r' });
                                radix = (ushort)charSet.Length;
                                charSetArray = encoding.GetBytes(charSet);
                            }
                        }
                    }

                    byte[] bytes;
                    byte[] niv;

                    if (opName.Equals("FPE"))
                    {
                        byte[] tweak = { 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00 };
                        if (encoding == Encoding.ASCII)
                        {
                            charSetArray = encoding.GetBytes(charSet);
                            niv = new byte[tweak.Length + charSetArray.Length + 1];
                            byte byteRadixLen = Convert.ToByte(charSetArray.Length);

                            System.Buffer.BlockCopy(tweak, 0, niv, 0, tweak.Length);
                            niv[tweak.Length] = byteRadixLen;
                            System.Buffer.BlockCopy(charSetArray, 0, niv, tweak.Length + 1, charSetArray.Length);
                        }
                        else
                        {
                            niv = new byte[tweak.Length + charSetArray.Length + 8];
                            System.Buffer.BlockCopy(tweak, 0, niv, 0, tweak.Length);
                            niv[tweak.Length] = 1;
                            niv[tweak.Length + 1] = umode;
                            bytes = BitConverter.GetBytes(radix);
                            if (BitConverter.IsLittleEndian)
                                Array.Reverse(bytes);

                            System.Buffer.BlockCopy(bytes, 0, niv, tweak.Length + 2, 2);

                            bytes = BitConverter.GetBytes(charSetArray.Length);
                            if (BitConverter.IsLittleEndian)
                                Array.Reverse(bytes);

                            System.Buffer.BlockCopy(bytes, 0, niv, tweak.Length + 4, 4);
                            System.Buffer.BlockCopy(charSetArray, 0, niv, tweak.Length + 8, charSetArray.Length);
                        }
                        mechanism = new Mechanism(CKM.CKM_THALES_FPE, niv);
                    }
                    else if (opName.Equals("FF1")) {
                        byte[] tweak = encoding.GetBytes(tweakStr);
                        niv = new byte[tweak.Length + charSetArray.Length + 11];

                        bytes = BitConverter.GetBytes(charSetArray.Length);
                        if (BitConverter.IsLittleEndian)
                            Array.Reverse(bytes);
                        System.Buffer.BlockCopy(bytes, 0, niv, 0, 4);

                        bytes = BitConverter.GetBytes(tweak.Length);
                        if (BitConverter.IsLittleEndian)
                            Array.Reverse(bytes);
                        System.Buffer.BlockCopy(bytes, 0, niv, 4, 4);

                        bytes = BitConverter.GetBytes(radix);
                        if (BitConverter.IsLittleEndian)
                            Array.Reverse(bytes);
                        System.Buffer.BlockCopy(bytes, 0, niv, 8, 2);

                        niv[10] = umode;

                        System.Buffer.BlockCopy(charSetArray, 0, niv, 11, charSetArray.Length);
                        System.Buffer.BlockCopy(tweak, 0, niv, charSetArray.Length + 11, tweak.Length);

                        mechanism = new Mechanism(CKM.CKM_THALES_FF1, niv);
                    }
                    // Specify encryption mechanism with initialization vector as parameter
                    else if (opName.Equals("CBC_PAD"))
                    {
                        mechanism = new Mechanism(CKM.CKM_AES_CBC_PAD, iv);
                    }
                    else if (opName.Equals("CBC"))
                    {
                        mechanism = new Mechanism(CKM.CKM_AES_CBC, iv);
                    }
                    else if (opName.Equals("CTR"))
                    {
                        mechanism = new Mechanism(CKM.CKM_AES_CTR, iv);
                    }
                    else if (opName.Equals("ECB"))
                    {
                        mechanism = new Mechanism(CKM.CKM_AES_ECB);
                    }
                    else
                    {
                        mechanism = new Mechanism(CKM.CKM_AES_CBC_PAD, iv);
                    }

                    if (!String.IsNullOrEmpty(inputFileName))
                    {
                        FileStream fs = new System.IO.FileStream(inputFileName, FileMode.Open, FileAccess.Read);
                        FileStream efs = new System.IO.FileStream(encryptedFileName, FileMode.Create, FileAccess.Write);
                        FileStream dfs = new System.IO.FileStream(decryptedFileName, FileMode.Create, FileAccess.Write);
                        StreamReader sr;
                        StreamWriter esw;
                        StreamWriter dsw;

                        if (encoding == null)
                        {
                            encoding = Encoding.ASCII;
                        }

                        sr = new StreamReader(fs, encoding, true);
                        esw = new StreamWriter(efs, Encoding.Unicode);
                        dsw = new StreamWriter(dfs, encoding);

                        esw.AutoFlush = true;
                        dsw.AutoFlush = true;
                        String line;
                        int skipLineCount, unmatchLineCount;
                        skipLineCount = unmatchLineCount = 0;

                        while (!sr.EndOfStream)
                        {
                            line = sr.ReadLine();

                            sourceData = encoding.GetBytes(line.Trim(new char[] { '\n', '\r' }));

                            if (sourceData.Length <= 1 && opName.Equals("FPE"))
                            {
                                Console.WriteLine("Fpe mode only supports input length >= 2.");
                                skipLineCount++;
                                dsw.WriteLine(string.Format("{0}", encoding.GetString(sourceData)));
                                continue;
                            }

                            if (sourceData.Length > 0)
                            {
                                try
                                {
                                    // Encrypt data 
                                    byte[] encryptedData = session.Encrypt(mechanism, foundKey, sourceData);

                                    esw.WriteLine(String.Format("{0}", encoding.GetString(encryptedData)));
                                    // Do something interesting with encrypted data

                                    // Decrypt data
                                    byte[] decryptedData = session.Decrypt(mechanism, foundKey, encryptedData);

                                    // Do something interesting with decrypted data
                                    if (Convert.ToBase64String(sourceData, 0, sourceData.Length) == Convert.ToBase64String(decryptedData, 0, sourceData.Length))
                                    {
                                        Console.WriteLine("Source Text and Decrypted data match!!");
                                        dsw.WriteLine(string.Format("{0}", encoding.GetString(decryptedData)));

                                    }
                                    else
                                    {
                                        Console.WriteLine("Source Text: \t" + line);
                                        Console.WriteLine("Decrypted Text: " + ConvertUtils.BytesToUtf8String(decryptedData));
                                        Console.WriteLine("!!!Source and decrypted data Do Not match!!!");
                                        unmatchLineCount++;
                                    }
                                }
                                catch (Pkcs11Exception pkex)
                                {
                                    Console.WriteLine(pkex.Message);
                                }
                                catch (Exception ex)
                                {
                                    Console.WriteLine(ex.StackTrace);
                                }
                            }
                        }

                        efs.Close();
                        dfs.Close();

                        Console.WriteLine("Skipped Count: " + skipLineCount);
                        Console.WriteLine("Unmatched Count: " + unmatchLineCount);
                    }
                    else
                    {
                        Console.WriteLine("Source Text: \t" + sourceText);
                        // Encrypt data 
                        byte[] encryptedData = session.Encrypt(mechanism, foundKey, sourceData);

                        // Do something interesting with encrypted data

                        // Decrypt data
                        byte[] decryptedData = session.Decrypt(mechanism, foundKey, encryptedData);

                        Console.WriteLine("Decrypted Text: " + ConvertUtils.BytesToUtf8String(decryptedData));

                        // Do something interesting with decrypted data
                        if (Convert.ToBase64String(sourceData, 0, sourceData.Length) == Convert.ToBase64String(decryptedData, 0, sourceData.Length))
                        {
                            Console.WriteLine("Source and decrypted data match!");
                        }
                        else
                        {
                            Console.WriteLine("!!!Source and decrypted data Do Not match!!!");
                        }
                    }

                    if (null != generatedKey)
                    {
                        session.DestroyObject(generatedKey);
                    }
                    session.Logout();

                    slot.CloseSession(session);
                }
            }
            return true;
        }

        Encoding getUTFEncoding(string utfmode, out byte umode)
        {
            if (utfmode.Equals("ASCII"))
            {
                umode = 0;
                return Encoding.ASCII;
            }
            else if (utfmode.Equals("UTF-8"))
            {
                umode = 1;
                return Encoding.UTF8;
            }
            else if (utfmode.Equals("UTF-16LE"))
            {
                umode = 2;
                return Encoding.Unicode;
            }
            else if (utfmode.Equals("UTF-16"))
            {
                umode = 3;
                return Encoding.BigEndianUnicode;
            }
            else if (utfmode.Equals("UTF-32LE"))
            {
                umode = 4;
                return Encoding.UTF32;
            }
            else if (utfmode.Equals("UTF-32"))
            {
                umode = 5;
                return new UTF32Encoding(true /*bigEndian*/, true /*byteOrderMark*/);
            }
            else if (string.IsNullOrEmpty(utfmode))
            {
                umode = 0;
                return Encoding.ASCII;
            }
            else
            {
                umode = 255;
                return Encoding.Default;
            }
        }
    }
}
