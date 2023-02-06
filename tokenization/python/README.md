# Tokenization Samples

## Prerequesties

- Python v2.7.x up.
- rfc3339 python library.
- requests python library.
- eventlet python library.
- Access to CipherTrust Manager(CTS).
- Access to CipherTrust Tokenization Server.
- Tokengroup and Tokentemplate present in CipherTrust Tokenization Server.

## Tokenize

Tokenize a given data or plaintext string using the tokengroup and tokentemplate.

**tokengroup** : `Defines a group name space in the configuration database. The Tokenization Server Administrator must create token groups that match the tokengroup parameter names used in the application code.`

**tokentemplate** : `Tokenization Server Administrator-defined name for a group of properties that define tokenization operation.`

**data** : `The data string to tokenize. The argument considers case and is limited to 128K.`

**github link** : https://github.com/thalescpl-io/CipherTrust_Application_Protection/blob/master/Tokenization/python/tokenizeSample.py

**Syntax** :

```
$ python tokenizeSample.py -d -u <username>:<password> -l <vts URL> -p <data or plaintext string> -O <outputFile> -tg <tokengroup> -tt <tokentemplate>
```

**Example** :

```
$ python tokenizeSample.py -d -u <username>:<password> -l <ip_address> -p DataToTokenizeDetokenize -O token -tg FF1_Tok_Group -tt FF1_Tok_Template
```

## Output

```
Header: {'User-Agent': 'python-requests/2.23.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '_/_', 'Connection': 'keep-alive', 'Content-Type': 'application/json', 'Content-Length': '104', 'Authorization': 'Basic cm9vdDpjYSRoY293'}
URL: https://<ipaddress>/vts/rest/v2.0/tokenize
Data: {"tokengroup": "FF1_Tok_Group", "tokentemplate": "FF1_Tok_Template", "data": "DataToTokenizeDetokenize"}

EzchFFKH33EGhopWc|Bb|TV(

Completed write text to file name token.
```

#

## Detokenize

Detokenize a given token using the tokengroup and tokentemplate.

**tokengroup** : `Defines a group name space in the configuration database. The Tokenization Server Administrator must create token groups that match the tokengroup parameter names used in the application code.`

**tokentemplate** : `Tokenization Server Administrator-defined name for a group of properties that define tokenization operation.`

**data** : `The detokenized sensitive data. May be masked depending on the configuration. The data string is case-sensitive and limited to 128K characters.`

**github link** : https://github.com/thalescpl-io/CipherTrust_Application_Protection/blob/master/Tokenization/python/detokenizeSample.py

**Syntax** :

```
$ python detokenizeSample.py -d -u <username>:<password> -l <vts URL> -I <inputFile> -O <outputFile> -tg <tokengroup> -tt <tokentemplate>
```

**Example** :

```
$ python detokenizeSample.py -d -u <username>:<password> -l <ipaddress> -I token -O raw -tg FF1_Tok_Group -tt FF1_Tok_Template
```

## Output

```
Header: {'User-Agent': 'python-requests/2.23.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '_/_', 'Connection': 'keep-alive', 'Content-Type': 'application/json', 'Content-Length': '105', 'Authorization': 'Basic cm9vdDpjYSRoY293'}
URL: https://<ipaddress>/vts/rest/v2.0/detokenize
Data: {"tokengroup": "FF1_Tok_Group", "tokentemplate": "FF1_Tok_Template", "token": "EzchFFKH33EGhopWc|Bb|TV("}

DataToTokenizeDetokenize

Completed write text to file name raw.
```

#

## Tokenization/Detokenization api details

https://github.com/thalescpl-io/CipherTrust_Application_Protection/blob/master/Tokenization/api.md
