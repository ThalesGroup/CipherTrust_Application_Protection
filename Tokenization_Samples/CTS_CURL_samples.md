# CTS CURL samples

## Prerequesties

- cURL 7.58.0 and above.
- Access to CipherTrust Manager.
- Tokengroup and Tokentemplate present in CipherTrust Manager.
- Access to CipherTrust Tokenization Server.

## Tokenize

Tokenize a given data or plaintext string using the tokengroup and tokentemplate.

**tokengroup** : `Defines a group name space in the configuration database. The CTS GUI Administrator must create token groups that match the tokengroup parameter names used in the application code.`

**tokentemplate** : `CTS GUI Administrator-defined name for a group of properties that define tokenization operation.`

**data** : `The data string to tokenize. The argument considers case and is limited to 128K.`

**Syntax** :

```
curl --location --request  POST -k 'https://<CTS_HOST>/vts/rest/v2.0/tokenize' -u <username>:<password> --header 'Connection: keep-alive, Content-Type: application/json, User-Agent: python-requests/2.18.4, Accept-Encoding: gzip, deflate, Accept: */*, Content-Length: 104, Authorization: Basic cm9vdDpjYSRoY293' --data-raw '{"tokengroup": <tokengroup>, "tokentemplate": <tokentemplate>, "data": <data or plaintext string> }'
```

**Example** :

```
curl --location --request  POST -k 'https://<CTS_HOST>/vts/rest/v2.0/tokenize' -u <username>:<password> --header 'Connection: keep-alive, Content-Type: application/json, User-Agent: python-requests/2.18.4, Accept-Encoding: gzip, deflate, Accept: */*, Content-Length: 104, Authorization: Basic cm9vdDpjYSRoY293' --data-raw '{"tokengroup": "FF1_Tok_Group", "tokentemplate": "FF1_Tok_Template", "data": "9453677629008569" }'
```

## Output

```
{"token":"?Q\"R*wZt5-T03wl}","status":"Succeed"}
```

#

## Detokenize

Detokenize a given token using the tokengroup and tokentemplate.

**tokengroup** : `Defines a group name space in the configuration database. The CTS GUI Administrator must create token groups that match the tokengroup parameter names used in the application code.`

**tokentemplate** : `CTS GUI Administrator-defined name for a group of properties that define tokenization operation.`

**data** : `The detokenized sensitive data. May be masked depending on the configuration. The data string is case-sensitive and limited to 128K characters.`

**Syntax** :

```
curl --location --request  POST -k 'https://<CTS_HOST>/vts/rest/v2.0/detokenize' -u <username>:<password> --header 'Connection: keep-alive, Content-Type: application/json, User-Agent: python-requests/2.18.4, Accept-Encoding: gzip, deflate, Accept: */*, Content-Length: 104, Authorization: Basic cm9vdDpjYSRoY293' --data-raw '{"tokengroup": <tokengroup>, "tokentemplate": <tokentemplate>, "token": <token>}'
```

**Example** :

```
curl --location --request  POST -k 'https://<CTS_HOST>/vts/rest/v2.0/detokenize' -u <username>:<password> --header 'Connection: keep-alive, Content-Type: application/json, User-Agent: python-requests/2.18.4, Accept-Encoding: gzip, deflate, Accept: */*, Content-Length: 104, Authorization: Basic cm9vdDpjYSRoY293' --data-raw '{"tokengroup": "FF1_Tok_Group", "tokentemplate": "FF1_Tok_Template", "token": "?Q\"R*wZt5-T03wl}"}'
```

## Output

```
{"data":"9453677629008569","status":"Succeed"}
```

#

## Tokenization/Detokenization api details

https://github.com/thalescpl-io/CipherTrust_Application_Protection/blob/master/Tokenization_Samples/api.md
