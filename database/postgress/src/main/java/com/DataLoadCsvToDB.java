import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Properties;


public class DataLoadCsvToDB {
	private static final String CSV_FILE_PATH = "c:\\data\\plaintext.csv";

	private static Properties properties;

	static {
		try (InputStream input = DataLoadCsvToDB.class.getClassLoader()
				.getResourceAsStream("application.properties")) {
			properties = new Properties();
			if (input == null) {
				throw new RuntimeException("Unable to find application.properties");
			}
			properties.load(input);
		} catch (Exception ex) {
			throw new RuntimeException("Error loading properties file", ex);
		}
	}

	public static void main(String[] args) throws Exception {
		try (Connection connection = DriverManager.getConnection(properties.getProperty("db.url"),
				properties.getProperty("db.username"), properties.getProperty("db.password"));
				BufferedReader br = new BufferedReader(new FileReader(CSV_FILE_PATH))) {

//			CREATE TABLE plaintext_protected (custid SMALLINT, name VARCHAR(100) , address VARCHAR(100) , city VARCHAR(100) , state VARCHAR(2) , zip VARCHAR(10) , phone VARCHAR(20) , email VARCHAR(100) , dob TIMESTAMP, creditcard BIGINT, creditcardcode SMALLINT, ssn VARCHAR(11) );

			String insertQuery = "INSERT INTO plaintext_protected (custid, name, address, city, state, zip, phone, email, dob, creditcard, creditcardcode, ssn) "
					+ "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

			PreparedStatement statement = connection.prepareStatement(insertQuery);

			String line;
			boolean headerSkipped = false;
			int cnt = 0;
			while ((line = br.readLine()) != null) {
				// Skip the header
				if (!headerSkipped) {
					headerSkipped = true;
					continue;
				}

				// Split the line into columns
				String[] columns = line.split(",");

				// Assuming the columns are in the exact order as defined in the table
				statement.setInt(1, Integer.parseInt(columns[0])); // custid
				statement.setString(2, columns[1]); // name
				statement.setString(3, ThalesEncryptDecryptService.callEncrypptApi(columns[2])); // address
				statement.setString(4, columns[3]); // city
				statement.setString(5, columns[4]); // state
				statement.setString(6, columns[5]); // zip
				statement.setString(7, columns[6]); // phone
				// statement.setString(8, columns[7]); // email
				statement.setString(8, ThalesEncryptDecryptService.callEncrypptApi(columns[7])); // email
				// statement.setTimestamp(9, parseTimestamp(columns[8])); // dob
				statement.setTimestamp(9, null); // dob
				statement.setLong(10, Long.parseLong(columns[9])); // creditcard
				statement.setInt(11, Integer.parseInt(columns[10])); // creditcardcode
				statement.setString(12, columns[11]); // ssn

				statement.addBatch();
				cnt++;
			}

			// Execute batch insert
			statement.executeBatch();
			System.out.println("Data has been inserted successfully.");
			System.out.println("total records = " + cnt);
		} catch (SQLException | IOException e) {
			e.printStackTrace();
		}
	}

	private static Timestamp parseTimestamp(String dateStr) throws ParseException {
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		return new Timestamp(dateFormat.parse(dateStr).getTime());
	}
}
