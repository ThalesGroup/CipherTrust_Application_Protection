# CipherTrust REST API Shared Sample

This is a standalone Java sample project that shows a reusable authentication and token-refresh pattern for the CipherTrust Manager REST API.


## Why this sample exists

This helper exists because CipherTrust Manager REST integrations often use short-lived JWT bearer tokens. In this sample, the token lifetime is commonly around 5 minutes, which is long enough for a short test but not long enough for many real workloads.

Without a refresh pattern, any long-running Java process can eventually fail when the token ages out. That becomes especially important for:

- long-running batch jobs
- Kafka or queue consumers
- scheduled decrypt or reprocess utilities
- backend services that run continuously
- multi-threaded worker processes
- thick-client or desktop tools that stay open for a long session

The core idea is simple: do not let each Java project reinvent token handling. Instead, reuse one small helper that can be dropped into almost any Java codebase that needs to call CipherTrust Manager REST endpoints over a long period of time.

## Top-level design pattern

This sample protects the application in two different ways.

### Path 1. Prevent token timeout before it happens

This is the proactive path.

The helper reads the token duration returned by the auth response, computes a refresh buffer, and refreshes before the JWT is expected to expire. This is the preferred path for long-running jobs because it reduces the chance of a failed business request.

### Path 2. Recover if token timeout still occurs

This is the reactive path.

If a request still gets a 401 or an expiry-style error, the helper refreshes the token and retries the request once. This protects the application from edge cases such as clock drift, network delay, or a request that started just before expiry.

Together, these two paths create a practical resilience pattern for long-running CipherTrust REST integrations.

## When this pattern is useful

This pattern is useful in nearly any Java project that needs to call CipherTrust Manager repeatedly over time, including:

- command-line utilities
- standalone jar-based internal tools
- batch or ETL jobs
- schedulers and nightly processing jobs
- multi-threaded worker services
- microservices or plain Java backend services
- desktop or thick-client applications
- proof-of-concept tools that may later become production code

## Companion design document

A visual HTML explainer is included here:

- [ciphertrust-rest-token-refresh-pattern.html](E:\yourproject\work\thales-end-to-end\ciphertrust-rest-api-shared-java-sample\ciphertrust-rest-token-refresh-pattern.html)

That document focuses on the architectural reason for the helper, the two token-protection paths, and how to apply the pattern in long-running Java applications.

## Location

Workspace copy:

`E:\yourproject\work\thales-end-to-end\ciphertrust-rest-api-shared-java-sample`

Standalone GitHub-friendly copy:

`E:\yourproject\work\ciphertrust-rest-api-shared-java-sample`

## What it includes

- reusable `CipherTrustRestSupport` helper
- optional Basic header support for `/api/v1/auth/tokens`
- proactive JWT refresh before expiry
- one retry on `401` or token-expiry responses
- prototype trusted TLS mode for lab environments
- simple encrypt-then-decrypt example
- separate multithreaded shared-token refresh demo
- debug mode so you can see auth, token usage, and refresh events
- plain Java packaging guidance using a normal jar file

## Main classes

Simple single-thread example:

- `com.thales.demo.sample.CipherTrustRestApiSharedSampleMain`

Multithreaded shared-token example:

- `com.thales.demo.sample.CipherTrustRestApiThreadedRefreshDemoMain`

## Deployment model

This project is intentionally slim.

It is designed to be used in one of two simple ways:

- as a source-code sample that developers copy into another Java application
- as a packaged jar that can be run from the command line on any machine with a compatible JDK

Because this sample only uses JDK classes and does not pull in external runtime libraries, deployment is straightforward.

## Build and package the jar

### 1. Open a command prompt or PowerShell window

Change to the project directory:

```powershell
cd E:\yourproject\work\thales-end-to-end\ciphertrust-rest-api-shared-java-sample
```

### 2. Build the jar

```powershell
mvn clean package
```

What this does:

- compiles the source files
- places `.class` files under `target\classes`
- creates a runnable jar under `target`

Expected jar name:

- `target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar`

