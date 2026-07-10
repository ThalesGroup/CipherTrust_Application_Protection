using System.Text;
using System;
using System.Data.SqlClient;
using System.Security.Cryptography;

namespace AlwaysEncryptedKeysUsingCsp
{
    class Create_CMK_CEK
    {
        static CngKey CreateKeyForEncryption(string keyName, string providername, int size, string algo)
        {
            CngProvider provider = new CngProvider(providername);

            CngKeyCreationParameters params1 = new CngKeyCreationParameters();
            params1.Provider = provider;
            params1.ExportPolicy = CngExportPolicies.AllowExport;
            CngPropertyCollection coll = params1.Parameters;
            CngProperty sz = new CngProperty("Length", BitConverter.GetBytes(size), CngPropertyOptions.None);
            coll.Add(sz);
            CngKey key = null;
            try
            {
                key = CngKey.Create(new CngAlgorithm(algo), keyName, params1);
            }
            catch (CryptographicException ex)
            {
                Console.WriteLine(ex.Message);
                return null;
            }
            return key;
        }

        //Opens the Key If Exist
        static CngKey OpenKeyForEncryption(string keyName, string providername)
        {
            CngProvider provider = new CngProvider(providername);
            CngKey key = null;
            try
            {
                key = CngKey.Open(keyName, provider);
            }
            catch (CryptographicException ex)
            {
                Console.WriteLine(ex.Message);
                return null;
            }
            return key;
        }

        static void Main(string[] args)
        {
            // providerName: name of the Thales CNG provider
            string providerName = "CADP Key Storage Provider";
            Console.WriteLine("Enter CMK keyName:");
            string cmkName = Console.ReadLine();

            Console.Clear();
            CngKey cmkKey = OpenKeyForEncryption(cmkName, providerName);
            if (cmkKey == null)
            {
                cmkKey = CreateKeyForEncryption(cmkName, providerName, 4096, "RSA");
                if (cmkKey == null)
                    return;
            }
            bool bAttempt = true;
            byte[] cekBytes = null;
            byte[] encdata = null;
            do
            {
                int choice = 0;
                Console.WriteLine("Select the option you wish to create CEK ");
                Console.WriteLine("0. To exit");
                Console.WriteLine("1. Bytes on Console, user need to remember the bytes:");
                Console.WriteLine("2. CEK Name, to create CEK on Key Secure");

                string ch = Console.ReadLine();
                bool res = Int32.TryParse(ch, out choice);
                if (res==true)
                {
                    //choice = 0;
                    switch (choice)
                    {
                        case 0:

                            return;
                        case 1:
                            bAttempt = false;
                            //Input the CEK Bytes 

                            Console.WriteLine("Enter the CEK bytes ");
                            String CEK_Bytes = Console.ReadLine();
                            cekBytes = Encoding.ASCII.GetBytes(CEK_Bytes);
                            encdata = Create_CEK_CMK_SQL(providerName, cmkName, cekBytes);
                            Console.WriteLine("Encrypted Bytes : {0}", ConvertBytesToHexString(encdata, true));
                            break;

                        case 2:
                            bAttempt = false;
                            //Enter the CEK name

                            Console.WriteLine("Enter CEK keyName:");
                            string cekName = Console.ReadLine();
                            CngKey cekKey = create_CEK_ByName(cekName, providerName);
                            if (cekKey != null)
                            {
                                CngKeyBlobFormat format = new CngKeyBlobFormat("RSAPUBLICBLOB");
                                try
                                {
                                    cekBytes = cekKey.Export(format);
                                }
                                catch (CryptographicException ex)
                                {
                                    Console.WriteLine(ex.Message);
                                    return;
                                }
                                encdata = Create_CEK_CMK_SQL(providerName, cmkName, cekBytes, cekName);
                                if (encdata != null)
                                {
                                    Console.WriteLine("Encrypted Bytes : {0}", ConvertBytesToHexString(encdata, true));
                                }
                            }
                            break;
                        default:
                            Console.WriteLine("Incorrect choice!");
                            break;
                    }
                }
            } while (bAttempt) ;
            }

        //Creates the Column encryption key Using Name
        static CngKey create_CEK_ByName(String cekName, String ProviderName)
        {
            CngKey cekKey = OpenKeyForEncryption(cekName, ProviderName);
            if (cekKey == null)
            {
                cekKey = CreateKeyForEncryption(cekName, ProviderName, 256, "AES");

                if (cekKey == null)
                    return null;
            }
            return cekKey;
        }

        //Encrypt the Column Encryption Key
        static byte[] Create_CEK_CMK_SQL(String providerName, String cmkName, byte[] cekBytes, String cekName = null)
        {
            byte[] encdata = null;

            #region Creating a SQL Connection with SqlConnectionColumnEncryptionSetting Enabled
            //SqlConnection _sqlconn;
            //SqlConnectionStringBuilder strbldr = new SqlConnectionStringBuilder();
            //strbldr.DataSource = "localhost";
            //strbldr.InitialCatalog = "Test";
            //strbldr.IntegratedSecurity = true;
            //// Enable Always Encrypted in the connection we will use for this demo
            ////
            //strbldr.TrustServerCertificate = true;

            //strbldr.ColumnEncryptionSetting = SqlConnectionColumnEncryptionSetting.Enabled;

            //strbldr.Encrypt = true;

            //_sqlconn = new SqlConnection(strbldr.ConnectionString);

            //_sqlconn.Open();

            #endregion
            try
            {
                SqlColumnEncryptionCngProvider sqlsngP = new SqlColumnEncryptionCngProvider();

                string mkpath = providerName + "/" + cmkName;

                encdata = sqlsngP.EncryptColumnEncryptionKey(mkpath, @"RSA_OAEP", cekBytes);

                #region For Inserting Column Master Key and Column Encryption Key in SQL
                //SqlCommand cmd = _sqlconn.CreateCommand();

                //cmd.CommandText = @"CREATE COLUMN MASTER KEY["+ cmkName + "] WITH ( KEY_STORE_PROVIDER_NAME = N'MSSQL_CNG_STORE', KEY_PATH ='" + mkpath + "')";

                //cmd.ExecuteNonQuery();

                //cmd.CommandText = @"CREATE COLUMN ENCRYPTION KEY[" + cekName + " ] WITH VALUES ( COLUMN_MASTER_KEY = ["+ cmkName + "], ALGORITHM = 'RSA_OAEP', ENCRYPTED_VALUE =" + ConvertBytesToHexString(encdata, true) + ")";

                //cmd.ExecuteNonQuery();
                #endregion
            }

            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return null;
            }
            return encdata;
        }


        /// <summary>
        /// Gets hex representation of byte array.
        /// <param name="input">input byte array</param>
        /// <param name="addLeadingZeroX">Add leading 0x</param>
        /// </summary>
        internal static string ConvertBytesToHexString(byte[] input, bool addLeadingZeroX = false)
        {
            StringBuilder str = new StringBuilder();
            if (addLeadingZeroX)
            {
                str.Append(@"0x");
            }
            foreach (byte b in input)
            {
                str.AppendFormat(b.ToString(@"X2"));
            }
            return str.ToString();
        }
    }
}