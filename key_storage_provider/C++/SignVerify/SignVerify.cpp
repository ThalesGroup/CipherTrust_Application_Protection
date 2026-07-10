/**@@SignVerify.cpp
 * 
 * This samples demonstrates Sign/SignVerify.
 * 
 */

#include <iostream>
#include <conio.h>
#include <string>
#include <Windows.h>
#include <ncrypt.h>
#include <algorithm>
using namespace std;
#define THALES_PROVIDER_NAME		L"CADP Key Storage Provider"

void hexPrint(string msg, unsigned char* p, int len)
{
	printf("%s", msg.c_str());
	int i=0;
	for(; i<len; ++i)
	{
		printf("%02X ", p[i]);
	}
	printf("\n");
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
	DWORD keySize = 0;
	string keyName;

	//Declarations
	NCRYPT_PROV_HANDLE				hProv = NULL;
	NCRYPT_KEY_HANDLE				hNKey = NULL;	
	CRYPT_KEY_PROV_INFO				keyInfo = {0};
	memset(&keyInfo, 0, sizeof(keyInfo));

	cout<<"Enter key name : ";
	cin>>keyName;
	cout<<endl;

	//keyName = "Gemalto_example_EC-P256";
	keySize = 256; //default key size
	wchar_t* wstrKeyName = ConvertMultiByteToWideCharString(keyName);

	keyInfo.pwszContainerName = wstrKeyName;
	keyInfo.pwszProvName = THALES_PROVIDER_NAME;
	keyInfo.dwProvType = 0;
	keyInfo.dwKeySpec = 0;

	if (!(ERROR_SUCCESS == NCryptOpenStorageProvider(&hProv, THALES_PROVIDER_NAME, 0)))
	{
		cout<<"error : NCryptOpenStorageProvider fail : check for CADP Key Storage Provider registration & CADP_Integration.properties file is configured properly."<<endl;	
	}
	
	if (!(ERROR_SUCCESS == NCryptOpenKey(hProv, &hNKey, wstrKeyName, NULL, 0)))
	{
		if (!(ERROR_SUCCESS == NCryptCreatePersistedKey(hProv, &hNKey, 
			BCRYPT_ECDSA_P256_ALGORITHM, wstrKeyName, 0, 0)))
		{
			cout<<"error : NCryptCreatePersistedKey failure."<<endl;
		}

		//set key size
		NCryptSetProperty(hNKey, NCRYPT_LENGTH_PROPERTY, (LPBYTE)&keySize, sizeof(keySize), 0);

		if (!(ERROR_SUCCESS == NCryptFinalizeKey(hNKey, NULL)))
		{
			cout<<"error : NCryptFinalizeKey failure."<<endl;	
			exit(0);
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

	HRESULT rc = ERROR_SUCCESS;
	DWORD cbOutput = 0;
	DWORD cbResult = 0;

	//EXPORT PUBLIC KEY
	/*
	PBYTE pbOutput = new BYTE[2048];
	BYTE buffer[20000] = {0};
	rc = NCryptExportKey(hNKey, 0, BCRYPT_ECCPUBLIC_BLOB, NULL, NULL, 0, &cbResult, 0);
	cbOutput = cbResult;
	pbOutput = new BYTE[cbOutput]; 
	rc = NCryptExportKey(hNKey, 0, BCRYPT_ECCPUBLIC_BLOB, NULL, pbOutput, cbOutput, &cbResult, 0);
	
	hexPrint("Exported Public Key:", pbOutput, cbResult);
	*/

	BYTE pbHashValue[32] = { 0x5c,0xa1,0x4d,0x44,0xdc,0x33,0xf3,0x50,0xde,0xbf,0xda,0xda,0x13,0xf2,0x14,0xd4,0x61,0x72,0xb0,0x1a,0xcb,0xf1,0x47,0xb2,0xc9,0x2c,0x7d,0xcb,0x03,0x8c,0x2c,0x8d };
	DWORD cbHashValue = 32;
	PBYTE pbSignature = NULL;
	DWORD cbSignature = 0;
	
	if (ERROR_SUCCESS != NCryptSignHash(hNKey, NULL, pbHashValue, cbHashValue, NULL, cbSignature, &cbResult, 0))
	{
		printf("NCryptSignHash failed to calculate sign length :: %x\n", GetLastError());		
	}
	//printf("Signhash requires %d bytes\n", cbResult);
	pbSignature = new BYTE[cbResult];
	memset(pbSignature, 0, cbResult);
	if (ERROR_SUCCESS != NCryptSignHash(hNKey, NULL, pbHashValue, cbHashValue, pbSignature, cbResult, &cbResult, 0))
	{
		printf("NCryptSignHash failed :: %x\n", GetLastError());
		delete [] pbSignature;
		exit(EXIT_FAILURE);
	}
	hexPrint("Signed data : ", pbSignature, cbResult);
	if(ERROR_SUCCESS != (rc = NCryptVerifySignature(hNKey, NULL, pbHashValue, cbHashValue,
		pbSignature, cbResult, 0)) )
	{
		printf("Verification failed rc = %x\n", GetLastError());
		delete [] pbSignature;
		exit(EXIT_FAILURE);
	} 
	else
	{
		printf("Signature Verified.\n");
	}

	if (hNKey)
		NCryptFreeObject(hNKey);

	if (hProv)
		NCryptFreeObject(hProv);
	
	delete [] pbSignature;
	FreeWideCharString(wstrKeyName);
}