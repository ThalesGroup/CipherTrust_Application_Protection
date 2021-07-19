/**
 * Sample code is provided for educational purposes.
 * No warranty of any kind, either expressed or implied by fact or law.
 * Use of this item is not restricted by copyright or license terms.
 */

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Date;
import java.util.logging.ConsoleHandler;
import java.util.logging.FileHandler;
import java.util.logging.Formatter;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.LogRecord;
import java.util.logging.Logger;

import com.ingrian.internal.ilc.IngrianLogService;
/**
 * <code>JavaUtilLogger</code> provides custom logging implement of IngrianLogging
 * using java logging framework.It provides implementation of <code>IngrianLogService</code>
 * @author aawasthi
 *
 */
public class JavaUtilLogger  implements IngrianLogService {
	 Logger logger;
	 String logPropertiesFilePath=System.getProperty("user.dir")+File.separator+"log.properties";
	 String logFile=System.getProperty("user.dir")+File.separator+"sampleLogger%u.log";

	 {
    	 try {
             LogManager.getLogManager().readConfiguration(new FileInputStream(new File(logPropertiesFilePath)));
         } catch (SecurityException e) {
             e.printStackTrace();
         } catch (FileNotFoundException e) {
 			e.printStackTrace();
 		} catch (IOException e) {
 			e.printStackTrace();
 		}
    }
	public JavaUtilLogger() {
		logger = Logger.getLogger(CustomLoggerSample.class.getName());
		logger.setLevel(Level.ALL);
		logger.addHandler(new ConsoleHandler());
		Handler fileHandler;
		try {
			fileHandler = new FileHandler(logFile);
			fileHandler.setFormatter(new Formatter() {
				@Override
				public String format(LogRecord record) {
					 return record.getThreadID()+"::"+record.getSourceClassName()+"::"
				                +record.getSourceMethodName()+"::"
				                +new Date(record.getMillis())+"::"
				                +record.getMessage()+"\n";
				}
			});
			logger.addHandler(fileHandler);
		} catch (SecurityException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	
	}
	@Override
	public void debug(String msg) {
		logger.log(Level.FINE, msg);
	}
	@Override
	public void debug(String msg, Throwable t) {
		logger.log(Level.FINE, msg,t);
	}
	@Override
	public void error(String msg) {
		logger.log(Level.SEVERE, msg);
	}
	@Override
	public void error(String msg, Throwable t) {
		logger.log(Level.SEVERE, msg,t);	
	}
	@Override
	public void info(String msg) {
		logger.log(Level.SEVERE, msg);	
	}
	@Override
	public boolean isDebugEnabled() {
		return logger.isLoggable(Level.FINE);
	}
	@Override
	public boolean isErrorEnabled() {
		return logger.isLoggable(Level.SEVERE);
	}
	@Override
	public boolean isInfoEnabled() {
		return logger.isLoggable(Level.INFO);
	}
	@Override
	public boolean isTraceEnabled() {
		return logger.isLoggable(Level.FINE);
	}
	@Override
	public boolean isWarnEnabled() {
		return logger.isLoggable(Level.WARNING);
	}
	@Override
	public void trace(String msg) {
		logger.log(Level.FINE, msg);
	}
	@Override
	public void warn(String msg) {
		logger.log(Level.WARNING, msg);
	}
	@Override
	public void warn(String msg, Throwable t) {
		logger.log(Level.WARNING, msg,t);
	}
	

}
