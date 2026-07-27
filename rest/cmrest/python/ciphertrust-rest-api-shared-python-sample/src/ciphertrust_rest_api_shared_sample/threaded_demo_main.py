from __future__ import annotations

import argparse
import base64
import concurrent.futures
import json
import time

from .models import ClientConfig
from .rest_support import AuthTokenProvider, CipherTrustRestSupport
from .simple_main import build_config, extract_batch_value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CipherTrust REST threaded token refresh demo")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--key-name", required=True)
    parser.add_argument("--plaintext-base64", required=True)
    parser.add_argument("--pad", default="oaep")
    parser.add_argument("--basic-auth")
    parser.add_argument("--basic-username")
    parser.add_argument("--basic-password")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--threads", type=int, default=3)
    parser.add_argument("--iterations-per-thread", type=int, default=2)
    parser.add_argument("--sleep-seconds-before-decrypt", type=int, default=0)
    parser.add_argument("--sleep-seconds-between-iterations", type=int, default=0)
    parser.add_argument("--max-business-requests-per-token", type=int, default=0)
    parser.add_argument("--refresh-skew-seconds-override", type=int)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--insecure-tls", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


def worker(worker_id: int, args: argparse.Namespace, session, auth_provider, config: ClientConfig) -> tuple[bool, str]:
    try:
        for iteration in range(1, args.iterations_per_thread + 1):
            print(f"[worker-{worker_id}] starting iteration {iteration} of {args.iterations_per_thread}")
            encrypt_body = {
                "id": args.key_name,
                "pad": args.pad,
                "batch_request": [{"plaintext": args.plaintext_base64}],
            }
            encrypt_response = CipherTrustRestSupport.send_authenticated_json_post(
                session, auth_provider, config, "/api/v1/crypto/encrypt", encrypt_body
            )
            CipherTrustRestSupport.ensure_success(encrypt_response, "encrypt")
            ciphertext = extract_batch_value(encrypt_response.json(), "ciphertext")
            print(f"[worker-{worker_id}] encrypt complete; ciphertext length={len(ciphertext)}")

            if args.sleep_seconds_before_decrypt > 0:
                print(f"[worker-{worker_id}] sleeping {args.sleep_seconds_before_decrypt} seconds before decrypt")
                time.sleep(args.sleep_seconds_before_decrypt)

            decrypt_body = {
                "id": args.key_name,
                "pad": args.pad,
                "batch_request": [{"ciphertext": ciphertext}],
            }
            decrypt_response = CipherTrustRestSupport.send_authenticated_json_post(
                session, auth_provider, config, "/api/v1/crypto/decrypt", decrypt_body
            )
            CipherTrustRestSupport.ensure_success(decrypt_response, "decrypt")
            plaintext = extract_batch_value(decrypt_response.json(), "plaintext")
            decoded = base64.b64decode(plaintext)
            print(f"[worker-{worker_id}] decrypt complete; decoded bytes={len(decoded)}")

            if iteration < args.iterations_per_thread and args.sleep_seconds_between_iterations > 0:
                print(f"[worker-{worker_id}] sleeping {args.sleep_seconds_between_iterations} seconds before next iteration")
                time.sleep(args.sleep_seconds_between_iterations)
        return True, "ok"
    except Exception as exc:
        print(f"[worker-{worker_id}] failed: {exc}")
        return False, str(exc)


def main() -> None:
    args = parse_args()
    config = build_config(args)
    session = CipherTrustRestSupport.build_http_session(config)
    auth_provider = AuthTokenProvider(session, config)

    print("Threaded refresh demo configuration:")
    print(f"Threads                       : {args.threads}")
    print(f"Iterations per thread         : {args.iterations_per_thread}")
    print(f"Sleep before decrypt (sec)    : {args.sleep_seconds_before_decrypt}")
    print(f"Sleep between iterations (sec): {args.sleep_seconds_between_iterations}")
    print(f"maxBusinessRequestsPerToken   : {args.max_business_requests_per_token}")
    print(f"refreshSkewSecondsOverride    : {args.refresh_skew_seconds_override}")
    print()

    success = 0
    failure = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(worker, worker_id, args, session, auth_provider, config) for worker_id in range(1, args.threads + 1)]
        for future in concurrent.futures.as_completed(futures):
            ok, _ = future.result()
            if ok:
                success += 1
            else:
                failure += 1

    print("\nThreaded demo complete.")
    print(f"Workers succeeded: {success}")
    print(f"Workers failed   : {failure}")
    print("Expected behavior with shared token provider:")
    print("- one worker may trigger refresh when token enters the refresh window")
    print("- nearby workers should then reuse the refreshed token rather than all refreshing independently")
    print("- in-flight requests keep using the token they started with")
    print("- a 401 or token-expiry-style response still gets one refresh-and-retry attempt")


if __name__ == "__main__":
    main()