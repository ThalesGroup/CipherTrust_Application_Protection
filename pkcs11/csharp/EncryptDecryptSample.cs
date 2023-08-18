//
// EncryptDecryptSample.cs
//

using Net.Pkcs11Interop.Common;
using Net.Pkcs11Interop.HighLevelAPI;
using Net.Pkcs11Interop.HighLevelAPI.MechanismParams;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;


namespace CADP.Pkcs11Sample
{
    public class EncryptDecryptSample : ISample
    {
        const uint KeyStateDeactivated = 3;

        static void Usage()
        {
            Console.WriteLine("Usage: pin keyname [encryption_mode] [header_mode] [inputFile] ([c char_set] ");
            Console.WriteLine("|[r range_charset_file]|[l literal_charset_file]) [utf_mode] [tweak]");
            Console.WriteLine("encryption_mode: ECB, CTR, CBC, CBC_PAD, FPE/FF1, RSA, GCM");
            Console.WriteLine("header_mode: none, v1.5, v1.5base64, v2.1, v2.7");
            Console.WriteLine("utf_mode: UTF-8 UTF-16LE/BE UTF-32LE/BE");
        }

        public bool Run(object[] inputParams)
        {
            using (IPkcs11Library pkcs11Library = Settings.Factories.Pkcs11LibraryFactory.LoadPkcs11Library(Settings.Factories, Settings.Pkcs11LibraryPath, Settings.AppType))
            {
                // Find first slot with token present
                ISlot slot = Helpers.GetUsableSlot(pkcs11Library);

                // Open RW session
                using (ISession session = slot.OpenSession(SessionType.ReadWrite))
                {
                    string pin = null;
                    string keyLabel = null;

                    string opName = null;
                    string headermode = null;
                    IObjectHandle generatedKey = null;
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
                    CKM ulHeaderEnc = 0;
                    CKM ulHeaderDec = 0;
                    bool bAsymKey = false;
                    string aad = string.Empty;
                    uint tagBits = 12;

                    ICkGcmParams mechanismParams = null;
                    byte[] gcm_iv = { 0xae, 0xc6, 0x12, 0xbe, 0x7c, 0x1d, 0xdb, 0x65, 0x9a, 0x4b, 0x31, 0x5c };
                    byte[] def_aad = { 0x38, 0x59, 0xb3, 0xc9, 0xd0, 0xb4, 0x2d, 0x45, 0xc4, 0x3e, 0x8e, 0xbd, 0x4c, 0x8c, 0xbd, 0xe1 };// 0xb6, 0xeb, 0x21, 0x06 };


                    if (inputParams.Length >= 2)
                    {
                        pin = Convert.ToString(inputParams[0]);
                        keyLabel = Convert.ToString(inputParams[1]);
                    }
                    else
                    {
                        Usage();
                        return false;
                    }

                    if (inputParams.Length >= 9) tweakStr = Convert.ToString(inputParams[8]);

                    if (inputParams.Length >= 8)
                    {
                        utfmode = Convert.ToString(inputParams[7]);
                        encoding = getUTFEncoding(utfmode, out umode);
                    }

                    if (inputParams.Length >= 7)
                    {
                        // how is the character set loaded? c...from the command line  r...from a file containing ranges  l...from a file containing the character set
                        char cset = Convert.ToChar(inputParams[5]);

                        if (cset == 'c')
                        {
                            charSet = Convert.ToString(inputParams[6]);
                            Console.WriteLine("character set specified on command line: '" + charSet + "'");
                        }
                        else if (cset == 'r')
                        {
                            charsetFileName = Convert.ToString(inputParams[6]);
                            csFileEncoding = Encoding.ASCII;
                            csRangeInput = true;
                        }
                        else if (cset == 'l')
                        {
                            charsetFileName = Convert.ToString(inputParams[6]);
                            csRangeInput = false;
                        }
                        else
                        {
                            charsetFileName = Convert.ToString(inputParams[6]);
                            csRangeInput = false;
                        }
                    }

                    if (inputParams.Length >= 5)
                    {
                        inputFileName = Convert.ToString(inputParams[4]);
                    }

                    if (inputParams.Length >= 4)
                    {
                        headermode = Convert.ToString(inputParams[3]);
                        if (headermode.Equals("v1.5")) { ulHeaderEnc = CKM.CKM_THALES_V15HDR | CKM.CKM_VENDOR_DEFINED; ulHeaderDec = CKM.CKM_THALES_ALLHDR | CKM.CKM_VENDOR_DEFINED; }
                        else if (headermode.Equals("v1.5base64")) { ulHeaderEnc = CKM.CKM_THALES_V15HDR | CKM.CKM_VENDOR_DEFINED | CKM.CKM_THALES_BASE64; ulHeaderDec = CKM.CKM_THALES_ALLHDR | CKM.CKM_VENDOR_DEFINED | CKM.CKM_THALES_BASE64; }
                        else if (headermode.Equals("v2.1")) { ulHeaderEnc = CKM.CKM_THALES_V21HDR | CKM.CKM_VENDOR_DEFINED; ulHeaderDec = CKM.CKM_THALES_ALLHDR | CKM.CKM_VENDOR_DEFINED; }
                        else if (headermode.Equals("v2.7")) { ulHeaderEnc = CKM.CKM_THALES_V27HDR | CKM.CKM_VENDOR_DEFINED; ulHeaderDec = CKM.CKM_THALES_ALLHDR | CKM.CKM_VENDOR_DEFINED; }
                        else { ulHeaderEnc = ulHeaderDec = 0; }
                    }

                    if (inputParams.Length >= 3)
                    {
                        opName = Convert.ToString(inputParams[2]);
                    }
                    if(opName == "GCM")
                    {
                        tagBits = Convert.ToUInt32(inputParams[3]);
                        //calculate tag bits.
                        tagBits *= 8;
                    }

                    if (string.IsNullOrEmpty(opName))
                        opName = "CBC_PAD";

                    IObjectHandle foundSymmKey = null;
                    IObjectHandle publicKey = null;
                    IObjectHandle privateKey = null;

                    IMechanism encmechanism = null;
                    IMechanism decmechanism = null;

                    byte[] iv = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 };
                    string sourceText = "This is Unencrypted Source Text.";
                    byte[] sourceData = ConvertUtils.Utf8StringToBytes(sourceText);
                    // Login as normal user
                    session.Login(CKU.CKU_USER, pin);

                    // Prepare attribute template that defines search criteria
                    List<IObjectAttribute> objectAttributes = new List<IObjectAttribute>();

                    if (opName.Equals("RSA"))
                    {
                        bAsymKey = true;
                        publicKey = Helpers.FindKey(session, keyLabel, (uint)CKO.CKO_PUBLIC_KEY);
                        privateKey = Helpers.FindKey(session, keyLabel, (uint)CKO.CKO_PRIVATE_KEY);

                        if (publicKey == null || privateKey == null)
                        {
                            // Generate key pair
                            Helpers.GenerateKeyPair(session, out publicKey, out privateKey, keyLabel); // password has been removed
                            Console.WriteLine("Asymmetric key " + keyLabel + " generated!");
                        }
                    }
                    else
                    {
                        foundSymmKey = Helpers.FindKey(session, keyLabel);

                        if (foundSymmKey == null)
                        {
                            uint keySize = 32;

                            generatedKey = Helpers.GenerateKey(session, keyLabel, keySize);
                            if (null != generatedKey)
                            {
                                Console.WriteLine(keyLabel + " key generated!");
                                foundSymmKey = generatedKey;
                            }
                            else
                            {
                                Console.WriteLine("Fail to generate " + keyLabel + " !");
                                return false;
                            }
                        }
                    }

                    if (String.IsNullOrEmpty(inputFileName))
                    {
                        if (!opName.Equals("FPE") && !opName.Equals("FF1"))
                        {
                            Console.WriteLine("Source Text: " + sourceText);
                        }
                        else
                        {
                            Console.WriteLine("FPE/FF1 operations require an input text file.");
                            session.Logout();
                            slot.CloseSession(session);
                            return false;
                        }
                    }

                    if (opName.Equals("FPE") || opName.Equals("FF1"))
                    {
                        if (charSet != null)
                        {
                            //  String orderCharset = new string(charSet.OrderBy(c => c).Distinct().ToArray());
                            encoding = getUTFEncoding(utfmode, out umode);
                            charSetArray = encoding.GetBytes(charSet);
                            if (umode == 0) radix = (ushort)charSet.Length;
                            else Console.WriteLine("Please only specify an ASCII character set on the command line.");
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
                    byte[] encryptedData;
                    byte[] decryptedData;

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
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_THALES_FPE, niv);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_THALES_FPE, niv);
                    }
                    else if (opName.Equals("FF1"))
                    {
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

                        //Console.WriteLine("FF1 control structure has been set up, radix is " + radix);
                        //Console.WriteLine("FF1 control structure has been set up: " + BitConverter.ToString(niv));
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_THALES_FF1, niv);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_THALES_FF1, niv);
                    }

