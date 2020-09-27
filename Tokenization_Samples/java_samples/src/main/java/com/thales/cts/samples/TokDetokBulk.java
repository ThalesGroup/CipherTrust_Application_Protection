/*************************************************************************
**                                                                      **
** Copyright(c) 2020                              Confidential Material **
**                                                                      **
** This file is the property of Thales E-security Copyright (c) 2020.   **
** The contents are proprietary and confidential.                       **
** Unauthorized use, duplication, or dissemination of this document,    **
** in whole or in part, is forbidden without the express consent of     **
** Thales E-security Copyright (c) 2020.                                **
**                                                                      **
**************************************************************************/

package com.thales.cts.samples;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.File;
import java.io.FileWriter;
import java.io.FileNotFoundException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Scanner;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FilenameUtils;
import com.jayway.jsonpath.*;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

// read write in file, single line per entry, line saperated inputs
public class TokDetokBulk {
    @SuppressWarnings("null")
    public void DoIt(String https_url,String credRaw,String filePath, String tokenGroup, String tokenTemplate) {
        String credential = Base64.encodeBase64String(credRaw.getBytes());
        ArrayList<String> dataBulk = new ArrayList<String>();
        String filePathTmp;
        try {
            File inputFile = new File(filePath);
            filePathTmp = inputFile.getParent() + "/" + FilenameUtils.removeExtension(inputFile.getName());
            Scanner fileReader = new Scanner(inputFile);
            while (fileReader.hasNextLine()) {
                String rawData = fileReader.nextLine();
                dataBulk.add(rawData);
            }
            fileReader.close();
          } catch (FileNotFoundException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
            return;
        }
        try {
            //Bulk Tokenize request
            URL myurl = new URL(https_url + "tokenize");
            String jStrArray = "[";
            for (int i = 0; i < dataBulk.size(); i++) {
                jStrArray = jStrArray + "{\"data\":\"" + dataBulk.get(i)
                        + "\",\"tokengroup\":\"" + tokenGroup + "\",\"tokentemplate\":\"" + tokenTemplate + "\"}";
                if (i < dataBulk.size() - 1) {
                    jStrArray = jStrArray + ",";
                }
            }
            jStrArray = jStrArray + "]";

            HttpsURLConnection con = (HttpsURLConnection) myurl.openConnection();
            con.setRequestProperty("Content-length", String.valueOf(jStrArray.length()));
            con.setRequestProperty("Content-Type", "application/json");
            con.setRequestProperty("Authorization", "Basic " + credential);
            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setDoInput(true);
            DataOutputStream output = new DataOutputStream(con.getOutputStream());
            output.writeBytes(jStrArray);
            output.close();
            BufferedReader rd = new BufferedReader(new InputStreamReader(con.getInputStream()));
            String line = "";
            String strResponse = "";

            while ((line = rd.readLine()) != null) {
                strResponse = strResponse + line;
            }
            rd.close();
            System.out.println("Bulk Tokenize request: " + jStrArray);
            System.out.println("Bulk Tokenize response: " + strResponse);

            try {
                FileWriter fileWriter = new FileWriter(filePathTmp + "_tokenized.txt");
                for (int i = 0; i < dataBulk.size() ; i++) {
                    String tokenTmp = JsonPath.read(strResponse, "$[" + i + "].token").toString();
                    tokenTmp = tokenTmp.replace("\\", "\\\\");
                    tokenTmp = tokenTmp.replace("\"", "\\\"");
                    fileWriter.write(tokenTmp + "\n");
                }
                fileWriter.close();
            } catch (FileNotFoundException e) {
                System.out.println("An error occurred.");
                e.printStackTrace();
                return;
            }

            // Bulk Detokenize request
            myurl = new URL(https_url + "detokenize");
            int totalTokens = 0;
            jStrArray = "[";
            try {
                File inputFile = new File(filePathTmp + "_tokenized.txt");
                Scanner fileReader = new Scanner(inputFile);
                while (fileReader.hasNextLine()) {
                    String token = fileReader.nextLine();
                    jStrArray = jStrArray + "{\"token\":\"" + token
                                + "\",\"tokengroup\" :\"" + tokenGroup 
                                + "\",\"tokentemplate\":\"" + tokenTemplate 
                                + "\"}";
                    if (fileReader.hasNextLine()) {
                        jStrArray = jStrArray + ",";
                    }
                    totalTokens++;
                }
                fileReader.close();
            } catch (FileNotFoundException e) {
                System.out.println("An error occurred.");
                e.printStackTrace();
                return;
            }
            jStrArray = jStrArray + "]";
            con = (HttpsURLConnection) myurl.openConnection();
            con.setRequestProperty("Content-length", String.valueOf(jStrArray.length()));
            con.setRequestProperty("Content-Type", "application/json");
            con.setRequestProperty("Authorization", "Basic " + credential);
            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setDoInput(true);
            output = new DataOutputStream(con.getOutputStream());
            output.writeBytes(jStrArray);
            output.close();
            rd = new BufferedReader(new InputStreamReader(con.getInputStream()));
            line = "";
            strResponse = "";
            while ((line = rd.readLine()) != null) {
                strResponse = strResponse + line;
            }
            rd.close();
            con.disconnect();
            System.out.println("Bulk Detokenize request: " + jStrArray);
            System.out.println("Bulk Detokenize response: " + strResponse);

            try {
                FileWriter fileWriter = new FileWriter(filePathTmp + "_detokenized.txt");
                for (int i = 0; i < totalTokens ; i++) {
                    String dataTmp = JsonPath.read(strResponse, "$[" + i + "].data").toString();
                    fileWriter.write(dataTmp + "\n");
                }
                fileWriter.close();
            } catch (FileNotFoundException e) {
                System.out.println("An error occurred.");
                e.printStackTrace();
                return;
            }
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}