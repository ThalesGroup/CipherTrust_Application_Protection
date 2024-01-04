using CADP.NetCore.Crypto;
using CADP.NetCore.KeyManagement;
using CADP.NetCore.Sessions;
using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Linq;

/// <summary>
/// This sample shows how to use multiple threads that share the same session and perform mac operations.
/// </summary>
public class MyThread
{
    String m_name;
    byte[] m_data;
    NaeHmacKey m_key;
    NaeSession m_session;
    public MyThread(String name, NaeHmacKey key, byte[] data, NaeSession session)
    {
        m_name = name;
        m_key = key;
        m_data = data;
        m_session = session;
    }
    public void MyThreadProc()
    {
        string algo_name = m_key.CryptoAlgName;
        HmacAlgo algoEnum = HmacAlgo.HmacSHA1;
        if (algo_name == "HmacSHA1")
        {
            algoEnum = HmacAlgo.HmacSHA1;
        }
        else if (algo_name == "HmacSHA256")
        {
            algoEnum = HmacAlgo.HmacSHA256;
        }
        else if (algo_name == "HmacSHA384")
        {
            algoEnum = HmacAlgo.HmacSHA384;
        }
        else
        {
            algoEnum = HmacAlgo.HmacSHA512;
        }
       
        try
        {
            NaeHmacKey hmacKey = new NaeHmacKey(m_session, algoEnum, m_key.KeyName);

            Console.WriteLine($"Starting {m_name}");
            byte[] outBytes_compute_hash = null;

            outBytes_compute_hash = hmacKey.ComputeHash(m_data);
            Console.WriteLine($"Mac Data {outBytes_compute_hash.Length} bytes (B64 encoded): {Convert.ToBase64String(outBytes_compute_hash)}");


            byte[] outBytes_mac = null;
            int inputOffset;

            NaeHmacKey hmacKey1 = new NaeHmacKey(m_session, algoEnum, m_key.KeyName);
            CryptoStream cryptoStream = new CryptoStream(Stream.Null, (NaeHmacKey)hmacKey1,
                                    CryptoStreamMode.Write);
            for (inputOffset = 0; inputOffset < m_data.Length; inputOffset += 3000)
            {
                if ((m_data.Length - inputOffset) < 3000)
                    cryptoStream.Write(m_data, inputOffset, m_data.Length - inputOffset);
                else
                    cryptoStream.Write(m_data, inputOffset, 3000);
            }

            cryptoStream.Close();

            outBytes_mac = hmacKey1.Hash;

            Console.WriteLine($"Re-calculated MAC value (B64 encoded) of input: {Convert.ToBase64String(outBytes_mac)}");

            bool ans = true;
            if (outBytes_compute_hash.Length != outBytes_mac.Length)
            {
                ans = false;
            }
            if (ans == true)
            {
                for (int i = 0; i < outBytes_mac.Length; i++)
                {
                    if (outBytes_mac[i] != outBytes_compute_hash[i])
                    {
                        ans = false;
                        break;
                    }
                }
            }
            Console.WriteLine($"Answer is {ans}");
            Console.WriteLine($"Finishing {m_name}");

        }
        catch (Exception e)
        {
            Console.WriteLine($"Error occured: {e.Message}");
        }

        
    }
}
class CryptoMultiThreadedHmac
{
    static void Main(string[] args)
    {
		NaeHmacKey key = null;
        /*Read Username and password*/
        Console.Write("Enter username: ");
        string user = Console.ReadLine();
        Console.Write("Enter password: ");
        string pass = string.Empty;
        ConsoleKeyInfo consoleKeyInfo;

        do
        {
            consoleKeyInfo = Console.ReadKey(true);

            // Handle backspace and remove the key.
            if (consoleKeyInfo.Key == ConsoleKey.Backspace)
            {
                Console.Write("\b \b");
                pass = (pass.Length > 0) ? pass.Remove(pass.Length - 1, 1) : pass;
            }
            else
            {
                // Not adding the function keys, other keys having key char as '\0' in the password string.
                if (consoleKeyInfo.KeyChar != '\0')
                {
                    pass += consoleKeyInfo.KeyChar;
                    Console.Write("*");
                }
            }
        }
        // Stops Receving Keys Once Enter is Pressed
        while (consoleKeyInfo.Key != ConsoleKey.Enter);

        // cleaning up the newline character
        pass = pass.Replace("\r", "");
        Console.WriteLine();

        /*Read the CADP.NETCore_Properties.xml from the nuget folder.
            In case, of multiple versions available it will take the latest one.
            Please update the code in case of below requirement:
            1. latest version is not required to be picked.
            2. custom location for the file
        */
        var propertyFilePath = string.Empty;
        string path = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        var cadpPackage = Path.Combine(path, ".nuget", "packages", "ciphertrust.cadp.netcore");
        var highestPackage = Directory.GetDirectories(cadpPackage).Select(x => Path.GetFileName(x)).OrderBy(x => Path.GetFileName(x)).Last();
        propertyFilePath = Path.Combine(cadpPackage, highestPackage, "content", "CADP.NETCore_Properties.xml");

        /* Create a new NAE Session using the username and password */
        NaeSession session = new NaeSession(user, pass, propertyFilePath);
        Console.WriteLine("NaeSession created successfully.");

        NaeKeyManagement nkm = new NaeKeyManagement(session);
        Console.WriteLine("Enter the keyname :");
        string keyname = Console.ReadLine();

        // Gets or Generate the key.
        key = GetOrGenerateKey(nkm, session, keyname);

        // If key is null, return. Else proceed with further steps.
        if (key == null)
        {
            return;
        }
        /*Read the input data form console*/
        byte[] inputBytes;
        Console.WriteLine("Please enter the input text");
        string input = Console.ReadLine();

        if (string.IsNullOrEmpty(input))
        {
            Console.WriteLine("Please enter a valid input");
            return;
        }
        UTF8Encoding utf8 = new UTF8Encoding();
        inputBytes = utf8.GetBytes(input);
        System.IO.MemoryStream memstr = new System.IO.MemoryStream();



        MyThread mt1, mt2, mt3;


        mt1 = new MyThread("thread (1)", key, inputBytes, session);
        mt2 = new MyThread("thread (2)", key, inputBytes, session);
        mt3 = new MyThread("thread (3)", key, inputBytes, session);

        ThreadStart ts1, ts2, ts3;

        ts1 = new ThreadStart(mt1.MyThreadProc);
        ts2 = new ThreadStart(mt2.MyThreadProc);
        ts3 = new ThreadStart(mt3.MyThreadProc);

        Thread t1, t2, t3;
        t1 = new Thread(ts1);
        t2 = new Thread(ts2);
        t3 = new Thread(ts3);
        t1.Start();
        t2.Start();
        t3.Start();

        t1.Join();
        t2.Join();
        t3.Join();

    }

