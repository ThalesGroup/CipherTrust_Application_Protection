package com.thales.cm.rest.cmrestdemo;

import java.util.Map;
/** This application demonstrates how to use the CM Rest API to encrypt a particular json element (message) in a file.
 * it leverages a helper class located at:
 * https://github.com/thalescpl-io/CipherTrust_Application_Protection/tree/master/rest/src/main/java/com/thales/cm/rest/cmhelper
 * Format for input file is:
 *     "msgcontent": {
      "recordnbr": 11,
      "title": "Your title",
      "message": "NRajFQ4P4EvuSe27VwG4NWQV5rb0FzO6upYSRp1bM4qKvPhBiJmc5BtEv42W6VjMMTMIvvN4BBCQ9JkiwJxeWL7kdY1",
      "username": "Sam Smith"
    }
  * To run this example need to set the following environment variables.
  * 
  * set cmdebug=0
SET cmuserid=admin
echo %cmuserid%
set cmpassword=yourpwd
set cmserver=yourcmipaddress
set cmkey=yourencryptionkey (must be in root domain of CM)
set cmdataformat=alphanumeric (keep this as alphanumeric)
set cmfile=C:\\jars\\CMRestDemo\\messages.json
java -jar CMRESTJsonDemo.jar 
  
 */
import java.util.Scanner;

import com.thales.cm.rest.cmhelper.CipherTrustManagerHelper;

import net.minidev.json.JSONArray;
import net.minidev.json.JSONObject;
import net.minidev.json.parser.JSONParser;
import net.minidev.json.parser.ParseException;

import java.io.*;

public class CMRESTJsonDemo {

	String fname = "messages.json";

	public static void main(String[] input) throws Exception {
		String datainput = "1";
		CMRESTJsonDemo dcng = new CMRESTJsonDemo();
		dcng.fname = dcng.getFile();
		while (true) {

			datainput = dcng.displayMenu();

			switch (datainput) {
			case "1":
				dcng.readJSONFile();
				break;
			case "2":
				dcng.addRecord();
				break;
			case "3":
				String found = dcng.viewRecord();
				if (found.equals("false"))
					System.out.println("Record not found.....");
				break;
			case "4":
				System.exit(1);
				break;
			default:
				dcng.readJSONFile();
				break;
			}

		}

	}
	/**
	 * Gets the input file.
	 * <p>
	 * 
	 * @return string file name from environment variable called cmfile
	 */
	private String getFile() {
		
		String cmfile = null;
		 Map<String, String> env = System.getenv();
			     for (String envName : env.keySet()) {
			    	 if (envName.equalsIgnoreCase("cmfile"))
			    	 {
			    		 cmfile = env.get(envName);
			    	 }
			     }
		if (cmfile != null)
			fname = cmfile;
		else cmfile = fname;
		return cmfile;
		
	}

	/**
	 * Adds a record to the input file.
	 * <p>
	 */

	private void addRecord() throws Exception {
		String username = "";
		String title = "1";
		String message = "";
		int totalrecords = 0;

		CipherTrustManagerHelper cmrest = new CipherTrustManagerHelper();
		String tkn = cmrest.getToken();

		JSONParser jsonParser = new JSONParser();
		JSONArray messageListNew = new JSONArray();
		try (FileReader reader = new FileReader(fname)) {
			// Read JSON file
			Object obj = jsonParser.parse(reader);

			JSONArray messageList = (JSONArray) obj;
			// System.out.println(messageList);

			for (int i = 0; i < messageList.size(); i++) {
				totalrecords++;

				JSONObject explrObject = (JSONObject) messageList.get(i);
				messageListNew.add(explrObject);

			}

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParseException e) {
			e.printStackTrace();
		}

		Scanner scan = new Scanner(System.in);

		System.out.print("Enter Customer Name : ");
		username = scan.nextLine();

		System.out.print("Enter Title : ");
		title = scan.nextLine();

		System.out.print("Enter Message : ");
		message = scan.nextLine();

		// First Record
		JSONObject messageDetails = new JSONObject();
		messageDetails.put("recordnbr", totalrecords + 1);
		messageDetails.put("username", username);
		messageDetails.put("title", title);

		// This is the call to encrypt the data
		String results = cmrest.cmRESTProtect("fpe", message, "encrypt");
		messageDetails.put("message", results);

		JSONObject messageObject = new JSONObject();
		messageObject.put("msgcontent", messageDetails);
		messageListNew.add(messageObject);
		System.out.println("added new record ");
		parseMessageObject(messageObject);
		// Write JSON file
		try (FileWriter file = new FileWriter(fname)) {
			file.write(messageListNew.toJSONString());
			file.flush();
			file.close();

		} catch (IOException e) {
			e.printStackTrace();
		}

		//scan.close();
	}

