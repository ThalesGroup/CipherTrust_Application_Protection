/*************************************************************************
**                                                                      **
** Sample code is provided for educational purposes.                    **
** No warranty of any kind, either expressed or implied by fact or law. **
** Use of this item is not restricted by copyright or license terms.    **
**                                                                      **
**************************************************************************/
/*
 ***************************************************************************
 * File: pkcs11_sample_cli.c
 ***************************************************************************

 ***************************************************************************
 * This file provides an interactive way for the user to use the samples
 * through the CLI.
 ***************************************************************************
 */

#include "pkcs11_sample_helper.h"
#include "pkcs11_sample_cli.h"
#include "pkcs11_sample_create_key.h"
#include "pkcs11_sample_encrypt_decrypt.h"
#include "pkcs11_sample_find_delete_key.h"
#include "pkcs11_sample_keypair_create_sign.h"
#include "pkcs11_sample_find_export_key.h"
#include "pkcs11_sample_en_decrypt_multipart.h"
#include "pkcs11_sample_digest.h"
#include "pkcs11_sample_attributes.h"

int menu()
{

    int retVal = 0;
    int opSelected;
    char **optArrayCKey[2] = {pin, key};
    char **optArrayDKey[2] = {pin, key};
    char **optArrayExportKey[3] = {pin, key, wrappingKey};
    char **optArrayEncryptDecrypt[3] = {pin, key, encryptionType};
    char **optArrayEncryptDecryptMultipart[3] = {pin, key, file};
    char **optArrayKeypairCreateSign[2] = {pin, keyPair};
    char **optArrayDigest[2] = {pin, digestOperation};
    char **optArrayDigestHMAC[3] = {pin, digestHmacOperation, key};
    char **optArrayAttributes[2] = {pin, key};

    printf("Select an operation to perform:\n\n");
    printf("(1) Create/Delete a key on the Key Manager\n");
    printf("(2) Encrypt/Decrypt operation\n");
    printf("(3) Sign/Verify an object or file\n");
    printf("(4) MAC and HMAC examples\n");
    printf("(5) Create attribute\n");
    printf("(6) Exit\n\n");

    opSelected = getCaseInput(0);

    switch (opSelected)
    {
    case 1:
    {
        printf("\n(1) Create key\n");
        printf("(2) Delete key\n");
        printf("(3) Export key\n\n");
        opSelected = getCaseInput(0);

        if (opSelected == 1)
        {
            printf("\n*** Create Key ***\n");
            sampleCli("./pkcs11_sample_create_key", optArrayCKey, 2, createKeySample);
            break;
        }
        else if (opSelected == 2)
        {
            printf("\n*** Delete Key ***\n");
            sampleCli("./pkcs11_sample_find_delete_key", optArrayDKey, 2, deleteKeySample);
            break;
        }
        else if (opSelected == 3)
        {
            printf("\n*** Find and export key ***\n");
            sampleCli("./pkcs11_sample_find_export_key", optArrayExportKey, 3, findExportKeySample);
            break;
        }
    }
    case 2:
    {
        printf("\n(1) Encrypt/Decrypt a single value\n");
        printf("(2) Encrypt/Decrypt a file\n\n");

        opSelected = getCaseInput(0);

        if (opSelected == 1)
        {
            printf("\n*** Encrypt Decrypt ***\n");
            sampleCli("./pkcs11_sample_encrypt_decrypt", optArrayEncryptDecrypt, 3, encryptDecryptSample);
            break;
        }
        else if (opSelected == 2)
        {
            printf("\n*** Encrypt Decrypt Multipart ***\n");
            sampleCli("./pkcs11_sample_en_decrypt_multipart", optArrayEncryptDecryptMultipart, 2, encryptDecryptMultipartSample);
            break;
        }
    }
    case 3:
    {
        printf("\n*** Create key pair and sign data ***\n");
        sampleCli("./pkcs11_sample_keypair_create_sign", optArrayKeypairCreateSign, 2, keypairCreateSignSample);
        break;
    }
    case 4:
    {
        printf("\n*** Hashing ***\n\n");
        printf("(1) MAC operation\n");
        printf("(2) HMAC operation\n\n");

        opSelected = getCaseInput(0);

        if (opSelected == 1)
        {
            sampleCli("./pkcs11_sample_digest", optArrayDigest, 2, digestSample);
            break;
        }
        else if (opSelected == 2)
        {
            sampleCli("./pkcs11_sample_digest", optArrayDigestHMAC, 3, digestSample);
            break;
        }
    }
    case 5:
    {
        printf("\n*** Create attribute ***\n");
        sampleCli("./pkcs11_sample_attributes", optArrayAttributes, 2, attributesSample);
        break;
    }
    case 6:
        printf("\nExit\n");
        retVal = 1;
        break;
    default:
        printf("\nInvalid command\n");
        break;
    }

    return retVal;

}

//Retrieves the users integer input and checks if the value is valid
int getCaseInput(int opSelected)
{

    while ( opSelected == 0 )
    {

        printf("> ");
        if (fgets( userInput, sizeof(userInput), stdin) == NULL)
        {
            printf("No Input\n");
            continue;
        }

        if( strlen(userInput) < 2 || strlen(userInput) > 3)
        {
            printf("Invalid input\n");
            continue;
        }

        if (sscanf(userInput, "%d", &opSelected) != 1)
        {
            opSelected = 0;
            printf("Invalid input\n");
            continue;
        }
        if (opSelected < 1 || opSelected > 6)
        {
            opSelected = 0;
            printf("Invalid input\n");
            continue;
        }
    }
    return opSelected;
}

