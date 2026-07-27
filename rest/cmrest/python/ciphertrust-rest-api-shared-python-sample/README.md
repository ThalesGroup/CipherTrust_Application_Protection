# CipherTrust REST API Shared Python Sample

Project location:

`E:\yourproject\work\ciphertrust-rest-api-shared-python-sample`

## Why this sample exists

This helper exists because CipherTrust Manager REST integrations often use short-lived JWT bearer tokens. In this sample, the token lifetime is commonly around 5 minutes, which is long enough for a quick manual test but not long enough for many real workloads.

Without a refresh pattern, any long-running Python process can eventually fail when the token ages out. That becomes especially important for:

- long-running batch jobs
- Kafka or queue consumers
- scheduled decrypt or reprocess utilities
- backend services that run continuously
- multi-threaded worker processes
- thick-client or desktop tools that stay open for a long session

The core idea is simple: do not let each Python project reinvent token handling. Instead, reuse one small helper that can be dropped into almost any Python codebase that needs to call CipherTrust Manager REST endpoints over a long period of time.

## Top-level design pattern

This sample protects the application in two different ways.

### Path 1. Prevent token timeout before it happens

This is the proactive path.

The helper reads the token duration returned by the auth response, computes a refresh buffer, and refreshes before the JWT is expected to expire. This is the preferred path for long-running jobs because it reduces the chance of a failed business request.

### Path 2. Recover if token timeout still occurs

This is the reactive path.

If a request still gets a `401` or an expiry-style error, the helper refreshes the token and retries the request once. This protects the application from edge cases such as clock drift, network delay, or a request that started just before expiry.

Together, these two paths create a practical resilience pattern for long-running CipherTrust REST integrations.

## When this pattern is useful

This pattern is useful in nearly any Python project that needs to call CipherTrust Manager repeatedly over time, including:

- command-line utilities
- standalone internal tools
- batch or ETL jobs
- schedulers and nightly processing jobs
- multi-threaded worker services
- backend APIs and worker containers
- desktop or thick-client applications
- proof-of-concept tools that may later become production code

## Companion design document

A visual HTML explainer is included here:

- [ciphertrust-rest-token-refresh-pattern-python.html](E:\yourproject\work\ciphertrust-rest-api-shared-python-sample\ciphertrust-rest-token-refresh-pattern-python.html)

That document focuses on the architectural reason for the helper, the two token-protection paths, and how to apply the pattern in long-running Python applications.

## What it includes

- reusable REST support helper
- optional Basic header support for `/api/v1/auth/tokens`
- proactive JWT refresh before expiry
- one retry on `401` or token-expiry responses
- prototype trusted TLS mode for lab environments
- simple encrypt-then-decrypt example
- separate multithreaded shared-token refresh demo
- launcher scripts for Windows and Linux
- wheel-friendly Python package layout

## Project layout

```text
ciphertrust-rest-api-shared-python-sample/
  README.md
  pyproject.toml
  requirements.txt
  run-simple.cmd
  run-threaded.cmd
  run-simple.sh
  run-threaded.sh
  ciphertrust-rest-token-refresh-pattern-python.html
  src/
    ciphertrust_rest_api_shared_sample/
      __init__.py
      models.py
      rest_support.py
      simple_main.py
      threaded_demo_main.py
```

## Recommended for prototype use

The lowest-footprint and simplest option is to use the included launcher scripts.

That path:

- does not require `pip install .`
- does not require building a wheel
- reuses the local source tree directly
- is the best choice for quick testing or demos

Windows:

```powershell
cd E:\yourproject\work\ciphertrust-rest-api-shared-python-sample
.\run-simple.cmd --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug
```

Linux:

```bash
cd /path/to/ciphertrust-rest-api-shared-python-sample
chmod +x run-simple.sh run-threaded.sh
./run-simple.sh --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug
```

Use `pip install .` only if you specifically want the `ciphertrust-rest-simple` and `ciphertrust-rest-threaded` commands available in your Python environment.

### Why the launcher script may work when the installed command does not