    /// <summary>
    /// Gets the keyname if exists, else generate it.
    /// </summary>
    /// <param name="naeKeyManagement">nae Key Management</param>
    /// <param name="session">session</param>
    /// <param name="keyName">keyName to be generated.</param>
    /// <returns>The Key Object.</returns>
    private static NaeHmacKey GetOrGenerateKey(NaeKeyManagement naeKeyManagement, NaeSession session, string keyName)
    {
        NaeHmacKey naeHmacKey = null;

        //Other options for algorithm name are HmacSHA1, HmacSHA256, HmacSHA384 and HmacSHA512
        HmacAlgo algoEnum = HmacAlgo.HmacSHA1;
        string strAlgo = algoEnum.ToString();
        try
        {
            naeHmacKey = (NaeHmacKey)naeKeyManagement.GetKey(keyName);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error occured: {ex.Message}");
            NaeHmacKey hmacKey = new NaeHmacKey(session, algoEnum);
            hmacKey.IsDeletable = true;
            hmacKey.IsExportable = true;
            naeHmacKey = hmacKey;
            try
            {
                /* If key does not exist, try creating a new HMAC key */
                Console.WriteLine("Generating new key.");
                hmacKey.GenerateKey(keyName);
                naeHmacKey = hmacKey;

            }
            catch (Exception e)
            {
                Console.WriteLine($"Error occured: {e.Message}");
                naeHmacKey = null ;
            }
        }

        return naeHmacKey;
    }
}