//Transforms the input given by the user in an array of arguments argv.
//Then calls the sample function with argv.
int callSample(char commandLine[], char *sampleFileName, int f())
{

    enum { kMaxArgs = 128 };
    char *argv[kMaxArgs];

    char *p1;
    p1 = strtok(commandLine, " ");
    argc = 0;

    argv[argc++] = sampleFileName;

    while (p1 && argc < kMaxArgs-1)
    {
        argv[argc++] = p1;
        p1 = strtok(0, " ");
    }
    argv[argc] = 0;

    printf("\n");
    f(argc, argv);
    printf("\n");

    return 0;

}

//Retrieves securily a string input from the user
static int getLine (char *prmpt, char *buff, char *checkValue)
{
    int ch, extra;
    size_t i;
    int validInput = 1;

    // Get line with buffer overrun protection.
    if (prmpt != NULL)
    {
        printf ("%s", prmpt);
        fflush (stdout);
    }

    //if (fgets (buff, 14, stdin) == NULL) {
    if (fgets (buff, PIN_LEN, stdin) == NULL)
    {
        printf("No Input\n");
        return NO_INPUT;
    }

    // If it was too long, there'll be no newline. In that case, we flush
    // to end of line so that excess doesn't affect the next call.
    if (buff[strlen(buff)-1] != '\n')
    {
        extra = 0;
        while (((ch = getchar()) != '\n') && (ch != EOF))
            extra = 1;
        if (extra == 1)
        {
            printf ("Input too long [%s]\n", buff);
        }
        return (extra == 1) ? TOO_LONG : OK;
    }
    // Otherwise remove newline and get the string.
    buff[strlen(buff)-1] = '\0';

    //If empty line return No input
    if (buff[0] == '\0')
    {
        printf("No Input\n");
        return NO_INPUT;
    }

    //If the input needs to be verified such as a HMAC operation or an
    //encryption type, it will be compared to an array of valid values.
    if ( checkValue != NULL )
    {
        if (strcmp(checkValue, "validHmacOperations") == 0)
        {
            size_t size = sizeof validHmacOperations / sizeof validHmacOperations[0];
            for (i = 0; i < size; i++)
            {
                if (strcmp(buff, validHmacOperations[i]) == 0)
                {
                    validInput = 0;
                }
            }
            if (validInput == 1)
            {
                printf("Input not recognized\n");
                return 1;
            }
        }
        if (strcmp(checkValue, "validMacOperations") == 0)
        {
            size_t size = sizeof validMacOperations / sizeof validMacOperations[0];
            for (i = 0; i < size; i++)
            {
                if (strcmp(buff, validMacOperations[i]) == 0)
                {
                    validInput = 0;
                }
            }
            if (validInput == 1)
            {
                printf("Input not recognized\n");
                return 1;
            }
        }
        if (strcmp(checkValue, "validEncryptionType") == 0)
        {
            size_t size = sizeof validEncryptionType / sizeof validEncryptionType[0];
            for (i = 0; i < size; i++)
            {
                if (strcmp(buff, validEncryptionType[i]) == 0)
                {
                    validInput = 0;
                }
            }
            if (validInput == 1)
            {
                printf("Input not recognized\n");
                return 1;
            }
        }
    }
    return OK;
}

//sampleCLI asks the user the required elements to run the sample selected
int sampleCli(char *sampleFileName, char ***optArray , int optArraySize, int f())
{

    char *commandLine;
    int i;

    commandLine = (char *)calloc(128, sizeof(char));

    for (i = 0; i < optArraySize; i++)
    {

        char *inputFromUser = NULL;
        char *symbol = NULL;

        //inputFromUser = (char *)malloc(15);
        inputFromUser = (char *)malloc(PIN_LEN);
        if (!inputFromUser)
        {
            printf("\n*** sampleCli error: Fail to allocate mem for inputFromUser ***\n");
            free(commandLine);
            return 0;
        }
        symbol = (char *)malloc(40);
        if (!symbol)
        {
            printf("\n*** sampleCli error: Fail to allocate mem for symbol ***\n");
            free(inputFromUser);
            free(commandLine);
            return 0;
        }

        if (optArray[i][2] != NULL)
        {
            do
            {
                inputResponse = getLine (optArray[i][1], inputFromUser, optArray[i][2]);
            }
            while ( inputResponse != 0 );
        }
        else
        {
            do
            {
                inputResponse = getLine (optArray[i][1], inputFromUser, NULL);
            }
            while ( inputResponse != 0 );
        }
        //Copies the prefix (-p, -k,- o..) to the symbol variable
        strncpy(symbol, optArray[i][0], sizeof(optArray[i][0]) - 1);

        //Append the user value to the prefix symbol
        strncat(symbol, inputFromUser, strlen(inputFromUser));
        //Append the prefix and the value to the command line arguments
        strncat(commandLine, symbol, strlen(symbol));

        free(inputFromUser);
        free(symbol);
    }

    printf("\n INFO: The command executed is\n %s %s\n", sampleFileName, commandLine);

    callSample(commandLine, sampleFileName, f);
    free(commandLine);
    return 0;
}

int main (void)
{
    int menuLoop = 0;

    printf("\n*** Welcome to the Samples CLI ***\n\n");
    printf("This interface demonstrates how to call the \nsamples through the command line. ");
    printf("To better \nunderstand how the PKCS11 API works you can \ntake a look at the sample code. \n\n");

    do
    {
        menuLoop = menu();
    }
    while ( menuLoop == 0 );

    return OK;

}
