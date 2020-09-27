/*************************************************************************
**                                                                      **
** Copyright(c) 2020                              Confidential Material **
**                                                                      **
** This file is the property of Thales Group.                           **
** The contents are proprietary and confidential.                       **
** Unauthorized use, duplication, or dissemination of this document,    **
** in whole or in part, is forbidden without the express consent of     **
** Thales Group.                                                        **
**                                                                      **
**************************************************************************/

package com.thales.cts.samples;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import org.apache.commons.codec.binary.Base64;
import com.jayway.jsonpath.*;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

public class TokDetok {
    @SuppressWarnings("null")
    public void DoIt(String https_url, String credRaw, String data, String tokenGroup, String tokenTemplate) {
        String credential = Base64.encodeBase64String(credRaw.getBytes());
        try {
            // Tokenize request
            URL myurl = new URL(https_url + "tokenize");
            HttpsURLConnection con = (HttpsURLConnection) myurl.openConnection();
            String jStr = "{\"data\":\"" + data + "\",\"tokengroup\":\"" + tokenGroup + "\",\"tokentemplate\":\"" + tokenTemplate + "\"}";
            con.setRequestProperty("Content-length", String.valueOf(jStr.length()));
            con.setRequestProperty("Content-Type", "application/json");
            con.setRequestProperty("Authorization", "Basic " + credential);
            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setDoInput(true);
            DataOutputStream output = new DataOutputStream(con.getOutputStream());
            output.writeBytes(jStr);
            output.close();
            BufferedReader rd = new BufferedReader(new InputStreamReader(con.getInputStream()));
            String line = "";
            String strResponse = "";

            while ((line = rd.readLine()) != null) {
                strResponse = strResponse + line;
            }
            rd.close();
            String token = JsonPath.read(strResponse, "$.token").toString();
            token = token.replace("\\", "\\\\");
            token = token.replace("\"", "\\\"");
            con.disconnect();
            System.out.println("Tokenize server: " + https_url);
            System.out.println("Tokenize request: " + jStr);
            System.out.println("Tokenize response: " + strResponse);

            // Detokenize request
            myurl = new URL(https_url + "detokenize");
            con = (HttpsURLConnection) myurl.openConnection();
            jStr = "{\"token\":\"" + token + "\",\"tokengroup\" :\"" + tokenGroup + "\",\"tokentemplate\":\"" + tokenTemplate + "\"}";
            System.out.println("Token : " + jStr);
            con.setRequestProperty("Content-length", String.valueOf(jStr.length()));
            con.setRequestProperty("Content-Type", "application/json");
            con.setRequestProperty("Authorization", "Basic " + credential);
            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setDoInput(true);
            output = new DataOutputStream(con.getOutputStream());
            output.writeBytes(jStr);
            output.close();
            rd = new BufferedReader(new InputStreamReader(con.getInputStream()));
            line = "";
            strResponse = "";

            while ((line = rd.readLine()) != null) {
                strResponse = strResponse + line;
            }
            rd.close();
            con.disconnect();
            System.out.println("Detokenize server: " + https_url);
            System.out.println("Detokenize request: " + jStr);
            System.out.println("Detokenize response: " + strResponse);

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}