package com.thales.cm.rest.cmazure;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import com.thales.cm.rest.cmhelper.CipherTrustManagerHelper;

public class SQLAzureCipherTrustREST {

	CipherTrustManagerHelper ctmh = null;

	public static void main(String[] args) throws Exception {

		SQLAzureCipherTrustREST azurerest = new SQLAzureCipherTrustREST();
		azurerest.ctmh = new CipherTrustManagerHelper();

		if (args.length != 4) {
			System.err.println("Usage: java SQLAzureCipherTrustREST userid password keyname ctmip  ");
			System.exit(-1);
		}
		azurerest.ctmh.dataformat = "alphanumeric";
		azurerest.ctmh.username = args[0];
		azurerest.ctmh.password = args[1];
		azurerest.ctmh.cmipaddress = args[3];
		try {
			String tkn = azurerest.ctmh.getToken();

			azurerest.ctmh.key = args[2];

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		String connectionUrl = "jdbc:sqlserver://yoursqlserver.net:1433;database=yourdb;user=youruser;password=Yoursupersecret!;encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;";
		Connection connection = DriverManager.getConnection(connectionUrl);

		azurerest.fpeencryptdata(connection);
		azurerest.fpedecryptdata(connection);

	}

	void fpeencryptdata(Connection connection) throws Exception {

		String sensitive = null;
		
		String insertSql = "insert into creditscore values (?,?)";
		connection.setAutoCommit(true);
		PreparedStatement prepsInsertCreditInfo = connection.prepareStatement(insertSql);
		
		for (int i = 1; i <= 9; i++) {
			sensitive = i + "73-56-5628";
			String encssn = this.ctmh.cmRESTProtect("fpe", sensitive, "encrypt");

			prepsInsertCreditInfo.setString(1, encssn);
			prepsInsertCreditInfo.setInt(2, 778+i);
			boolean returnvalue = prepsInsertCreditInfo.execute();

			System.out.println("completed insert with " + returnvalue);
			
		}
	}

	void fpedecryptdata(Connection connection) throws Exception {

		Statement stmt = null;
		try {
			stmt = connection.createStatement();
			String results;

			String sql = "SELECT ssn, score FROM creditscore";
			ResultSet rs = stmt.executeQuery(sql);

			while (rs.next()) {
				// Retrieve by column name

				String ssn = rs.getString("ssn");
				int score = rs.getInt("score");
				System.out.println("Encrypted email: " + ssn);
				results = this.ctmh.cmRESTProtect("fpe", ssn, "decrypt");
				System.out.println("Decrypted ssn: " + results);

			}
			rs.close();

		} catch (SQLException se) {
			// Handle errors for JDBC
			se.printStackTrace();
		} catch (Exception e) {
			// Handle errors for Class.forName
			e.printStackTrace();
		} finally {
			// finally block used to close resources
			try {
				if (stmt != null)
					connection.close();
			} catch (SQLException se) {
			} // do nothing
			try {
				if (connection != null)
					connection.close();
			} catch (SQLException se) {
				se.printStackTrace();
			} // end finally try
		} // end try
		System.out.println("Goodbye!");

	}
}