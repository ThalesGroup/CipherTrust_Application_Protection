/**
 * Sample code is provided for educational purposes.
 * No warranty of any kind, either expressed or implied by fact or law.
 * Use of this item is not restricted by copyright or license terms.
 */
package mypackage.listener;

import java.security.Security;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;

/*
 * HelloListnener is used to remove the IngrianProvider when application is stopped.
 * This is done so that IngrianProvider is loaded again when application is started.
 * This needs to be done only when Ingrian and its dependent jars are placed inside 
 * war WEB-INF/lib folder. 
 */
public class HelloListener implements ServletContextListener {

	@Override
	public void contextInitialized(ServletContextEvent servletContextEvent) {
		// Do nothing
	}

	@Override
	public void contextDestroyed(ServletContextEvent servletContextEvent) {
		if (Security.getProvider("IngrianProvider") != null) {
			Security.removeProvider("IngrianProvider");
		}
	}
}
