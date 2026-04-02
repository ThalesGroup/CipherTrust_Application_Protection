/**@@CreateKey.cpp
 * 
 * This samples demonstrates how to create key.
 * Following key types are supported :
 * AES - All sizes
 * RSA [2048, 3072, 4096]
 * EC - All sizes
 * 
 * 
 */



#include <iostream>
#include <conio.h>
#include <string>
#include <Windows.h>
#include <ncrypt.h>
#include <algorithm>
//#include "stdafx.h"
using namespace std;
#define THALES_PROVIDER_NAME		L"CADP Key Storage Provider"


int SetKeyLength(int keyType)
{
	int keyLength = 0;
	switch(keyType)
	{
		case 1 : //AES
				cout<<"Enter AES key length [128, 192, 256] : ";
				cin>>keyLength;
				if (keyLength != 128 && keyLength != 192 && keyLength != 256)
				{
					cout<<"aes : invalid key length"<<endl;
					exit(EXIT_FAILURE);
				}
				break;
		case 2:  //RSA
				cout<<"Enter RSA key length [2048 - 4096] : ";
				cin>>keyLength;
				if (keyLength != 2048 && keyLength != 3072 && keyLength != 4096)
				{
					cout<<"rsa key length not supported"<<endl;
					exit(EXIT_FAILURE);
				}
				break;
		case 3 : //EC
				cout<<"Enter EC key length [256, 384, 521] : ";
				cin>>keyLength;
				if (keyLength != 256 && keyLength != 384 && keyLength != 521)
				{
					cout<<"ec : invalid key length"<<endl;
					exit(EXIT_FAILURE);
				}
				break;
		default :
			cout<<"invalid key type"<<endl;
			exit(EXIT_FAILURE);
	}

	return keyLength;
}

string SetECAlgo(int keySize)
{
	string algo;
	switch(keySize)
	{
		case 256 :
			algo = "ECDSA_P256";
			break;
		case 384 :
			algo = "ECDSA_P384";
			break;
		case 521 :
			algo = "ECDSA_P521";
			break;
		default : cout<<"invalid ec key size"<<endl;
			exit(EXIT_FAILURE);
	}
	return algo;
}

wchar_t* ConvertMultiByteToWideCharString(string mbString)
{

	int wchars_num =  MultiByteToWideChar( CP_UTF8 , 0 , mbString.c_str() , -1, NULL , 0 );
	wchar_t* wstrKeyName = new wchar_t[wchars_num];
	MultiByteToWideChar(CP_UTF8 , 0 , mbString.c_str() , -1, wstrKeyName , wchars_num );
	
	return wstrKeyName;
}

void FreeWideCharString(wchar_t* wcString)
{
	if (wcString)
		delete[] wcString; 
}

int main(int argc, char* argv[])
{
	int keyType = 0;
	int keySize = 0;
	string keyName;

	string keyAlgorithm;
	bool isKeyCreated = true;

	//Declarations
	NCRYPT_PROV_HANDLE				hProv = NULL;
	NCRYPT_KEY_HANDLE				hNKey = NULL;	
	CRYPT_KEY_PROV_INFO				keyInfo = {0};
	memset(&keyInfo, 0, sizeof(keyInfo));

	int choice = -1;
	cout<<"****************Create Key Sample****************"<<endl;
	cout<<"1. AES"<<endl;
	cout<<"2. RSA"<<endl;
	cout<<"3. EC"<<endl;
	cout<<"Enter key type : ";
	cin>>keyType;
	cout<<endl;

	cout<<"Enter key name : ";
	cin.ignore();
	getline(cin, keyName);
	cout<<endl;
	if (keyName.length() == 0)
	{
		cout<<"Invalid keyname"<<endl;
		exit(EXIT_FAILURE);
	}
	switch(keyType)
	{
		case 1 : 
				keyAlgorithm = "AES";
				keySize = SetKeyLength(keyType);
				break;
		case 2 :
				keyAlgorithm = "RSA";
				keySize = SetKeyLength(keyType);
				break;
		case 3 :
				keySize = SetKeyLength(keyType);
				keyAlgorithm = SetECAlgo(keySize);
				break;
		default :
				cout<<"Invalid key type"<<endl;
				exit(EXIT_FAILURE);
	}

	wchar_t* wstrKeyName = ConvertMultiByteToWideCharString(keyName);
	wchar_t* wstrKeyAlgo = ConvertMultiByteToWideCharString(keyAlgorithm);

	keyInfo.pwszContainerName = wstrKeyName;
	keyInfo.pwszProvName = THALES_PROVIDER_NAME;
	keyInfo.dwProvType = 0;
	keyInfo.dwKeySpec = 0;

	if (!(ERROR_SUCCESS == NCryptOpenStorageProvider(&hProv, THALES_PROVIDER_NAME, 0)))
	{
		cout<<"error : NCryptOpenStorageProvider fail : check for CADP Key Storage Provider registration & CADP_Integration.properties file is configured properly.\n."<<endl;	
	}
	
	if (!(ERROR_SUCCESS == NCryptOpenKey(hProv, &hNKey, wstrKeyName, NULL, 0)))
	{
		if (!(ERROR_SUCCESS == NCryptCreatePersistedKey(hProv, &hNKey, 
			wstrKeyAlgo, wstrKeyName, 0, 0)))
		{
			cout<<"error : NCryptCreatePersistedKey failure."<<endl;	
		}

		//set key size
		NCryptSetProperty(hNKey, NCRYPT_LENGTH_PROPERTY, (LPBYTE)&keySize, 4, 0);

		if (!(ERROR_SUCCESS == NCryptFinalizeKey(hNKey, NULL)))
		{
			cout<<"error : NCryptFinalizeKey failure."<<endl;	
		}
		else
		{
			cout<<"New key created successfuly."<<endl;
		}
	}
	else
	{
		cout<<"Key already exists."<<endl;
	}


	if (hNKey)
		NCryptFreeObject(hNKey);

	if (hProv)
		NCryptFreeObject(hProv);
	
	FreeWideCharString(wstrKeyName);
	FreeWideCharString(wstrKeyAlgo);
}