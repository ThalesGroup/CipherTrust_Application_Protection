/**
 * Sample code is provided for educational purposes.
 * No warranty of any kind, either expressed or implied by fact or law.
 * Use of this item is not restricted by copyright or license terms.
 */
package mypackage;

import java.io.IOException;
import java.io.PrintWriter;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.Provider;
import java.security.Security;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.IvParameterSpec;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.ingrian.security.nae.NAEKey;
import com.ingrian.security.nae.NAESecretKey;
import com.ingrian.security.nae.NAESession;
/**
 * Simple servlet to validate that the Hello example can
 * execute servlets.  In the web application deployment descriptor,
 * this servlet must be mapped to correspond to the link in the
 * "index.html" file.
 *
 */

public final class Hello extends HttpServlet {


    /**
     * Respond to a GET request for the content produced by
     * this servlet.
     *
     * @param request The servlet request we are processing
     * @param response The servlet response we are producing
     *
     * @exception IOException if an input/output error occurs
     * @exception ServletException if a servlet error occurs
     */
    public void doGet(HttpServletRequest request,
                      HttpServletResponse response)
	throws IOException, ServletException {

	response.setContentType("text/html");
	PrintWriter writer = response.getWriter();

	writer.println("<html>");
	writer.println("<head>");
	writer.println("<title>Sample Application Servlet Page</title>");
	writer.println("</head>");
	writer.println("<body bgcolor=white>");

	writer.println("<table border=\"0\">");
	writer.println("<tr>");
	writer.println("<td>");
	writer.println("<img src=\"images/key_hole.gif\">");
	writer.println("</td>");
	writer.println("<td>");
	writer.println("<h1>Sample Application Servlet</h1>");
	writer.println("</td>");


	writer.println("<a href=\"reqparams.html\">");
	       writer.println("<img src=\"images/code.gif\" height=24 " +
		       "width=24 align=right border=0 alt=\"view code\"></a>");
        writer.println("<a href=\"index.html\">");
	 writer.println("<img src=\"images/return.gif\" height=24 " +
		       "width=24 align=right border=0 alt=\"return\"></a>");

	String userName = request.getParameter("username");
        String password = request.getParameter("password");
	String keyName = request.getParameter("keyname");

	writer.println("Parameters in this request: " + "<br>");
        if (userName != null && password != null && keyName != null) {
            writer.println("User Name ");
            writer.println(" = " + HTMLFilter.filter(userName) + "<br>");
            writer.println("Password ");
            writer.println(" = " + HTMLFilter.filter(password) + "<br>");
	    writer.println("Key Name ");
            writer.println(" = " + HTMLFilter.filter(keyName) + "<br>");
        } else {
            writer.println("No Parameters, Please enter some");
        }

	writer.println("<P>");
        writer.print("<form action=\"");
        writer.print("Hello\"");
        writer.println("method=POST>");
        writer.println("User Name: ");
		   
	writer.println("<input type=text size=20 name=username>");
        writer.println("<br>");
        writer.println("Password:  ");
	writer.println("<input type=text size=20 name=password>");
        writer.println("<br>");
	writer.println("Key Name:  ");
	writer.println("<input type=text size=20 name=keyname>");
        writer.println("<br>");
        writer.println("<input type=submit>");
        writer.println("</form>");

    
	writer.println("</tr>");
	writer.println("</table>");

	if (userName != null && password != null && keyName != null) {

	    writer.println("<table border=\"0\">");
	    writer.println("<tr>");
	    writer.println("<td>");
	    writer.println("Start encryption.");
	    writer.println("<br>");
	    
	    NAESession session  = null;
	    try {
		session  = NAESession.getSession( userName, password );
		NAESecretKey key       = NAEKey.getSecretKey( keyName, session );
		Cipher cipher       = Cipher.getInstance( "AES/CBC/PKCS5Padding", "IngrianProvider" );
		
		byte[] IV = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
		IvParameterSpec IVSPEC  = new IvParameterSpec( IV );
		cipher.init( Cipher.ENCRYPT_MODE, key, IVSPEC );
		
		String data = "Hello servlet. ";
		byte[] inbuf = data.getBytes() ;
		
		writer.println("Provider: " + Security
				   .getProvider("IngrianProvider"));
		writer.println("<br>");
		writer.println(" Data to encrypt: " + data);
		writer.println("<br>");
		writer.println(" Encryption algorithm: " + key.getAlgorithm());
		writer.println("<br>");
		byte[] outbuf = cipher.doFinal(inbuf);
		writer.println(" Encrypted data: " + outbuf);
		writer.println("<br>");
		cipher.init( Cipher.DECRYPT_MODE, key, IVSPEC );
		byte[] newbuf = cipher.doFinal(outbuf);
		String data_new = new String(newbuf);
		writer.println(" Decrypted data: " + data_new);
		writer.println("<br>");
	    } catch (NoSuchAlgorithmException exc) {
		throw new IOException("No such alg. " + exc.getMessage());
	    } catch (NoSuchProviderException exc) {
		throw new IOException("No such provider. " + exc.getMessage());
	    } catch (NoSuchPaddingException exc) {
		throw new IOException("No such pad. " + exc.getMessage());
	    } catch (InvalidKeyException exc) {
		throw new IOException("Invalid key. " + exc.getMessage());
	    } catch (InvalidAlgorithmParameterException exc) {
		throw new IOException("Invalid alg params. " + exc.getMessage());
	    } catch (IllegalBlockSizeException exc) {
		throw new IOException("Illegal block size. " + exc.getMessage());
	    } catch (BadPaddingException exc) {
		throw new IOException("Bad Padding. " + exc.getMessage());
	    }finally{
	    	if(session != null){
	    		session.closeSession();
	    	}
	    }
	    
	    writer.println(" Finish encryption.");
	    Provider[] providers = Security.getProviders();
	    writer.println("<h3> Registered providers: </h3>");
	    for (int i = 0; i < providers.length; i++) {
		writer.println("<tr>");
		writer.println("  <th align=\"right\">" + providers[i].toString() + "</th>");
		writer.println("</tr>");
	    }
	    writer.println("</td>");
	    writer.println("</tr>");
	    writer.println("</table>");
	}
	
	writer.println("</body>");
	writer.println("</html>");

    }

    public void doPost(HttpServletRequest request,
		       HttpServletResponse response)
        throws IOException, ServletException
    {
        doGet(request, response);
    }
}
