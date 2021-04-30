package com.thales.cm.rest.cmgcp;



import java.sql.Connection;
import java.sql.DriverManager;

public class ConnectionObject {
   private static Connection conn = null;
   
   public static Connection getConnection(){
	   String url = "jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=yourprojectid;OAuthType=0;OAuthServiceAcctEmail=youraccount.iam.gserviceaccount.com;OAuthPvtKeyPath=C:\\keys\\gcp\\yourprojectid.json;";
	   try{
		   Class.forName("com.simba.googlebigquery.jdbc42.Driver").newInstance();
		   conn = DriverManager.getConnection(url);
	   }catch(Exception e){
		   e.printStackTrace();
	   }
	   return conn;
   }
}
