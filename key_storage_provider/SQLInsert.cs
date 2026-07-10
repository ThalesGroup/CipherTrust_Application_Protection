using System;
using System.Collections.Generic;
using System.Data.SqlClient;


namespace AlwaysEncryptedDemo
{
    class SQLInsert
    {
        private static SqlConnection _sqlconn;
        /// <summary>
        /// Insert a row for a new row in Table_1.
        /// </summary>
        /// <param name="Name">User Name</param>
        /// <param name="Password">Password</param>
        private static void AddNewPatient(string name, string password)
        {
            SqlCommand cmd = _sqlconn.CreateCommand();
            // Use parameterized SQL to insert the data.
            cmd.CommandText = @"INSERT INTO [dbo].[Table_1] ([Name] ,[password]) VALUES (@Name, @Password);";
            SqlParameter paramSSN = new SqlParameter(@"@Name", System.Data.SqlDbType.NChar, 100, System.Data.ParameterDirection.Input, false, 0, 0, null, System.Data.DataRowVersion.Current,name);
            cmd.Parameters.Add(paramSSN);
            SqlParameter paramPassword = new SqlParameter(@"@Password", System.Data.SqlDbType.Char, 11, System.Data.ParameterDirection.Input, false, 0, 0, null, System.Data.DataRowVersion.Current, password);
            cmd.Parameters.Add(paramPassword);
            try
            {
                cmd.ExecuteNonQuery();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return;
            }
        }
        static void Main(string[] args)
        {
            SqlConnectionStringBuilder strbldr = new SqlConnectionStringBuilder();
            strbldr.DataSource = "localhost";
            strbldr.InitialCatalog = "Test";
            strbldr.IntegratedSecurity = true;
            // Enable Always Encrypted in the connection we will use for this demo
            strbldr.TrustServerCertificate = true;

            strbldr.ColumnEncryptionSetting = SqlConnectionColumnEncryptionSetting.Enabled;

            strbldr.Encrypt = true;

            _sqlconn = new SqlConnection(strbldr.ConnectionString);

            Dictionary<string, SqlColumnEncryptionKeyStoreProvider> providers =
           new Dictionary<string, SqlColumnEncryptionKeyStoreProvider>();
            providers.Add("SFNT_CNG_STORE", new SqlColumnEncryptionCngProvider());

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
                AddNewPatient("Test1", "test1234");
                AddNewPatient("Test2", "test1234");

                //To print the Contents of table_1
                cmd.CommandText = @"SELECT * from [dbo].[Table_1]";
                SqlDataReader rdr = cmd.ExecuteReader();
                while (rdr.Read())
                {
                    Console.WriteLine("Name: " + rdr[0]);
                    Console.WriteLine("Passwd: " + rdr[1]);
                }
            }
            finally
            {
                _sqlconn.Close();
            }
        }
    }
}
