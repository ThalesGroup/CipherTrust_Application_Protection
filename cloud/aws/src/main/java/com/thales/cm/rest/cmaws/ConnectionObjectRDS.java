package com.thales.cm.rest.cmaws;



import java.sql.Connection;
import java.sql.DriverManager;

public class ConnectionObjectRDS {
   private static Connection conn = null;
   
   public static Connection getConnection(){
	   String url = "jdbc:mysql://your.rds.amazonaws.com/cmdemo?verifyServerCertificate=false&useSSL=true";
	   try{
		   conn = DriverManager.getConnection(url,"youruserid","Yoursupersecret123!");
	   }catch(Exception e){
		   e.printStackTrace();
	   }
	   return conn;
   }
}
