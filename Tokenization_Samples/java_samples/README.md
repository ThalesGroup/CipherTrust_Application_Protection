# CTS Java samples

## Prerequesties

- Java 1.8 and above.
- Apache Maven 3.6.0 and above.
- Access to CipherTrust Manager.
- Access to CipherTrust Tokenization Server.
- Tokengroup and Tokentemplate present in CipherTrust Tokenization Server.

## Tokenize/detokenize

Tokenize/detokenize a given data or plaintext string using the tokengroup and tokentemplate.

**tokengroup** : `Defines a group name space in the configuration database. The CTS GUI Administrator must create token groups that match the tokengroup parameter names used in the application code.`

**tokentemplate** : `CTS GUI Administrator-defined name for a group of properties that define tokenization operation.`

**data** : `The data string to tokenize. The argument considers case and is limited to 128K.`

**github link** : https://github.com/thalescpl-io/CipherTrust_Application_Protection/blob/master/Tokenization_Samples/java_samples/src/main/java/com/thales/cts/samples/TokDetok.java

**Syntax** :

```
$ mvn compile
$ mvn exec:java -Dexec.mainClass="com.thales.cts.samples.CTSSample" -Dexec.args=" -l <CTS_HOST> -u <username>:<password> -g <tokengroup> -t <tokentemplate> -i <data or plaintext string>"
```

**Example** :

```
$ mvn exec:java -Dexec.mainClass="com.thales.cts.samples.CTSSample" -Dexec.args=" -l <CTS_HOST> -u <username>:<password> -g FF1_Tok_Group -t FF1_Tok_Template -i 9453677629008564"
```

## Output

```
Tokenize server: https://<CTS_HOST>/vts/rest/v2.0/
Tokenize request: {"data":"9453677629008564","tokengroup":"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"}
Tokenize response: {"token":"u=r`OJ?f~^vZqw\"j","status":"Succeed"}
Token : {"token":"u=r`OJ?f~^vZqw\"j","tokengroup" :"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"}
Detokenize server: https://<CTS_HOST>/vts/rest/v2.0/
Detokenize request: {"token":"u=r`OJ?f~^vZqw\"j","tokengroup" :"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"}
Detokenize response: {"data":"9453677629008564","status":"Succeed"}
```

#

## Tokenize/detokenize Bulk mode

Tokenize/detokenize a given bulk data or plaintext string from file using the tokengroup and tokentemplate.

**tokengroup** : `Defines a group name space in the configuration database. The CTS GUI Administrator must create token groups that match the tokengroup parameter names used in the application code.`

**tokentemplate** : `CTS GUI Administrator-defined name for a group of properties that define tokenization operation.`

**data** : `The data string to tokenize. The argument considers case and is limited to 128K.`

**github link** : https://github.com/thalescpl-io/CipherTrust_Application_Protection/blob/master/Tokenization_Samples/java_samples/src/main/java/com/thales/cts/samples/TokDetokBulk.java

**Syntax** :

```
$ mvn compile
$ mvn exec:java -Dexec.mainClass="com.thales.cts.samples.CTSSample" -Dexec.args=" -l <CTS_HOST> -u <username>:<password> -g <tokengroup> -t <tokentemplate> -f <data or plaintext string file>"
```

**Example** :

```
$ mvn exec:java -Dexec.mainClass="com.thales.cts.samples.CTSSample" -Dexec.args=" -l <CTS_HOST> -u <username>:<password> -g FF1_Tok_Group -t FF1_Tok_Template -i src/main/java/com/thales/cts/samples/input.txt"
```

## Output

```
Bulk Tokenize request: [{"data":"9453677629008564","tokengroup":"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"data":"9453677629008566","tokengroup":"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"data":"9453677629008567","tokengroup":"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"data":"9453677629008568","tokengroup":"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"data":"9453677629008569","tokengroup":"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"}]
Bulk Tokenize response: [{"token":"u=r`OJ?f~^vZqw\"j","status":"Succeed"},{"token":"-,(4{WFKqc @d$$=","status":"Succeed"},{"token":"cR$Jx&>s#oWa>+O9","status":"Succeed"},{"token":"{U=Cb|r~i8='/8eZ","status":"Succeed"},{"token":"?Q\"R*wZt5-T03wl}","status":"Succeed"}]
SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
SLF4J: Defaulting to no-operation (NOP) logger implementation
SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
Bulk Detokenize request: [{"token":"u=r`OJ?f~^vZqw\"j","tokengroup" :"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"token":"-,(4{WFKqc @d$$=","tokengroup" :"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"token":"cR$Jx&>s#oWa>+O9","tokengroup" :"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"token":"{U=Cb|r~i8='/8eZ","tokengroup" :"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"},{"token":"?Q\"R*wZt5-T03wl}","tokengroup" :"FF1_Tok_Group","tokentemplate":"FF1_Tok_Template"}]
Bulk Detokenize response: [{"data":"9453677629008564","status":"Succeed"},{"data":"9453677629008566","status":"Succeed"},{"data":"9453677629008567","status":"Succeed"},{"data":"9453677629008568","status":"Succeed"},{"data":"9453677629008569","status":"Succeed"}]
```

#

## Tokenization/Detokenization api details

https://github.com/thalescpl-io/CipherTrust_Application_Protection/blob/master/Tokenization_Samples/api.md
