# v1 vs v2 Request Comparison

This document captures the CRDP bulk request and response shapes that this
repository should use.

Important casing note:

- the runtime code uses lowercase `request_data`
- keep it lowercase even if older web documentation shows `Request_data`
- the CRDP validation error observed from the service also expected lowercase
  `request_data`

## v1 protectbulk

Request:

```json
{
  "protection_policy_name": "char-internal",
  "data_array": [
    "1234562jhljhjl39480234",
    "39480234jhljhjkyl32345"
  ]
}
```

Response:

```json
{
  "protected_data_array": [
    {
      "protected_data": "1001000zbQYX9Y6e43bi5Q7s9FUYB"
    },
    {
      "protected_data": "1001000efsruXmcOkqxLLU5s5GCga"
    }
  ]
}
```

## v2 protectbulk

Request:

```json
{
  "request_data": [
    {
      "data_array": [
        "1234562jhljhjl39480234",
        "39480234jhljhjkyl32345"
      ],
      "protection_policy_name": "char-internal"
    },
    {
      "data_array": [
        "ksjhfkjadsfi58856jadsf",
        "cgdt17649klreamnpz0871"
      ],
      "protection_policy_name": "char-internal"
    },
    {
      "data_array": [
        "123123k123jkhhjk12k3jk",
        "t1gpq2387xcyt04glbkhjat"
      ],
      "protection_policy_name": "char-none"
    }
  ]
}
```

Response:

```json
{
  "status": "Success",
  "total_count": 6,
  "success_count": 6,
  "error_count": 0,
  "response_data": [
    {
      "protection_policy_name": "char-internal",
      "protected_data_array": [
        {
          "protected_data": "1001000zbQYX9Y6e43bi5Q7s9FUYB"
        },
        {
          "protected_data": "1001000efsruXmcOkqxLLU5s5GCga"
        }
      ]
    },
    {
      "protection_policy_name": "char-internal",
      "protected_data_array": [
        {
          "protected_data": "1001000J0lc3cX39nWRA0VpHshKgl"
        },
        {
          "protected_data": "1001000ZywBoUvDkfJ3v3lC7xmo41"
        }
      ]
    },
    {
      "protection_policy_name": "char-none",
      "protected_data_array": [
        {
          "protected_data": "uF3fOg1ZgYzFyxeMD6n5vO"
        },
        {
          "protected_data": "ENbQa5upIeX6sHF4g351UHh"
        }
      ]
    }
  ]
}
```

## v1 revealbulk

Request:

```json
{
  "protection_policy_name": "char-internal",
  "username": "admin",
  "protected_data_array": [
    {
      "protected_data": "1001000zbQYX9Y6e43bi5Q7s9FUYB"
    },
    {
      "protected_data": "1001000efsruXmcOkqxLLU5s5GCga"
    }
  ]
}
```

Response:

```json
{
  "data_array": [
    {
      "data": "1234562jhljhjl39480234"
    },
    {
      "data": "39480234jhljhjkyl32345"
    }
  ]
}
```

## v2 revealbulk

Request:

```json
{
  "username": "admin",
  "request_data": [
    {
      "protection_policy_name": "char-internal",
      "protected_data_array": [
        {
          "protected_data": "1001000zbQYX9Y6e43bi5Q7s9FUYB"
        },
        {
          "protected_data": "1001000efsruXmcOkqxLLU5s5GCga"
        }
      ]
    },
    {
      "protection_policy_name": "char-internal",
      "protected_data_array": [
        {
          "protected_data": "1001000J0lc3cX39nWRA0VpHshKgl"
        },
        {
          "protected_data": "1001000ZywBoUvDkfJ3v3lC7xmo41"
        }
      ]
    },
    {
      "protection_policy_name": "char-none",
      "protected_data_array": [
        {
          "protected_data": "uF3fOg1ZgYzFyxeMD6n5vO"
        },
        {
          "protected_data": "ENbQa5upIeX6sHF4g351UHh"
        }
      ]
    }
  ]
}
```

Response:

```json
{
  "status": "Success",
  "total_count": 6,
  "success_count": 6,
  "error_count": 0,
  "data_array": [
    [
      {
        "data": "1234562jhljhjl39480234"
      },
      {
        "data": "39480234jhljhjkyl32345"
      }
    ],
    [
      {
        "data": "ksjhfkjadsfi58856jadsf"
      },
      {
        "data": "cgdt17649klreamnpz0871"
      }
    ],
    [
      {
        "data": "123123k123jkhhjk12k3jk"
      },
      {
        "data": "t1gpq2387xcyt04glbkhjat"
      }
    ]
  ]
}
```

## Repository alignment

These repository components are expected to follow the shapes above:

- Java request builder and parser:
  [JavaCrdpService.java](E:\codex\work\thales.databricks.integration\src\main\java\com\thales\databricks\integration\service\JavaCrdpService.java:1)
- Python request builder and parser:
  [transport.py](E:\codex\work\thales.databricks.integration\src\thales_databricks_integration\transport.py:1)

The current runtime code already uses:

- v1 protect: `protection_policy_name` + `data_array`
- v2 protect: lowercase `request_data` + grouped `data_array`
- v1 reveal: `protection_policy_name` + `username` + `protected_data_array`
- v2 reveal: lowercase `request_data` + grouped `protected_data_array`

And it parses:

- v2 protect responses from `response_data[*].protected_data_array`
- v2 reveal responses from grouped `data_array`

If a future CRDP deployment returns a different response nesting, this file
should be treated as the source-of-truth contract to bring the builders and
parsers back into alignment.