### 3. Verify the output

After packaging, you should see:

- `target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar`

## Where to deploy the jar

For a simple utility or internal sample, the easiest deployment approach is:

- copy the jar to a utility folder on the target machine
- keep any wrapper scripts or sample command lines alongside it
- run it with a local JDK installation

Example folder layout on a target machine:

```text
C:\apps\ciphertrust-rest-sample\
  ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar
  run-simple.cmd
  run-threaded.cmd
```

For a developer workstation:

- any folder is fine as long as Java and network connectivity to CipherTrust Manager are available

For a server or batch host:

- place the jar in a dedicated application folder
- run it with a service account or scheduled task identity as appropriate
- keep credentials out of scripts when possible

## How to run the packaged jar

### Option 1. Run the simple sample with `java -jar`

The jar manifest is configured so the default main class is:

- `com.thales.demo.sample.CipherTrustRestApiSharedSampleMain`

Example:

```powershell
java -jar target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q=
```

If your environment requires a Basic header on the token request:

```powershell
java -jar target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --basicAuth=a2V5aG9sZGVyOlZvcm1ldHJpYzEyMyE= --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q=
```

### Option 2. Run the threaded demo with `java -cp`

Because the threaded demo uses a different main class, use the classpath form:

```powershell
java -cp target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar com.thales.demo.sample.CipherTrustRestApiThreadedRefreshDemoMain --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --threads=3 --iterationsPerThread=2 --sleepSecondsBeforeDecrypt=40
```

### Option 3. Run directly from compiled classes

This can be useful while developing before packaging:

Simple sample:

```powershell
java -cp target\classes com.thales.demo.sample.CipherTrustRestApiSharedSampleMain --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q=
```

Threaded demo:

```powershell
java -cp target\classes com.thales.demo.sample.CipherTrustRestApiThreadedRefreshDemoMain --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --threads=3 --iterationsPerThread=2 --sleepSecondsBeforeDecrypt=40
```

## Step-by-step command-line example

This is the cleanest end-to-end path for a new machine.

### 1. Prerequisites

Make sure these are installed:

- JDK 21 or compatible JDK used to build the sample
- Maven
- network access to CipherTrust Manager

### 2. Build the jar

```powershell
cd E:\yourproject\work\thales-end-to-end\ciphertrust-rest-api-shared-java-sample
mvn clean package
```

### 3. Confirm the jar exists

```powershell
dir target
```

Look for:

- `ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar`

### 4. Run the simple sample

```powershell
java -jar target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true
```

### 5. Run the threaded demo

```powershell
java -cp target\ciphertrust-rest-api-shared-java-sample-1.0.0-SNAPSHOT.jar com.thales.demo.sample.CipherTrustRestApiThreadedRefreshDemoMain --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --threads=3 --iterationsPerThread=2 --sleepSecondsBeforeDecrypt=40
```

## How refresh works

The CipherTrust auth response returns the token `duration`, for example `300` seconds.

The helper then derives a client-side refresh buffer called `refreshSkewSeconds`.

Example:

- token duration = `300`
- refresh skew = `30`
- the client treats the token as needing refresh at about second `270`

That buffer helps avoid edge cases where a request starts just before expiry and finishes after the server considers the token expired.

## Multithreaded behavior

In a multithreaded app, the helper does not wait for every in-flight thread to finish and then refresh once.

The expected behavior is:

- all threads share one `AuthTokenProvider`
- each new request asks the provider for a valid token
- the first thread that notices the token is inside the refresh window performs the refresh
- nearby threads then reuse the refreshed token
- requests already in flight continue using the token they started with
- if one of those in-flight requests still gets a `401`, the helper refreshes and retries once

This is exactly why the shared provider is synchronized: it reduces the chance that many threads all refresh at the same time.

## CipherTrustRestSupport.java Walkthrough

The helper class is designed so you can lift it into another Java project and reuse the same token and HTTP behavior without pulling in the demo `main` programs.

Source file:

