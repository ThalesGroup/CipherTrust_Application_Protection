using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.Security.Cryptography;
using System.Text;

namespace CMK_CEK_Rotation
{
    class CMK_CEK_Rotation
    {
        private static SqlConnection _sqlconn;

        /*
         * old_cmk_id: id of old master key
         * providerName: name of the safenet CNG provider
         */
        static int old_cmk_id, count;
        static string providerName = "CADP Key Storage Provider";

        static void Main(string[] args)
        {
            //name of old master key
            String old_CMKName = "ETCMK";

            //name of column encryption key associated with old master key
            String CEKName = "TTCEK";

            //name of new master key, which will now be associated with "CEKName"
            String New_CMKName = "CLRCMK";

            SqlConnectionStringBuilder strbldr = new SqlConnectionStringBuilder();
            strbldr.DataSource = "localhost";
            strbldr.InitialCatalog = "Test";
            strbldr.IntegratedSecurity = true;

            strbldr.TrustServerCertificate = true;

            strbldr.ColumnEncryptionSetting = SqlConnectionColumnEncryptionSetting.Enabled;

            strbldr.Encrypt = true;

            _sqlconn = new SqlConnection(strbldr.ConnectionString);

            // MSSQL_CNG_STORE is provider id sql server custom provider which we specify while creating master key

            /*CREATE COLUMN MASTER KEY[ETCMK]
            WITH
            (
                KEY_STORE_PROVIDER_NAME = N'MSSQL_CNG_STORE',
                KEY_PATH = N'SafeNetProtectApp Key Storage Provider/ETCMK'
            )
            GO
            */
            Dictionary<string, SqlColumnEncryptionKeyStoreProvider> providers =
                new Dictionary<string, SqlColumnEncryptionKeyStoreProvider>();
            providers.Add("MSSQL_CNG_STORE", new SqlColumnEncryptionCngProvider());

            SqlConnection.RegisterColumnEncryptionKeyStoreProviders(providers);

            try
            {
                _sqlconn.Open();
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine("Sql Connection not open", ex.Message);
                return;
            }
            catch (SqlException ex)
            {
                Console.WriteLine("Sql Connection not open", ex.Message);
                return;
            }
            try
            {
                SqlCommand cmd = _sqlconn.CreateCommand();

                cmd.CommandText = @"SELECT column_master_key_id FROM sys.column_master_keys WHERE name = '" + old_CMKName + "'";
                SqlDataReader rdr = cmd.ExecuteReader();
                while (rdr.Read())
                {
                    Console.WriteLine("Old CMK Id " + rdr[0]);
                    old_cmk_id = (int)rdr[0];
                }
                rdr.Close();

                //Check Whether the Key Can be rotated or not
                SqlCommand cmd1 = _sqlconn.CreateCommand();

                cmd1.CommandText = "SELECT count(*) AS newcount FROM sys.column_encryption_key_values WHERE column_master_key_id !=" + old_cmk_id + " AND column_encryption_key_id IN (SELECT cekv.column_encryption_key_id FROM sys.column_encryption_key_values cekv, sys.column_master_keys cmk WHERE cmk.column_master_key_id = cekv.column_master_key_id AND cmk.column_master_key_id =" + old_cmk_id + ")";

                SqlDataReader rdr1 = cmd1.ExecuteReader();

                while (rdr1.Read())
                {

                    Console.WriteLine("Old CMK Id " + rdr1["newcount"]);
                    count = (int)rdr1[0];
                }
                rdr1.Close();

                if (count != 0)
                {
                    Console.WriteLine("There are CEK values encrypted by CMK for some of the CEKs that would be affected by this rotation. Manually clean these old entries or run 'Sql-Database-Clean-Cmk_Values' to clean these values before continue.");
                    return;
                }
                //=============================================================================================================================


                //cekBytes can be input if user knows the bytes

                //in example we consider that key is present on keysecure

                //open column encryption key in  Thales provider 
                CngKey cekKey = OpenKeyForEncryption(CEKName, providerName);

                //create a blob formt
                CngKeyBlobFormat format = new CngKeyBlobFormat("RSAPUBLICBLOB");
                byte[] cekBytes = null;
                try
                {
                    // export column encryption key bytes
                    cekBytes = cekKey.Export(format);
                }
                catch (CryptographicException)
                {
                    return;
                }

                SqlColumnEncryptionCngProvider sql = new SqlColumnEncryptionCngProvider();

                string newmkpath = providerName + "/" + New_CMKName;

                //Encrypt Column encryption key with the new master key
                byte[] encdata = sql.EncryptColumnEncryptionKey(newmkpath, @"RSA_OAEP", cekBytes);

                //now CEK is encrypted with new CMK

                String alter_key = @"ALTER COLUMN ENCRYPTION KEY [" + CEKName + "] ADD VALUE ( COLUMN_MASTER_KEY = [" + New_CMKName + "],ALGORITHM = 'RSA_OAEP',ENCRYPTED_VALUE =" + ConvertBytesToHexString(encdata, true) + ")";

                cmd.CommandText = alter_key;
                cmd.ExecuteNonQuery();
            }
            finally
            {
                _sqlconn.Close();
            }
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

        //Opem the CEK key already present
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
            }
            return key;
        }
    }
}
