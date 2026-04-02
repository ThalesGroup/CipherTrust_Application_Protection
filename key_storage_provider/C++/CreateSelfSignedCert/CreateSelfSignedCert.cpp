/*@@CreateSelfSignedCert.cpp
* This sample demonstrates how to create a self-signed certificate.
*
* Following NCrypt functions are used:
* - NCryptOpenStorageProvider()
* - NCryptOpenKey()
* - NCryptCreatePersistedKey()
* - NCryptFinalizeKey()
* - NCryptSetProperty()
* - NCryptFreeObject()
*
*/

#include <stdio.h>
#include <stdlib.h>
#include <Windows.h>
#include <ncrypt.h>
#include <iostream>
#include <string>
using namespace std;
#define THALES_PROVIDER_NAME L"CADP Key Storage Provider"
#define KEY_CONTAINER_NAME    L"CADP_example_RSA_Key"			//keyName

/**
* This is helper function.
* As parameters it receives string and error code and prints the message before exit.
*/
void Leave(int error, LPCSTR text)
{
  if (error) printf("Error %08lx. %s\n", error, text);
  else printf("%s\n", text);

  getchar ();
  exit(0);
}

string GetCurrentPath()
{
	char buffer[MAX_PATH];
    DWORD dwResult = GetModuleFileName(NULL, buffer, MAX_PATH);
    std::string fullExeName(buffer);
	string::size_type pos = fullExeName.find_last_of( "\\/" );
    return string( buffer ).substr( 0, pos);
}


#define CheckResult(v) do { int error = (v); if (error) Leave(error, #v); } while (false)

void CreateSelfSignedCertificateUsingCng();

/**
* The CreateSelfSignedCertificateUsingCng() function creates sefl-signed certificate.
* In order to do that it opens a CNG key storage provider, creates a persisted key
* (NCryptCreatePersistedKey() followed by NCryptFinalizeKey), calls to CertCreateSelfSignCertificate()
* to generate the certificate and receiva a certificate context object and sets NCRYPT_CERTIFICATE_PROPERTY
* to a key.
* 
* @return no value (void function) 
* 
*/
void CreateSelfSignedCertificateUsingCng()
{
  NCRYPT_PROV_HANDLE hProv = NULL;
  CheckResult(NCryptOpenStorageProvider(&hProv, THALES_PROVIDER_NAME, 0));
  
  NCRYPT_KEY_HANDLE hNKey = NULL;

  // Check if such a key already exists else create a new key
  if (!(ERROR_SUCCESS == NCryptOpenKey(hProv, &hNKey, KEY_CONTAINER_NAME, NULL, 0)))
  
  {
	CheckResult(NCryptCreatePersistedKey(hProv, &hNKey, BCRYPT_RSA_ALGORITHM, KEY_CONTAINER_NAME, 0, 0));

	CheckResult(NCryptFinalizeKey(hNKey, 0));	//default key size is 2048
  }
  CERT_NAME_BLOB certName = {0};
	certName.cbData = 0;
	certName.pbData = NULL;

  char X500Name[1024] = {0};  
  char *subject = "Certificate Subject";
  char *organization = "Organization";
  char *country = "Country";
  sprintf_s(X500Name, 1024, "CN=\"%s\",O=\"%s\",C=\"%s\"", subject, organization, country);

  // Prepair certificate name in X509 format
  CheckResult(!::CertStrToName(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, X500Name, //dn
                               CERT_OID_NAME_STR, NULL, NULL, &certName.cbData, NULL));
	
  certName.pbData = new BYTE[certName.cbData];
  SecureZeroMemory(certName.pbData, certName.cbData);

  if (!certName.pbData)
    Leave(0, "Memory allocation failed.");

  CheckResult(!::CertStrToName(X509_ASN_ENCODING | PKCS_7_ASN_ENCODING, X500Name, //dn
                               CERT_OID_NAME_STR, NULL, certName.pbData, &certName.cbData, NULL));
  
  
  CRYPT_KEY_PROV_INFO keyInfo = {0};
  keyInfo.pwszContainerName = KEY_CONTAINER_NAME;
  keyInfo.pwszProvName = THALES_PROVIDER_NAME;
  keyInfo.dwProvType = 0;
 
  SYSTEMTIME cs;
  GetSystemTime(&cs);
  cs.wYear += 1;

  PCCERT_CONTEXT pCertContext = CertCreateSelfSignCertificate(hNKey, &certName, 0, &keyInfo, NULL, NULL, &cs, NULL);

  if (!pCertContext)
  {
	  cout<<"\nCertCreateSelfSignCertificate failure : %x\n"<< GetLastError()<<endl;
	  exit(EXIT_FAILURE);
  }

  unsigned long base64CertSize = 0;
  CryptBinaryToStringA(pCertContext->pbCertEncoded, pCertContext->cbCertEncoded, CRYPT_STRING_BASE64HEADER, NULL, &base64CertSize );
  LPSTR base64Cert = (LPSTR)LocalAlloc(0, base64CertSize);
  CryptBinaryToStringA(pCertContext->pbCertEncoded, pCertContext->cbCertEncoded, CRYPT_STRING_BASE64HEADER, base64Cert, &base64CertSize);

  //cout<<endl<<base64Cert<<endl;
  string destFilePath;
  destFilePath = GetCurrentPath() + "\\SelfSignedCert.crt";

  FILE* file = fopen(destFilePath.c_str(), "w");
  if (!file)
  {
	cout<<"\nfopen failure"<<endl;
	exit(EXIT_FAILURE);
  }
  if (!fwrite(base64Cert, base64CertSize, sizeof(BYTE), file))	
  {
	 cout<<"\nfwrite failure\n"<<endl;
	 exit(EXIT_FAILURE);
  }
  else
  {
	cout<<"\nSelfSignedCert created successfully.\n"<<endl;
	cout<<destFilePath<<endl;
  }

  fclose(file);
  delete [] certName.pbData;
  certName.pbData = NULL;

  CheckResult(NCryptSetProperty(hNKey, NCRYPT_CERTIFICATE_PROPERTY, pCertContext->pbCertEncoded, pCertContext->cbCertEncoded, 0));
 
  if (pCertContext)
    CertFreeCertificateContext(pCertContext);

  if (hNKey)
     NCryptFreeObject(hNKey);

  if (hProv)
    NCryptFreeObject(hProv);  
}

int main(int argc, char* argv[])
{
  CreateSelfSignedCertificateUsingCng();

  printf("Press Enter key to exit...\n");
  getchar ();
  return 0;
}