- [CipherTrustRestSupport.java](E:\yourproject\work\thales-end-to-end\ciphertrust-rest-api-shared-java-sample\src\main\java\com\thales\demo\sample\CipherTrustRestSupport.java)

### Class purpose

`CipherTrustRestSupport` centralizes five things:

- building the Java HTTP client
- handling prototype trusted TLS mode
- authenticating to `/api/v1/auth/tokens`
- caching and refreshing the JWT token
- sending authenticated JSON POST requests to CipherTrust Manager

That keeps the application code small. The calling code only has to:

- build a `ClientConfig`
- build an `HttpClient`
- create one shared `AuthTokenProvider`
- call `sendAuthenticatedJsonPost(...)`

### `buildHttpClient(boolean insecureTls, int timeoutSeconds)`

Purpose:

- creates the Java `HttpClient` used for all REST calls

What it does:

- sets the connection timeout
- enables normal redirect handling
- if `insecureTls=true`, disables hostname verification and installs a trust-all SSL context

When to use it:

- use `insecureTls=true` only in a prototype or lab where you want to avoid certificate and hostname validation
- use `insecureTls=false` in production with properly trusted server certificates

Why it matters:

- this gives you one place to control transport behavior instead of repeating TLS setup in every call site

### `ClientConfig`

Purpose:

- holds the configuration needed by the helper

Fields and meaning:

- `baseUrl`
  Base URL for CipherTrust Manager, such as `https://192.168.159.134`
- `username`
  Username used in the password grant body sent to `/api/v1/auth/tokens`
- `password`
  Password used in the password grant body
- `basicAuth`
  Optional Base64 `username:password` value used in the HTTP `Authorization: Basic ...` header for the token request
- `labels`
  Labels sent in the token request body
- `timeoutSeconds`
  Timeout used for auth and crypto calls
- `debug`
  Enables helper debug printing
- `maxBusinessRequestsPerToken`
  Demo-only override that forces refresh after a set number of authenticated crypto calls
- `refreshSkewSecondsOverride`
  Optional override for the proactive refresh buffer

Validation behavior:

- requires `baseUrl`, `username`, and `password`
- defaults labels to `myapp` and `cli` if not supplied
- normalizes timeout to at least a sensible default
- prevents negative refresh skew override values

### `ClientConfig.encodeBasic(String username, String password)`

Purpose:

- convenience helper for building a Basic auth value from raw credentials

What it returns:

- Base64 of `username:password`

When to use it:

- use it if your environment requires a Basic header on the token call and you would rather not precompute the value yourself

### `AuthTokenProvider`

Purpose:

- owns the current token session and refresh logic

Why it exists:

- this class is the heart of the reusable sample
- instead of every caller checking expiry on its own, all callers go through one shared provider

Threading model:

- its public methods are `synchronized`
- that means only one thread at a time can refresh or update token state
- this reduces duplicate refresh attempts in multi-threaded services

Recommended usage:

- create one shared `AuthTokenProvider` for one logical application instance
- for a web service, that usually means one provider per JVM or container instance
- for a thick client, that usually means one provider per running desktop application instance

### `AuthTokenProvider.getValidSession()`

Purpose:

- returns a token session that is safe to use for the next request

What it does:

- authenticates if there is no cached token yet
- refreshes if `maxBusinessRequestsPerToken` was reached
- refreshes if the current token is inside the proactive refresh window
- otherwise returns the cached session

Important note:

- this method does not wait for all already-running requests to finish
- it simply decides what token should be handed out to the next caller asking for one

### `AuthTokenProvider.forceRefresh()`

Purpose:

- forces a re-authentication immediately

Typical use case:

- used after a `401` or token-expired response to get a fresh token and retry once

Why it is separate from `getValidSession()`:

- it makes the code path explicit when the refresh is reactive rather than proactive

### `AuthTokenProvider.recordBusinessRequestUse(String path)`

Purpose:

- increments the count of authenticated crypto requests performed on the current token

Why it exists:

- it supports the demo-only `maxBusinessRequestsPerToken` behavior
- it also prints useful debug output showing how many protected business calls have reused the current token

