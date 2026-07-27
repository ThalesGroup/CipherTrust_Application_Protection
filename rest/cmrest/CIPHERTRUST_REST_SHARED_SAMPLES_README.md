# CipherTrust REST API Shared Samples

This repository contains two standalone reference projects that demonstrate the same core design pattern in different languages:

- `ciphertrust-rest-api-shared-java-sample`
- `ciphertrust-rest-api-shared-python-sample`

Both projects focus on one specific problem:

- how to safely call CipherTrust Manager REST APIs when the JWT bearer token is short-lived, often around 5 minutes
- how to keep long-running tools, batch jobs, services, or worker processes from failing when that token expires

These samples are intentionally lightweight and reusable. They are not full frameworks. The goal is to give application teams a practical token-handling pattern they can copy into their own Java or Python codebases.

## Why These Samples Exist

A simple proof of concept can often authenticate once, make a few REST calls, and finish before the token expires. Real workloads are different.

In practice, CipherTrust REST integrations may need to run longer than a single token lifetime, especially in scenarios such as:

- long-running batch jobs
- queue or Kafka consumers
- nightly schedulers and reprocessing utilities
- backend services that stay up continuously
- desktop or thick-client tools that remain open for long sessions
- multi-threaded workers that keep making protected calls over time

Without a shared token-refresh pattern, teams often end up with one of these problems:

- the job fails after several minutes because the token expired
- each code path handles refresh differently
- multiple threads all try to refresh at once
- token handling logic gets duplicated across projects

These samples solve that by centralizing token lifecycle behavior in one reusable helper.

## Core Design Pattern

Both the Java and Python samples implement the same two-path pattern.

### 1. Proactive protection

Before sending a business request, the helper checks whether the JWT is nearing expiry.

If it is, the helper refreshes the token first.

This is the preferred steady-state path because it reduces avoidable failures.

### 2. Reactive recovery

If a request still receives a `401` or a token-expired-style response, the helper refreshes the token and retries the request once.

This is the safety net for edge cases such as:

- clock skew
- network delay
- a request starting just before expiry
- concurrency timing races

Together, these two paths make the calling application more resilient without forcing business logic to understand token lifetime details.

## Projects Included

### Java sample

Folder:

- `ciphertrust-rest-api-shared-java-sample`

Purpose:

- shows a reusable Java token/auth helper for CipherTrust Manager REST APIs
- includes a simple encrypt-then-decrypt example
- includes a threaded demo showing how multiple workers can share one token provider
- can be run directly as a packaged jar

Best fit for:

- standalone Java utilities
- thick-client or desktop Java applications
- backend services and workers written in Java
- internal reusable jar-based patterns

Key implementation areas:

- `CipherTrustRestSupport.java`
- `CipherTrustRestApiSharedSampleMain.java`
- `CipherTrustRestApiThreadedRefreshDemoMain.java`

Deployment models:

- package as a jar and run with `java -jar`
- run alternate entry points with `java -cp`
- embed the helper classes directly in another Java project
- publish as an internal reusable jar if multiple Java applications need the same pattern

### Python sample

Folder:

- `ciphertrust-rest-api-shared-python-sample`

Purpose:

- shows the same token/auth pattern in Python
- includes a simple encrypt-then-decrypt example
- includes a threaded demo for shared token handling
- supports source-tree launch, package install, or wheel packaging

Best fit for:

- Python utilities and scripts
- backend workers and automation tools
- internal CLI tools
- Python services that repeatedly call CipherTrust Manager

Key implementation areas:

- `rest_support.py`
- `simple_main.py`
- `threaded_demo_main.py`

Deployment models:

- run directly from source with launcher scripts
- install with `pip install .`
- build and distribute as a wheel
- embed the helper module into another Python codebase

