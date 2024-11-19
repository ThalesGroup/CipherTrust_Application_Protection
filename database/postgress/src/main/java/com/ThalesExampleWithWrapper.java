import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class ThalesExampleWithWrapper {
	
	
	private static Properties properties;

	static {
		try (InputStream input = ThalesExampleWithWrapper.class.getClassLoader()
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
	
    public static void main(String[] args) {
        String url = properties.getProperty("db.url");
        String user = properties.getProperty("db.username");
        String password = properties.getProperty("db.password");

        try (
        		
        	Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement()) {

        	
            String query = "SELECT custid, email, address  FROM plaintext_protected limit 5";
            try (ResultSet rs = new ThalesDecryptingResultSetWrapper(stmt.executeQuery(query))) {
                while (rs.next()) {
                    String id = rs.getString("custid");
                   // int id = rs.getInt("custid");
                    String email = rs.getString("email");
                    String address = rs.getString("address");
                    System.out.println("ID: " + id);
                    System.out.println("Email: " + email);
                    System.out.println("Address: " + address);

                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