Production note:

- this counter is mainly useful for demonstration and observability, not because CipherTrust requires refresh after a fixed number of calls

### `Session`

Purpose:

- represents the cached token state

Fields and meaning:

- `jwt`
  The actual bearer token used on crypto calls
- `durationSeconds`
  Lifetime returned by the auth response, or defaulted if missing
- `expiresAtMillis`
  Client-calculated absolute expiry timestamp
- `refreshSkewSeconds`
  Client-side safety buffer before expiry

### `Session.isExpiringSoon()`

Purpose:

- determines whether the token has entered the proactive refresh window

Logic:

- computes `expiresAtMillis - refreshSkewSeconds`
- returns `true` once the current time reaches that threshold

Why it matters:

- this is what makes the helper refresh before the token is fully expired

### `Session.shortToken()`

Purpose:

- returns only the first few characters of the JWT for logging

Why it matters:

- lets you correlate refresh events in debug logs without dumping the full token value into output

### `sendAuthenticatedJsonPost(...)`

Purpose:

- main convenience method for sending an authenticated JSON POST to CipherTrust Manager

What it does:

1. asks `AuthTokenProvider` for a valid session
2. sends the request with `Authorization: Bearer <jwt>`
3. if the response indicates token expiry, refreshes once and retries once
4. records that a business request used the current token

Why this is the method most applications will call:

- it combines token lookup, refresh handling, retry behavior, and HTTP send into one reusable unit

Typical endpoints for this method:

- `/api/v1/crypto/encrypt`
- `/api/v1/crypto/decrypt`
- other CipherTrust JSON POST endpoints that require the same bearer token pattern

### `ensureSuccess(HttpResponse<String> response, String action)`

Purpose:

- simple guard that throws if the HTTP response is not a success status

Why it helps:

- keeps the demo `main` programs readable
- gives a clear message that includes the HTTP code and response body

Typical usage:

- call it right after `sendAuthenticatedJsonPost(...)`
- if it does not throw, parse the JSON body normally

### `authenticate(HttpClient client, ClientConfig config)`

Purpose:

- calls `/api/v1/auth/tokens` and builds a cached `Session`

What it sends:

- JSON body with `grant_type=password`
- the configured username and password
- token labels
- refresh token lifetime fields already used by this sample

Optional header behavior:

- if `basicAuth` is present, sends `Authorization: Basic ...`
- if `basicAuth` is absent, sends only the JSON body credentials

What it extracts:

- `jwt`
- `duration`

What it computes:

- `expiresAtMillis`
- `refreshSkewSeconds`

Default refresh skew logic:

- approximately 10% of token lifetime
- minimum 5 seconds
- maximum 30 seconds

Why that logic is useful:

- it scales reasonably across short and long token lifetimes without hard-coding one value everywhere

### `sendAuthenticatedJsonPostOnce(...)`

Purpose:

- low-level helper that sends one POST using a provided JWT

Why it exists:

- `sendAuthenticatedJsonPost(...)` needs a clean way to perform the first attempt and the retry attempt without duplicating request-building logic

Application code note:

- most callers should not use this directly
- it is primarily an internal building block used by the higher-level helper

### `tokenLooksExpired(String body)`

Purpose:

- lightweight detection of token-expiry-style error messages in the response body

Why it exists:

- some systems communicate expiry through an error payload rather than only through HTTP `401`

Limitation:

- it is intentionally simple string matching, so teams may want to replace it with structured JSON error parsing in a production implementation

### `extractJwt(String body)`

Purpose:

- pulls the `jwt` value out of the auth response body

How it works:

- uses a regular expression to find the field
- unescapes the JSON string value before returning it

Production note:

- if you prefer stronger parsing guarantees, this can be replaced with a JSON library such as Jackson

### `extractOptionalNumber(String body, String fieldName)`

Purpose:

- extracts optional integer fields such as `duration`

Why it is useful:

- lets the helper gracefully use response fields when present while still tolerating missing ones

