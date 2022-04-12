# **Sample code for Unicode CADP Vaultless Tokenization**

## **Overview**
---
These sample code used for demonstration of how tokenization and detokenization operations are performed on Unicode input characters in CADP Vaultless Tokenization.

Tokenization and detokenization of Unicode blocks in CADP Vaultless Tokenization can be achieved using:

* AlgoSpec
* unicode.properties file

    * Range parameter of unicode.properties file 
    * FromFile parameter of unicode.properties file  

> SafeNet Vaultless Tokenization with Unicode supports all the token formats. For more details on supported formats, refer to **CADP Vaultless Tokenization userguide**.

---
## **Samples**

1. CADP Vaultless tokenization and detokenization sample of unicode using AlgoSpec

	This sample shows how to tokenize and detokenize unicode input characters by setting setUnicode parameter in AlgoSpec.

     * File: [*AlgoSpecUnicodeSample.java*](AlgoSpecUnicodeSample.java)
    * **Usage**:
    ```shell
    java AlgoSpecUnicodeSample naeuser naepassword keyname
    ```
2. CADP Vaultless tokenization and detokenization sample of unicode Block Using Range Parameter

    This sample shows how to tokenize and detokenize unicode block using range type in unicode type specifier in unicode.properties file.

     * File: [*RangeUnicodeSample.java*](RangeUnicodeSample.java)
    * **Usage**:
    ```shell
    java RangeUnicodeSample naeuser naepassword keyname
    ```

3. CADP Vaultless tokenization and detokenization sample of unicode Block Using FromFile Parameter

    This sample shows how to tokenize and detokenize unicode block using FromFile type in unicode type specifier in unicode.properties file.

     * File: [*FromFileUnicodeSample.java*](FromFileUnicodeSample.java)
    * **Usage**:
    ```shell
    java FromFileUnicodeSample naeuser naepassword keyname
    ```
> **For details, refer to the unicode.properties file**.