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
import org.apache.commons.cli.*;

public class CTSSample {
    public static void main( String[] args ) throws ParseException {
        // CTS host name or IP for tokenization/detokenization
        Option hostOpt = Option.builder("l")
        .longOpt("host")
        .desc("CTS host name or IP for tokenization/detokenization")
        .required(true)
        .hasArg(true)
        .build();

        // CTS Host credentials
        Option credOpt = Option.builder("u")
        .longOpt("cred")
        .desc("credentials username:password")
        .required(true)
        .hasArg(true)
        .build();

        // Input data file path
        Option filePathOpt = Option.builder("f")
        .longOpt("path")
        .hasArg(true)
        .desc("input data(raw string) file path")
        .required(false)
        .build();

        // input data string
        Option dataOpt = Option.builder("i")
        .longOpt("data")
        .hasArg(true)
        .desc("input data(raw string)")
        .required(false)
        .build();

        // token Group in the configuration database
        Option tokTmpOpt = Option.builder("g")
        .longOpt("tokGroup")
        .desc("token Group")
        .required(true)
        .hasArg(true)
        .build();

        // token Template in the configuration database
        Option tokGrpOpt = Option.builder("t")
        .longOpt("tokTemplate")
        .desc("token Template")
        .required(true)
        .hasArg(true)
        .build();

        Option helpOpt = Option.builder("h")
        .longOpt("help")
        .hasArg(false)
        .required(false)
        .build();

        Options options = new Options();
        options.addOption(hostOpt);
        options.addOption(credOpt);
        options.addOption(filePathOpt);
        options.addOption(dataOpt);
        options.addOption(tokTmpOpt);
        options.addOption(tokGrpOpt);
        options.addOption(helpOpt);


        try {
            CommandLineParser parser = new DefaultParser();
            CommandLine cmd = parser.parse(options, args);
            String host = cmd.getOptionValue("l");
            String https_url = "https://" + host + "/vts/rest/v2.0/";
            String credentialRaw = cmd.getOptionValue("u");
            String tokenGroup = cmd.getOptionValue("g");
            String tokenTemplate = cmd.getOptionValue("t");
            HelpFormatter formatter = new HelpFormatter();

            if (cmd.hasOption("h")) {
                formatter.printHelp("CTS Samples", options, true);
                return;
            }
            if (cmd.hasOption("f")) {
                String filePath = cmd.getOptionValue("f");
                TokDetokBulk cls = new TokDetokBulk();
                cls.DoIt(https_url, credentialRaw, filePath, tokenGroup, tokenTemplate);
            } else if (cmd.hasOption("i")) {
                String data = cmd.getOptionValue("i");
                TokDetok cls = new TokDetok();
                cls.DoIt(https_url, credentialRaw, data, tokenGroup, tokenTemplate);
            } else {
                formatter.printHelp("CTS Samples", options, true);
                return;
            }
        } catch (ParseException e) {
            System.out.println( "Unexpected exception:" + e.getMessage());
        }
    }
}