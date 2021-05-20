# tokenize

Tokenize a given data or plaintext string using the tokengroup and tokentemplate.

**URL** : `https://VTS_IP_Address/vts/rest/v2.0/tokenize`

**Method** : `POST`

**Auth required** : `A valid user name and password must be passed as an argument. The values are case sensitive`

**Data constraints**

```json
{
  "tokengroup": "tokengroup",
  "data": "data or plaintext string",
  "tokentemplate": "tokentemplate"
}
```

**Data example**

```json
{
  "tokengroup": "FF1_Tok_Group",
  "data": "DataToTokenizeDetokenize",
  "tokentemplate": "FF1_Tok_Template"
}
```

## Success Response

```json
{
  "token": "EzchFFKH33EGhopWc|Bb|TV(",
  "status": "Succeed"
}
```

## Error Response

**Condition** : `If short input data string provided`

```json
{
  "status": "error",
  "reason": "After accounting for keepleft (0) and keepright (0), not enough input characters are left to successfully tokenize the input of length 1."
}
```

# detokenize

Detokenize a given token using the tokengroup and tokentemplate.

**URL** : `https://VTS_IP_Address/vts/rest/v2.0/detokenize`

**Method** : `POST`

**Auth required** : `A valid user name and password must be passed as an argument. The values are case sensitive`

**Data constraints**

```json
{
  "tokengroup": "tokengroup",
  "token": "The token to detokenize",
  "tokentemplate": "tokentemplate"
}
```

**Data example**

```json
{
  "tokengroup": "FF1_Tok_Group",
  "token": "EzchFFKH33EGhopWc|Bb|TV(",
  "tokentemplate": "FF1_Tok_Template"
}
```

## Success Response

```json
{
  "data": "DataToTokenizeDetokenize",
  "status": "Succeed"
}
```

## Error Response

**Condition** : `If empty/invalid token received.`

```json
{
  "status": "error",
  "reason": "There are not enough input characters for the detokenize operation."
}
```
