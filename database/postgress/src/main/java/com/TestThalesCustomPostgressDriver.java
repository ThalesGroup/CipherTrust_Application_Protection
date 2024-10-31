import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.PrintStream;
import java.sql.Connection;
import java.sql.Driver;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;

public class TestThalesCustomPostgressDriver {
	
	
	private static Properties properties;

	static {
		try (InputStream input = TestThalesCustomPostgressDriver.class.getClassLoader()
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
	
	public static void main(String[] args) throws FileNotFoundException {

		try {

			Driver customDriver = new ThalesCustomPostgresDriver();
			String url = properties.getProperty("db.url");
			Properties props = new Properties();
			props.setProperty("user", properties.getProperty("db.username"));
			props.setProperty("password", properties.getProperty("db.password"));

			Connection connection = customDriver.connect(url, props);


			Statement stmt = connection.createStatement();
			ResultSet rs = stmt.executeQuery("SELECT email,address ,city FROM plaintext_protected limit 5");

			while (rs.next()) {
				System.out.println(rs.getString("email"));
				System.out.println(rs.getString("address"));
				System.out.println(rs.getString("city"));
				
			}
		} catch (SQLException e) {
			System.out.println("SQL Exception: " + e.getMessage());
			//e.printStackTrace();
		} catch (Exception e) {
			System.out.println("General Exception: " + e.getMessage());
			//e.printStackTrace();
		}
	}
}
