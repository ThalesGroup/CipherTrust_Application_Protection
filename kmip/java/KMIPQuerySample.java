/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
// Standard JCE classes. 
import java.security.Security;
import java.util.ArrayList;
import java.util.Map;

import com.ingrian.security.nae.IngrianProvider;
import com.ingrian.security.nae.KMIPQueryFunction;
import com.ingrian.security.nae.KMIPQueryFunction.Query;
import com.ingrian.security.nae.KMIPSession;
import com.ingrian.security.nae.NAEClientCertificate;

/**
 * KMIP Query Sample
 * 
 * This sample shows how to use the KMIP Query Operation. Query results are
 * requested by specifying a List collection of Query enum values for the query
 * information to be returned from the Key Manager.
 * 
 * @see KMIPQueryFunction.Query
 * 
 *      The KMIPSession.query() method returns a map of Query names and a list
 *      of the properties, for example:
 * 
 *      <"Operations", <Get, Destroy, GetAttributes, ....>>
 * 
 *      In order to Query, one must be authenticated to the Key Manager via a
 *      KMIP Session.
 * 
 *      Note: For Key Manager, executing a query on a
 *      non-authenticated session is not supported, though unauthenticated Query
 *      operation from client-to-server is allowed by the KMIP standard.
 * 
 * @link: http://docs.oasis-open.org/kmip/spec/v1.0/os/kmip-spec-1.0-os.html#
 *        _Toc262581232
 * 
 */
public class KMIPQuerySample {
    public static void main(String[] args) throws Exception {
        if (args.length != 2)
        {
                usage();
        } 
        // add Ingrian provider to the list of JCE providers
        Security.addProvider(new IngrianProvider());
        KMIPSession session=null;
        try {

             session = KMIPSession
                    .getSession(new NAEClientCertificate( args[0],  args[1].toCharArray()));
            // create list of Key Manager properties to query
            ArrayList<Query> query = new ArrayList<Query>();
            query.add(Query.QueryObjects);
            query.add(Query.QueryOperations);
            query.add(Query.QueryServerInformation);

            /* execute the query on the session */
            Map<Query, ArrayList<String>> queryResult2 = session.query(query);

            /* view the results */
            for (Query answer : queryResult2.keySet()) {
                System.out.println(answer.getPrintName() + ": "
                        + queryResult2.get(answer));
            }
            
         
        } catch (Exception e) {
            System.out.println("The Cause is " + e.getMessage() + ".");
            e.printStackTrace();
        }
        finally {
        	if(session!=null)
        		session.closeSession();
		}
    }

    private static void usage() {
        System.err.println("Usage: java KMIPQuerySample clientCertAlias keyStorePassword");
        System.exit(-1);
    }
}