### `toJsonArray(List<String> values)`

Purpose:

- converts the labels list into a JSON array string

### `quote(String value)`

Purpose:

- escapes string content so it can safely be inserted into simple JSON built as text

### `unescapeJson(String text)`

Purpose:

- converts escaped JSON text back into a plain Java string

### `trimTrailingSlash(String value)`

Purpose:

- normalizes `baseUrl` so the code does not accidentally generate double slashes in request URLs

### `isBlank(String value)`

Purpose:

- tiny null-or-blank helper used during config validation and optional header decisions

### `debug(ClientConfig config, String message)`

Purpose:

- centralizes helper debug output

Why it helps:

- keeps logging format consistent
- makes it easy to disable all helper debug output by setting `debug=false`

## Reuse patterns

### Thick client or desktop application

Typical example:

- Java Swing app
- JavaFX app
- command-line utility with a long-running session
- locally installed business client that talks directly to CipherTrust Manager

Recommended pattern:

1. build one `HttpClient` at application startup
2. build one `ClientConfig`
3. build one shared `AuthTokenProvider`
4. reuse those objects for the life of the running client process

Why this works well:

- the desktop app avoids re-authenticating on every button click or workflow step
- the same cached token can be reused across multiple encrypt or decrypt operations
- the helper refreshes automatically as the session ages

Things to consider:

- if the desktop app supports multiple independent environments, create one provider per environment
- if the app stores secrets locally, protect them carefully because the desktop machine is closer to the user and endpoint risk
- for production, do not leave `insecureTls=true`

### Web service or backend API

Typical example:

- plain Java HTTP service
- microservice running in a container
- batch worker pulling messages from Kafka or another queue

Recommended pattern:

1. create the `HttpClient`, `ClientConfig`, and `AuthTokenProvider` once during service startup
2. hold them as shared singleton-style objects for the life of the JVM
3. let all request-handling threads share the same provider inside that JVM or container

Why this works well:

- reduces unnecessary token calls
- gives consistent refresh behavior across worker threads
- avoids the thundering-herd problem where many threads all authenticate at once

Things to consider:

- each JVM or container instance will still maintain its own token state
- in a horizontally scaled deployment, each pod or container typically has its own provider and token lifecycle
- if very high throughput is needed, watch both CipherTrust auth load and crypto endpoint load separately

### Short-lived utility or batch launcher

Typical example:

- one-off admin tool
- nightly batch job
- performance harness or benchmark utility

Recommended pattern:

- still use the same helper, but expect fewer token refresh events if the run is short
- if the run is long, the helper will naturally refresh as needed

Why this works well:

- keeps even small utilities consistent with the same production-style token handling logic

## Arguments

Shared arguments used by both examples:

- `--baseUrl` required, for example `https://192.168.159.134`
- `--username` required, CipherTrust username used in the password grant
- `--password` required, CipherTrust password used in the password grant
- `--keyName` required, for example `rsakey1`
- `--plaintextBase64` required, plaintext to encrypt expressed as Base64
- `--pad` optional, defaults to `oaep`
- `--timeoutSeconds` optional, defaults to `60`
- `--insecureTls` optional, defaults to `true`
- `--debug` optional, defaults to `false`
- `--basicAuth` optional, precomputed Base64 `username:password` for Basic auth on the token call
- `--basicUsername` optional, alternative way to generate the Basic header at runtime
- `--basicPassword` optional, alternative way to generate the Basic header at runtime
- `--maxBusinessRequestsPerToken` optional, defaults to `0`
- `--refreshSkewSecondsOverride` optional, overrides the derived refresh buffer

Simple sample only:

- `--repeat` optional, defaults to `1`
- `--sleepSecondsBeforeDecrypt` optional, defaults to `0`
- `--sleepSecondsBetweenIterations` optional, defaults to `0`

Threaded demo only:

- `--threads` optional, defaults to `3`
- `--iterationsPerThread` optional, defaults to `2`
- `--sleepSecondsBeforeDecrypt` optional, defaults to `0`
- `--sleepSecondsBetweenIterations` optional, defaults to `0`