	/**
	 * Views a record in the inputfile.
	 * <p>
	 * 
	 * @return string returns "true" if found "false if not found
	 */

	private String viewRecord() throws Exception {

		String found = "true";
		String testing = "0";
		CipherTrustManagerHelper cmrest = new CipherTrustManagerHelper();

		Scanner scan = new Scanner(System.in);
		String username;
		String password;
		String recordnbr;
		System.out.print("Enter CM UserName : ");
		username = scan.nextLine();
		System.out.print("Enter CM Password : ");
		if (testing.equals("1")) {
			password = scan.nextLine();
		} else {
			Console console = System.console();
			if (console == null) {
				System.out.println("No console: not in interactive mode!");
				System.exit(0);
			}
			char[] passwordchar = console.readPassword();
			password = new String(passwordchar);

		}
		cmrest.username = username;
		cmrest.password = password;

		System.out.print("Enter Record Number to view : ");
		recordnbr = scan.nextLine();
		String tkn = cmrest.getToken();

		boolean validnbr = this.isNumeric(recordnbr);
		if (!validnbr)
		{
			System.out.println("Not a number please enter a valid record number ");
			while (!validnbr)
			{
				recordnbr = scan.nextLine();
				validnbr = this.isNumeric(recordnbr);
				if (!validnbr)
				{
					System.out.println("Not a number please enter a valid record number ");
				}
				
			}
			
		}
		Integer recordnbrInt = new Integer(recordnbr);
		int recordnbrint = recordnbrInt.intValue();

		JSONObject messageObject = this.findRecord(recordnbrint);

		if (messageObject != null) {
			this.parseMessageObjectDecrypt(messageObject, cmrest);

		} else
			found = "false";
		
		//scan.close();
		return found;

	}

	private boolean isNumeric(String strNum) {
	    if (strNum == null) {
	        return false;
	    }
	    try {
	        double d = Double.parseDouble(strNum);
	    } catch (NumberFormatException nfe) {
	        return false;
	    }
	    return true;
	}
	
	/**
	 * Displays the menu
	 * <p>
	 * 
	 * @return string Value chosen by user
	 */

	private String displayMenu() {

		System.out.println(" ");
		System.out.println("v1.2");
		System.out.println("---------------------------------------");
		System.out.println("CipherTrust Manager REST JSON file Demo");
		System.out.println("---------------------------------------");
		System.out.println("Menu");
		System.out.println("1. Print file " + fname);
		System.out.println("2. Add a Record");
		System.out.println("3. View a Record");
		System.out.println("4. Exit");

		String datainput = "1";
		Scanner scan = new Scanner(System.in);
		/* enter filename with extension to open and read its content */

		System.out.print("Enter number from above : ");
		datainput = scan.nextLine();

		//scan.close();
		return datainput;

	}

	/**
	 * Finds the record number passed in.
	 * <p>
	 * 
	 * @param recordnumber
	 *            recordnumber to search
	 * @return JSONObject JSON Element of found record or null if not found
	 */
	private JSONObject findRecord(int recordnbr) {

		JSONParser jsonParser = new JSONParser();
		JSONObject explrObject = null;
		try (FileReader reader = new FileReader(fname)) {
			// Read JSON file
			Object obj = jsonParser.parse(reader);

			JSONArray messageList = (JSONArray) obj;
			// System.out.println(messageList);
			System.out.println("Total Number of Records  " + messageList.size());
			
			if(recordnbr >  messageList.size() || recordnbr <=0)
				return null;
			
			System.out.println(" ");
			for (int i = 0; i < messageList.size(); i++) {

				// store each object in JSONObject
				explrObject = (JSONObject) messageList.get(i);
				JSONObject messageObject = (JSONObject) explrObject.get("msgcontent");

				int recordnbrint = (int) messageObject.get("recordnbr");
				if (recordnbr == recordnbrint)
					break;

			}

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParseException e) {
			e.printStackTrace();
		}

		return explrObject;

	}

