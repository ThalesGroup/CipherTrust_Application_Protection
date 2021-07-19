/**
 * Sample code is provided for educational purposes.
 * No warranty of any kind, either expressed or implied by fact or law.
 * Use of this item is not restricted by copyright or license terms.
 */
package mypackage;

/**
 * HTML filter utility.
 *
 * @author Craig R. McClanahan
 * @author Tim Tye
 * @version $Revision: 267129 $ $Date: 2004-03-18 11:40:35 -0500 (Thu, 18 Mar 2004) $
 */

public final class HTMLFilter {


    /**
     * Filter the specified message string for characters that are sensitive
     * in HTML.  This avoids potential attacks caused by including JavaScript
     * codes in the request URL that is often reported in error messages.
     *
     * @param message The message string to be filtered
     */
    public static String filter(String message) {

        if (message == null)
            return (null);

        char content[] = new char[message.length()];
        message.getChars(0, message.length(), content, 0);
        StringBuffer result = new StringBuffer(content.length + 50);
        for (int i = 0; i < content.length; i++) {
            switch (content[i]) {
            case '<':
                result.append("&lt;");
                break;
            case '>':
                result.append("&gt;");
                break;
            case '&':
                result.append("&amp;");
                break;
            case '"':
                result.append("&quot;");
                break;
            default:
                result.append(content[i]);
            }
        }
        return (result.toString());

    }


}