## Which arguments are demo-only

These are mainly for testing and demonstration, not normal production knobs:

- `--maxBusinessRequestsPerToken`
- `--sleepSecondsBeforeDecrypt`
- `--sleepSecondsBetweenIterations`
- `--refreshSkewSecondsOverride`

Production behavior should normally rely on the actual token lifetime returned by CipherTrust plus a reasonable client-side refresh buffer.

## Debug mode

Add:

- `--debug=true`

This prints messages such as:

- when the tool authenticates
- whether the token call used a Basic header
- the short token prefix returned
- which REST path is using the current token
- when proactive refresh happens
- when a reactive refresh and retry happens
- how many authenticated business requests have used the current token

## Simple single-thread example

Run from either sample directory:

```powershell
mvn exec:java "-Dexec.args=--baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q="
```

If your environment requires a Basic header on `/api/v1/auth/tokens`:

```powershell
mvn exec:java "-Dexec.args=--baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --basicAuth=a2V5aG9sZGVyOlZvcm1ldHJpYzEyMyE= --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q="
```

## Easy refresh demos for the simple sample

Artificial refresh after one business request:

```powershell
mvn exec:java "-Dexec.args=--baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --maxBusinessRequestsPerToken=1"
```

Natural refresh by adding time between iterations:

```powershell
mvn exec:java "-Dexec.args=--baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --repeat=2 --sleepSecondsBetweenIterations=40"
```

Refresh pressure before decrypt:

```powershell
mvn exec:java "-Dexec.args=--baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --sleepSecondsBeforeDecrypt=40"
```

## Multithreaded shared-token demo

This example shows how several workers share one token provider.

```powershell
mvn exec:java "-Dexec.mainClass=com.thales.demo.sample.CipherTrustRestApiThreadedRefreshDemoMain" "-Dexec.args=--baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --threads=3 --iterationsPerThread=2 --sleepSecondsBeforeDecrypt=40"
```

Good demo variations:

- `--threads=3 --iterationsPerThread=2 --sleepSecondsBeforeDecrypt=40`
  Shows several workers reaching decrypt around the same time, with one of them typically triggering refresh.
- `--threads=4 --iterationsPerThread=3 --sleepSecondsBetweenIterations=35`
  Shows refresh pressure across repeated shared-token usage.
- `--maxBusinessRequestsPerToken=2`
  Forces more visible refresh activity for demonstration only.

## Notes

- `--plaintextBase64` is the only payload input the user needs to provide
- the simple sample encrypts first and then decrypts the returned ciphertext automatically
- `--insecureTls=true` is the default for prototype use
- for production, use trusted certificates and set `--insecureTls=false`
- if the decrypted bytes represent binary key material rather than human-readable text, the Base64 output is the safer value to inspect



## Convenience launcher scripts

This project now includes small wrapper scripts for both Windows and Linux or Unix-style environments.

Windows:

- `run-simple.cmd`
- `run-threaded.cmd`

Linux or Unix:

- `run-simple.sh`
- `run-threaded.sh`

These scripts:

- assume the jar has already been built with `mvn clean package`
- look for the jar under the local `target` folder
- pass all arguments through to the Java program

### Windows examples

Simple sample:

```powershell
.\run-simple.cmd --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true
```

Threaded sample:

```powershell
.\run-threaded.cmd --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --threads=3 --iterationsPerThread=2 --sleepSecondsBeforeDecrypt=40
```

### Linux or Unix examples

Make the scripts executable once:

```bash
chmod +x run-simple.sh run-threaded.sh
```

Simple sample:

```bash
./run-simple.sh --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true
```

Threaded sample:

```bash
./run-threaded.sh --baseUrl=https://192.168.159.134 --username=apiuser --password=yourwd123! --keyName=rsakey1 --plaintextBase64=VGhpcyBpcyBhIHRlc3Q= --debug=true --threads=3 --iterationsPerThread=2 --sleepSecondsBeforeDecrypt=40
```