	/**
	 * Reads all records in a file
	 * <p>
	 */

	private void readJSONFile() {

		JSONParser jsonParser = new JSONParser();

		try (FileReader reader = new FileReader(fname)) {
			// Read JSON file
			Object obj = jsonParser.parse(reader);

			JSONArray messageList = (JSONArray) obj;

			System.out.println(" ");
			System.out.println("Total Number of Records " + messageList.size());
			if (messageList.size() == 0)
				System.out.println(" No records to list please add a record");
			System.out.println(" ");
			System.out.println("---------------------------------------");

			for (int i = 0; i < messageList.size(); i++) {

				// store each object in JSONObject
				JSONObject explrObject = (JSONObject) messageList.get(i);
				parseMessageObject(explrObject);
				// System.out.println(explrObject.get("msgcontent"));
			}
			System.out.println("---------------------------------------");
			System.out.println(" ");

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParseException e) {
			e.printStackTrace();
		}

	}

	/**
	 * Prints the json object passed in. First checks to see if the user has
	 * access to the key by
	 * <p>
	 * 
	 * @param JSONObject
	 *            JSON Object to print
	 * @param CipherTrustManagerHelper
	 *            Helper class to make calls to CM
	 */
	private  void parseMessageObjectDecrypt(JSONObject message, CipherTrustManagerHelper cmrest)
			throws IOException {

		// First call CM to see if the user has access to the key.
		int keysize = cmrest.getKeySize();
		if (keysize == 0) {
			System.out.println("  ");
			System.out.println("No access to key!!!!!!!!!!!!!");
			System.out.println(" ");
		}
		JSONObject messageObject = (JSONObject) message.get("msgcontent");

		int recordnbr = (int) messageObject.get("recordnbr");
		String username = (String) messageObject.get("username");
		String title = (String) messageObject.get("title");
		String message1 = (String) messageObject.get("message");
		String results = null;
		try {
			if (keysize > 0)
				// This is the call to decrypt the data
				results = cmrest.cmRESTProtect("fpe", message1, "decrypt");
			else
				results = message1;

		} catch (Exception e) {
			if (e.getMessage().contains("Resource"))
				System.out.println("No access to key");

			e.printStackTrace();

		}
		System.out.println("" + recordnbr + "," + username + "," + title + "," + results);
	}

	/**
	 * Prints the json object passed in.
	 * <p>
	 * 
	 * @param JSONObject
	 *            JSON Object to print
	 */

	private  void parseMessageObject(JSONObject message) {
		// Get msgcontent object within list
		JSONObject messageObject = (JSONObject) message.get("msgcontent");

		int recordnbr = (int) messageObject.get("recordnbr");
		String username = (String) messageObject.get("username");
		String title = (String) messageObject.get("title");
		String message1 = (String) messageObject.get("message");
		System.out.println("" + recordnbr + "," + username + "," + title + "," + message1);
	}

	// Currently not used.

	private void printRecords() {
		String line = null;
		try {
			/* FileReader reads text files in the default encoding */
			FileReader fileReader = new FileReader(fname);

			/* always wrap the FileReader in BufferedReader */
			BufferedReader bufferedReader = new BufferedReader(fileReader);

			while ((line = bufferedReader.readLine()) != null) {
				System.out.println(line);
			}

			/* always close the file after use */
			bufferedReader.close();
			System.out.println("-------------------");
			System.out.println(" ");
			System.out.println(" ");
		} catch (IOException ex) {
			System.out.println("Error reading file named '" + fname + "'");
		}

	}
}
