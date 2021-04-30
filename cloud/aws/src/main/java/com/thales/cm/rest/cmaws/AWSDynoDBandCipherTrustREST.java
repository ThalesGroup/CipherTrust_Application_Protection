package com.thales.cm.rest.cmaws;

import java.io.IOException;
import java.util.*;
import com.amazonaws.services.dynamodbv2.*;
import com.amazonaws.services.dynamodbv2.model.AttributeValue;

import com.thales.cm.rest.cmhelper.CipherTrustManagerHelper;

public class AWSDynoDBandCipherTrustREST {
	CipherTrustManagerHelper ctmh = null;
	//
	private static final String ADDRESS = "Address";
	private static final String EMAIL = "EmailAddress";
	private static final String TABLE = "ThalesDynoDBCrypto";
	final static AmazonDynamoDB ddb = new AmazonDynamoDBClient();

	public static void main(final String[] args) throws Exception {

		AWSDynoDBandCipherTrustREST awsresrest = new AWSDynoDBandCipherTrustREST();
		awsresrest.ctmh = new CipherTrustManagerHelper();

		if (args.length != 4) {
			System.err.println("Usage: java AWSDynoDBandCipherTrustREST userid password keyname ctmip  ");
			System.exit(-1);
		}
		awsresrest.ctmh.dataformat = "alphanumeric";
		awsresrest.ctmh.username = args[0];
		awsresrest.ctmh.password = args[1];
		awsresrest.ctmh.cmipaddress = args[3];
		try {
			String tkn = awsresrest.ctmh.getToken();

			awsresrest.ctmh.key = args[2];

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		String address = "123 Anystreet Rd., Anytown, USA";

		String results = null;
		String email = "alice@example.com";
		final Map<String, AttributeValue> item = new HashMap<>();
		
		results = awsresrest.ctmh.cmRESTProtect("fpe", address, "encrypt");
		item.put(ADDRESS, new AttributeValue().withS(results));
		results = null;
		results = awsresrest.ctmh.cmRESTProtect("fpe", email, "encrypt");
		item.put(EMAIL, new AttributeValue().withS(results));

		ddb.putItem(TABLE, item);

		final Map<String, AttributeValue> item2 = new HashMap<>();
		address = "321 Washington Ave., Despair, USA";
		results = null;
		email = "sam@example.com";
		results = awsresrest.ctmh.cmRESTProtect("fpe", address, "encrypt");
		item2.put(ADDRESS, new AttributeValue().withS(results));
		results = awsresrest.ctmh.cmRESTProtect("fpe", email, "encrypt");
		item2.put(EMAIL, new AttributeValue().withS(results));

		ddb.putItem(TABLE, item2);

	 
		final Map<String, AttributeValue> item3 = ddb
				.getItem(TABLE, Collections.singletonMap(EMAIL, new AttributeValue().withS(awsresrest.ctmh.cmRESTProtect("fpe", results, "decrypt")))).getItem();

		address = item3.get(ADDRESS).getS();
		System.out.println("address in dyndb " + address);
		results = awsresrest.ctmh.cmRESTProtect("fpe", address, "decrypt");
		System.out.println("decrpted address in dyndb " + results);

	}

}