/**
* Sample code is provided for educational purposes.
* No warranty of any kind, either expressed or implied by fact or law.
* Use of this item is not restricted by copyright or license terms.
*/
import java.security.Security;
import java.util.Arrays;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.List;

import com.ingrian.internal.jaxb.UserGroupInfoResponse;
import com.ingrian.internal.jaxb.UserGroupQueryResponse;
import com.ingrian.internal.jaxb.UserInfoResponse;
import com.ingrian.internal.jaxb.UserQueryResponse;
import com.ingrian.security.nae.CustomAttributes;
import com.ingrian.security.nae.NAEAdminRequestProcessor;
import com.ingrian.security.nae.NAESession;
import com.ingrian.security.nae.NAEUserModifyRequest;

/*
 * This sample shows how to perform AdminRequestSample. 
 * It will perform below actions on Key Manager:
 * <li>create a new user</li>
 * <li>create a new group</li>
 * <li>add user to  group</li>
 * <li>delete user from group</li>
 * <li>delete user</li> 
 * AdminRequestSample.java
 */
public class AdminRequestSample {
	private static Scanner sc= new Scanner(System.in,"UTF-8");

	public static void main(String[] args) {

		System.out.println("Sample : AdminRequestSample\n"+
						"Admin Request Options :\n"+
						"1.Create a new user\n"+
						"2.Create a new group\n"+
						"3.Add user to  group\n"+
						"4.Delete user from group\n"+
						"5.Delete group\n"+
						"6.Delete user\n"+
						"7.Get user information\n"+
						"8.Get all users information\n"+
						"9.Get group information\n"+
						"10.Get all group information\n"+
						"11.Modify User Custom Attributes\n" +
						"12.Exit\n");
		int option =0;
		NAESession session =null;
		try {
			System.out.print("Enter admin user-name:");
			String adminUser = sc.next();
			System.out.print("Enter admin password:");
			String adminPassword = sc.next();
			 session = NAESession.getSession(adminUser,adminPassword.toCharArray());
			NAEAdminRequestProcessor processor = new NAEAdminRequestProcessor(session);
			
			do {
				System.out.print("\nPlease select one of option to perform:");
				option = sc.nextInt();
				switch (option) {
				case 1:
					createUser(processor);
					break;
				case 2:
					createGroup(processor);
					break;
				case 3:
					addUserToGroup(processor);
					break;
				case 4:
					deleteUserToGroup(processor);
					break;
				case 5:
					deleteGroup(processor);
					break;
				case 6:
					deleteUser(processor);
					break;
				case 7:
					getUserInfo(processor);
					break;
				case 8:
					getAllUserInfo(processor);
					break;
				case 9:
					getGroupInfo(processor);
					break;
				case 10:
					getAllGroupInfo(processor);
					break;
				case 11:
					modifyUserCustomAttrs(processor);
					break;
				default:
					System.out.println("exit..");
					break;
				}

			} while (option <= 10);
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (session != null)
				session.closeSession();
		}
	}
	
	private static void createUser(NAEAdminRequestProcessor processor){
			System.out.print("Enter user-name :");
			String newuser = sc.next();
			System.out.print("Enter password:");
			String newpass = sc.next();
			System.out.print("Do you want to give change password privilege to user (y/n)");
			String chFlag = sc.next();
			if (chFlag.equalsIgnoreCase("y"))
				processor.createUser(newuser, newpass, true);
			else
				processor.createUser(newuser, newpass, false);
			System.out.println("user created successfully");
	}
	
	private static void createGroup(NAEAdminRequestProcessor processor){
			System.out.print("Enter group-name :");
			String newgroup = sc.next();
			processor.createGroup(newgroup);
			System.out.println("group created successfully");
	}
	
	private static void addUserToGroup(NAEAdminRequestProcessor processor){
			System.out.print("Enter group-name:");
			String group = sc.next();
			System.out.print("Enter user-name list (Ex: user1,user2):");
			String users = sc.next();
			String usersarr[]= users.split(",");
			processor.addUserToGroup(group, Arrays.asList(usersarr));
			System.out.println("users ["+Arrays.asList(usersarr)+"] added successfully");
	}
	
	private static void deleteUserToGroup(NAEAdminRequestProcessor processor){
			System.out.print("Enter group-name:");
			String group = sc.next();
			System.out.print("Enter user-name list (Ex: user1,user2):");
			String users = sc.next();
			String usersarr[]= users.split(",");
			processor.removeUserFromGroup(group, Arrays.asList(usersarr));
			System.out.println("users ["+Arrays.asList(usersarr)+"] removed successfully");
	}
	private static void deleteGroup(NAEAdminRequestProcessor processor){
			System.out.print("Enter group-name :");
			String newgroup = sc.next();
			processor.deleteGroup(newgroup);
			System.out.println("group deleted successfully");
	}
	
	private static void deleteUser(NAEAdminRequestProcessor processor){
			System.out.print("Enter user-name :");
			String user = sc.next();
			processor.deleteUser(user);
			System.out.println("user deleted successfully");
	}
	
	private static void getUserInfo(NAEAdminRequestProcessor processor){
			System.out.print("Enter user-name :");
			String user = sc.next();
			UserInfoResponse response=processor.getUserInfo(user);
			System.out.println("Response:"+response);
	}
	
	private static void getAllUserInfo(NAEAdminRequestProcessor processor){
			UserQueryResponse response=processor.getAllUsers();
			System.out.println("Response:"+response);
	}
	
	private static void getGroupInfo(NAEAdminRequestProcessor processor){
			System.out.print("Enter group-name :");
			String group = sc.next();
			UserGroupInfoResponse response=processor.groupUserInfo(group);
			System.out.println("Response:"+response);
	}
	
	private static void getAllGroupInfo(NAEAdminRequestProcessor processor){
			UserGroupQueryResponse response=processor.getAllGroupInfo();
			System.out.println("Response:"+response);
	}
		
	private static void modifyUserCustomAttrs(NAEAdminRequestProcessor processor){
		System.out.print("Enter user-name :");
		String userName = sc.next();
		
		CustomAttributes attrsToAdd = new CustomAttributes();
		List<String> attrsToDelete= new ArrayList<String>();
		
		System.out.print("Enter Number Of Attribute To Add/Modify :");
		int num=Integer.parseInt(sc.next());
		while(num-->0){
			System.out.print("Enter Attribute Name To Add/Modify :");
			String attr=sc.next();
			System.out.print("Enter Attribute Value :");
			String attrValue = sc.next();
			attrsToAdd.addAttribute(attr,attrValue);
		}
		
		System.out.print("Enter Number Of Attributes To Delete :");
		num=Integer.parseInt(sc.next());	
		while(num-->0){
			System.out.print("Enter Attribute Name To Delete :");
			String attr=sc.next();
			attrsToDelete.add(attr);
		}	
				
		NAEUserModifyRequest umr =  new NAEUserModifyRequest.Builder()
									.userName(userName)
									.customAttrsToAdd(attrsToAdd)
									.customAttrsToDelete(attrsToDelete)
									.build();
									
		boolean success=processor.modifyUser(umr);
		if(success)
			System.out.println("User Custom attributes modified successfully");
		else
			System.out.println("Failure in user Custom attibute modification");
	}
}
