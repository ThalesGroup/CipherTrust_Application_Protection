/**@@SymmetricKeyEncryption.cpp
 * 
 * This samples demonstrates Encryption/Decryption using Symmetric Key.
 * Following key types are supported :
 * AES - All sizes
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
	printf("%s >>", msg.c_str());
	int i=0;
	for(; i<len; ++i)
	{
		printf("%02X,", p[i]);
	}
	printf("<<\n");
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
			BCRYPT_AES_ALGORITHM, wstrKeyName, 0, 0)))
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

		NCryptOpenKey(hProv, &hNKey, wstrKeyName, NULL, 0);
	}
	else
	{
		cout<<"Key already exists."<<endl;
	}

	BYTE input[16] = { 0x31, 0x32, 0x33, 0x34, 0x31, 0x32, 0x33, 0x34, 0x31, 0x32, 0x33, 0x34, 0x31, 0x32, 0x33, 0x34 };
	PBYTE out = NULL;
	DWORD cbRes = 0;
	if(ERROR_SUCCESS != NCryptEncrypt(hNKey, input, 16, NULL, out, cbRes, &cbRes, 0))
	{
		printf("Encryption failed");
	}

	printf("Required bytes : %d\n", cbRes);
	out = new BYTE[cbRes];
	if(ERROR_SUCCESS != NCryptEncrypt(hNKey, input, 16, NULL, out, cbRes, &cbRes, 0))
	{
		printf("Encryption failed");
	}
	hexPrint("Encrypted", out, cbRes);

	DWORD decDataLen = 0;
	if(ERROR_SUCCESS != NCryptDecrypt(hNKey, out, cbRes, NULL, NULL, 0, &decDataLen, 0))
	{
		printf("Decryption failed");
	}
	PBYTE decrypted = new BYTE[decDataLen];
	if(ERROR_SUCCESS != NCryptDecrypt(hNKey, out, cbRes, NULL, decrypted, decDataLen, &cbRes, 0))
	{
		printf("Decryption failed");
	}
	
	hexPrint("Decrypted", decrypted, decDataLen);


	if (hNKey)
		NCryptFreeObject(hNKey);

	if (hProv)
		NCryptFreeObject(hProv);
	
	delete [] out;
	delete [] decrypted;
	FreeWideCharString(wstrKeyName);
}