On some Windows machines, the `pip install .` console entry point wrapper such as `ciphertrust-rest-simple.exe` can be blocked by local security controls, endpoint protection, or execution policy behavior.

In that case, you may see an error like:

- `Program 'ciphertrust-rest-simple.exe' failed to run: Access is denied`

The included `run-simple.cmd` and `run-threaded.cmd` scripts often still work because they do not rely on the generated `.exe` shim. They call Python directly with `python -m ...`, which avoids that blocked wrapper layer.

For Windows prototype use, the recommended order is now:

1. `run-simple.cmd` or `run-threaded.cmd`
2. `python -m ciphertrust_rest_api_shared_sample.simple_main ...`
3. installed `ciphertrust-rest-simple` command only if your environment allows the generated launcher exe to run

## Install options

### Option 1. Run directly from source

From the project root:

```powershell
$env:PYTHONPATH="src"
python -m ciphertrust_rest_api_shared_sample.simple_main --help
```

### Option 2. Install locally

This is optional and is mainly for users who want package-style commands instead of the launcher scripts.

```powershell
pip install .
```

Then run:

```powershell
ciphertrust-rest-simple --help
ciphertrust-rest-threaded --help
```

### Option 3. Build a wheel

```powershell
python -m pip install build
python -m build
```

That creates artifacts under:

- `dist\`

## Common arguments

- `--base-url` required
- `--username` required
- `--password` required
- `--key-name` required
- `--plaintext-base64` required
- `--pad` optional, defaults to `oaep`
- `--timeout-seconds` optional, defaults to `60`
- `--insecure-tls` optional, defaults to enabled for prototype trusted mode
- `--no-insecure-tls` optional, use this when you want normal certificate validation
- `--debug` optional flag
- `--basic-auth` optional precomputed Base64 `username:password`
- `--basic-username` optional helper input
- `--basic-password` optional helper input
- `--max-business-requests-per-token` demo-only
- `--refresh-skew-seconds-override` demo-only override

## Simple example

```powershell
.\run-simple.cmd --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug
```

## Threaded example

```powershell
.\run-threaded.cmd --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug --threads 3 --iterations-per-thread 2 --sleep-seconds-before-decrypt 40
```

## Launcher scripts

This is the recommended path for prototype and low-storage use cases because it avoids installing the sample package into your Python environment.

Windows:

```powershell
.\run-simple.cmd --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug
.\run-threaded.cmd --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug --threads 3 --iterations-per-thread 2 --sleep-seconds-before-decrypt 40
```

Linux:

```bash
chmod +x run-simple.sh run-threaded.sh
./run-simple.sh --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug
./run-threaded.sh --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug --threads 3 --iterations-per-thread 2 --sleep-seconds-before-decrypt 40
```

## Reuse guidance

The launcher scripts set `PYTHONPATH` to the local `src` folder automatically, so they work before installation.

This package is meant to be reused in three ways:

- copy the helper into another Python application
- install the package into an internal utility environment
- build a wheel and hand it to another team

For a desktop or thick client:

- create one shared `requests.Session`
- create one shared `AuthTokenProvider`
- reuse them for the lifetime of the running process

For a web service or backend worker:

- create them once during startup
- share them across worker threads in the same process
- let each process or container own its own token lifecycle

## Why you saw the SSL error

The error you hit:

- `SSLCertVerificationError: certificate verify failed: self-signed certificate in certificate chain`

means Python tried to validate the CipherTrust Manager server certificate and did not trust the certificate chain.

This is the same kind of issue we previously handled in the Java sample when using prototype trusted mode.

The Python sample now defaults to prototype trusted mode as well.

That means this works for prototype or lab environments without extra certificate setup:

```powershell
.\run-simple.cmd --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug
```

If you want normal certificate validation instead, use:

```powershell
.\run-simple.cmd --no-insecure-tls --base-url https://192.168.159.134 --username apiuser --password yourwd123! --key-name rsakey1 --plaintext-base64 VGhpcyBpcyBhIHRlc3Q= --debug
```