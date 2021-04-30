package com.thales.cm.rest.cmaws;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Calendar;
import java.util.Date;

import com.thales.cm.rest.cmhelper.CipherTrustManagerHelper;

public class AWSMysqlRDSandCipherTrustREST {

	CipherTrustManagerHelper ctmh = null;

	public static void main(String[] args) throws Exception {

		AWSMysqlRDSandCipherTrustREST awsresrest = new AWSMysqlRDSandCipherTrustREST();
		awsresrest.ctmh = new CipherTrustManagerHelper();

		if (args.length != 4) {
			System.err.println("Usage: java AWSMysqlRDSandCipherTrustREST userid password keyname ctmip  ");
			System.exit(-1);
		}

		awsresrest.ctmh.username = args[0];
		awsresrest.ctmh.password = args[1];
		awsresrest.ctmh.cmipaddress = args[3];
		awsresrest.ctmh.dataformat = "alphanumeric";
		try {
			String tkn = awsresrest.ctmh.getToken();

			awsresrest.ctmh.key = args[2];

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		Calendar calendar = Calendar.getInstance();
		Date startDate = calendar.getTime();

		Connection connection = ConnectionObjectRDS.getConnection();
		connection.setAutoCommit(false);

		awsresrest.fpeencryptdata(connection);
		awsresrest.fpedecryptdata(connection);

		if (connection != null)
			connection.close();

		Calendar calendar2 = Calendar.getInstance();

		// Get start time (this needs to be a global variable).
		Date endDate = calendar2.getTime();
		long sumDate = endDate.getTime() - startDate.getTime();
		System.out.println("Total time " + sumDate);
	}

	void fpeencryptdata(Connection connection) throws Exception {

		String SQL = "insert into person values (?,?,?,?)";
		int batchSize = 2;
		int count = 0;
		int[] result;

		PreparedStatement pstmt = connection.prepareStatement(SQL);
		String results = null;
		String sensitive = null;
		for (int i = 1; i <= 10; i++) {
			sensitive = "bobjones" + i + "@something.com";
			System.out.println(sensitive);
			results = this.ctmh.cmRESTProtect("fpe", sensitive, "encrypt");
			pstmt.setString(1, results);
			sensitive = i + " Anystreet Rd., Anytown, USA";
			System.out.println(sensitive);
			results = this.ctmh.cmRESTProtect("fpe", sensitive, "encrypt");
			pstmt.setString(2, results);
			pstmt.setInt(3, i);
			pstmt.setInt(4, i + i);
			pstmt.addBatch();

			count++;

			if (count % batchSize == 0) {
				System.out.println("Commit the batch");
				result = pstmt.executeBatch();
				System.out.println("Number of rows inserted: " + result.length);
				connection.commit();
			}
		}

		if (pstmt != null)
			pstmt.close();

	}

	void fpedecryptdata(Connection connection) throws Exception {

		Statement stmt = null;
		try {
			stmt = connection.createStatement();
			String results;

			String sql = "SELECT email, address, age, category FROM person";
			ResultSet rs = stmt.executeQuery(sql);

			while (rs.next()) {
				// Retrieve by column name

				String email = rs.getString("email");
				String address = rs.getString("address");
				int age = rs.getInt("age");
				int category = rs.getInt("category");
				System.out.println("Encrypted email: " + email);
				System.out.println("Encrypted address:" + address);
				results = this.ctmh.cmRESTProtect("fpe", email, "decrypt");
				System.out.println("Decrypted email: " + results);

				results = this.ctmh.cmRESTProtect("fpe", address, "decrypt");
				System.out.println("Decrypted address:" + results);

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
