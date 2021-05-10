package com.thales.cm.rest.cmgcp;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Calendar;
import java.util.Date;
//import com.thales.cm.rest.helper.CipherTrustManagerHelper;
import com.thales.cm.rest.cmhelper.CipherTrustManagerHelper;

public class GCPBigQueryCipherTrustREST {
	
	CipherTrustManagerHelper ctmh = null;

	public static void main(String[] args) throws Exception {

		if (args.length != 8) {
			System.err
					.println("Usage: java GCPBigQueryCipherTrustREST userid password keyname numberofrecords batchsize mode operation ctmip  " );
			System.exit(-1);
		}

		int numberofrecords = Integer.parseInt(args[3]);
		int batchsize = Integer.parseInt(args[4]);
		String mode = args[5];
		String operation = args[6];


		GCPBigQueryCipherTrustREST gcprest = new GCPBigQueryCipherTrustREST();


		gcprest.ctmh =  new CipherTrustManagerHelper();
		gcprest.ctmh.dataformat = "alphanumeric";
		gcprest.ctmh.username = args[0];
		gcprest.ctmh.password = args[1];
		gcprest.ctmh.cmipaddress = args[7];
	
		try {
			String tkn = gcprest.ctmh.getToken();

			gcprest.ctmh.key =  args[2];

		}
		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		Calendar calendar = Calendar.getInstance();

		// Get start time (this needs to be a global variable).
		Date startDate = calendar.getTime();

		Connection connection = ConnectionObject.getConnection();

		if (mode.equalsIgnoreCase("fpe")) {
			if (operation.equalsIgnoreCase("both")) {
				gcprest.fpeencrypt( connection, mode, numberofrecords, batchsize);
				gcprest.fpedecryptdata( connection, mode);
			} else
				gcprest.fpeencrypt( connection, mode, numberofrecords, batchsize);
		} else {
			System.out.println("other encryption modes available");
		}

		if (connection != null)
			connection.close();

		Calendar calendar2 = Calendar.getInstance();

		// Get start time (this needs to be a global variable).
		Date endDate = calendar2.getTime();
		long sumDate = endDate.getTime() - startDate.getTime();
		System.out.println("Total time " + sumDate);
	}

	 void fpedecryptdata( Connection connection, String action)
			throws Exception {

		Statement stmt = null;
		try {
			stmt = connection.createStatement();
			String results;

			String sql = "SELECT PersonID, LastName, FirstName, Address, City FROM Persons";
			ResultSet rs = stmt.executeQuery(sql);


			while (rs.next()) {
				// Retrieve by column name

				int id = rs.getInt("PersonID");
				String last = rs.getString("LastName");
				String first = rs.getString("FirstName");
				String addr = rs.getString("Address");
				String city = rs.getString("City");
				System.out.println(", last: " + last);
				// System.out.println("data: " + results);
				System.out.println("ID: " + id);

				results = this.ctmh.cmRESTProtect( "fpe", last, "decrypt");

				System.out.println("Original Data " + results);
				System.out.println(", First: " + first);
				System.out.println(", addr: " + addr);
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

	 
	 void fpeencrypt(Connection connection, String action, int nbrofrecords,
			int batchqty) throws Exception {

		String SQL = "insert into thalesbyoedemo.Persons values (?,?,?,?,?)";

		int batchSize = batchqty;

		int count = 0;
		int[] result;
		int size = nbrofrecords;
		//simba driver comment out.
		//connection.setAutoCommit(false);
		PreparedStatement pstmt = connection.prepareStatement(SQL);
		String results = null;
		String sensitive = null;

		for (int i = 1; i <= size; i++) {

			sensitive = randomNumeric(15);

			results = this.ctmh.cmRESTProtect( "fpe", sensitive, "encrypt");

			pstmt.setInt(1, i);
			pstmt.setString(2, results);
			pstmt.setString(3, "FirstName");
			pstmt.setString(4, sensitive + " Addr");
			pstmt.setString(5, action);
			pstmt.addBatch();

			count++;

			if (count % batchSize == 0) {
				System.out.println("executeBatch the batch");
				result = pstmt.executeBatch();
				System.out.println("Number of rows inserted: " + result.length);
				//take out for simba
				//connection.commit();
			}
		}

		if (pstmt != null)
			pstmt.close();
		// if(connection!=null)
		// connection.close();

	}

	
	// private static final String ALPHA_NUMERIC_STRING =
	// "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
	private static final String ALPHA_NUMERIC_STRING = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

	public static String randomAlphaNumeric(int count) {
		StringBuilder builder = new StringBuilder();
		while (count-- != 0) {
			int character = (int) (Math.random() * ALPHA_NUMERIC_STRING.length());
			builder.append(ALPHA_NUMERIC_STRING.charAt(character));
		}
		return builder.toString();
	}

	private static final String NUMERIC_STRING = "0123456789";

	public static String randomNumeric(int count) {
		StringBuilder builder = new StringBuilder();
		while (count-- != 0) {
			int character = (int) (Math.random() * NUMERIC_STRING.length());
			builder.append(NUMERIC_STRING.charAt(character));
		}
		return builder.toString();
	}

}