                    // Specify encryption mechanism with initialization vector as parameter
                    else if (opName.Equals("CBC_PAD"))
                    {
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CBC_PAD | ulHeaderEnc, iv);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CBC_PAD | ulHeaderDec, iv);
                    }
                    else if (opName.Equals("CBC"))
                    {
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CBC | ulHeaderEnc, iv);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CBC | ulHeaderDec, iv);
                    }
                    else if (opName.Equals("CTR"))
                    {
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CTR | ulHeaderEnc, iv);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CTR | ulHeaderDec, iv);
                    }
                    else if (opName.Equals("ECB"))
                    {
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_ECB | ulHeaderEnc);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_ECB | ulHeaderDec);
                    }
                    else if(opName.Equals("GCM"))
                    {
                        mechanismParams = session.Factories.MechanismParamsFactory.CreateCkGcmParams(gcm_iv, (uint)gcm_iv.Length * 8, def_aad, tagBits);
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_GCM, mechanismParams);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_GCM, mechanismParams);
                    }
                    else if (opName.Equals("RSA"))
                    {
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_RSA_PKCS);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_RSA_PKCS);
                    }
                    else
                    {
                        encmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CBC_PAD, iv);
                        decmechanism = session.Factories.MechanismFactory.Create(CKM.CKM_AES_CBC_PAD, iv);
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
                                    if (bAsymKey == false)
                                        encryptedData = session.Encrypt(encmechanism, foundSymmKey, sourceData);
                                    else
                                        encryptedData = session.Encrypt(encmechanism, publicKey, sourceData);

                                    esw.WriteLine(String.Format("{0}", encoding.GetString(encryptedData)));
                                    // Do something interesting with encrypted data

                                    // Decrypt data
                                    if (bAsymKey == false)
                                        decryptedData = session.Decrypt(decmechanism, foundSymmKey, encryptedData);
                                    else
                                        decryptedData = session.Decrypt(decmechanism, privateKey, encryptedData);

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
                        if (bAsymKey == false)
                            encryptedData = session.Encrypt(encmechanism, foundSymmKey, sourceData);
                        else
                            encryptedData = session.Encrypt(encmechanism, publicKey, sourceData);

                        // Do something interesting with encrypted data
                        if(opName.Equals("GCM"))
                        {
                            int taglen = (int)tagBits / 8;
                            byte[] tagData = encryptedData.Skip(encryptedData.Length - taglen).Take(taglen).ToArray();
                            byte[] encData = encryptedData.Take(encryptedData.Length - taglen).ToArray();
                            encryptedData = new byte[tagData.Length + encData.Length];
                            Buffer.BlockCopy(tagData, 0, encryptedData, 0, taglen);
                            Buffer.BlockCopy(encData, 0, encryptedData, taglen, encData.Length);
                            Console.WriteLine($"Tag Data: {ConvertUtils.BytesToHexString(tagData)}");
                        }

                        // Decrypt data
                        if (bAsymKey == false)
                            decryptedData = session.Decrypt(decmechanism, foundSymmKey, encryptedData);
                        else
                            decryptedData = session.Decrypt(decmechanism, privateKey, encryptedData);

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
                        List<IObjectAttribute> objAttributes = new List<IObjectAttribute>();
                        objAttributes.Add(session.Factories.ObjectAttributeFactory.Create(CKA.CKA_THALES_KEY_STATE, KeyStateDeactivated));
                        session.SetAttributeValue(generatedKey, objAttributes);

                        session.DestroyObject(generatedKey);
                    }

                    session.Logout();
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
