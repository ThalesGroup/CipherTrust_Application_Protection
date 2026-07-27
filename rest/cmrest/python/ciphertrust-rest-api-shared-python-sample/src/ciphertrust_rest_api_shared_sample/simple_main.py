from __future__ import annotations

import argparse
import base64
import json
from typing import Optional

from .models import ClientConfig
from .rest_support import AuthTokenProvider, CipherTrustRestSupport


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CipherTrust REST simple encrypt/decrypt sample")
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
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--sleep-seconds-before-decrypt", type=int, default=0)
    parser.add_argument("--sleep-seconds-between-iterations", type=int, default=0)
    parser.add_argument("--max-business-requests-per-token", type=int, default=0)
    parser.add_argument("--refresh-skew-seconds-override", type=int)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--insecure-tls", action=argparse.BooleanOptionalAction, default=True)
    return parser.parse_args()


def extract_batch_value(response_json: dict, field_name: str) -> str:
    batch = response_json.get("batch_results") or response_json.get("batch_response") or response_json.get("batch_request")
    if isinstance(batch, list) and batch:
        value = batch[0].get(field_name)
        if value:
            return value
    value = response_json.get(field_name)
    if value:
        return value
    raise RuntimeError(f"Unable to locate {field_name} in response: {json.dumps(response_json)}")


def build_config(args: argparse.Namespace) -> ClientConfig:
    basic_auth = args.basic_auth or ClientConfig.encode_basic(args.basic_username, args.basic_password)
    return ClientConfig(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
        basic_auth=basic_auth,
        timeout_seconds=args.timeout_seconds,
        debug=args.debug,
        insecure_tls=args.insecure_tls,
        max_business_requests_per_token=args.max_business_requests_per_token,
        refresh_skew_seconds_override=args.refresh_skew_seconds_override,
    )


def main() -> None:
    args = parse_args()
    config = build_config(args)
    session = CipherTrustRestSupport.build_http_session(config)
    auth_provider = AuthTokenProvider(session, config)

    for iteration in range(1, args.repeat + 1):
        print(f"Iteration {iteration} of {args.repeat}")
        encrypt_body = {
            "id": args.key_name,
            "pad": args.pad,
            "batch_request": [{"plaintext": args.plaintext_base64}],
        }
        encrypt_response = CipherTrustRestSupport.send_authenticated_json_post(
            session, auth_provider, config, "/api/v1/crypto/encrypt", encrypt_body
        )
        CipherTrustRestSupport.ensure_success(encrypt_response, "encrypt")
        encrypt_json = encrypt_response.json()
        print("Encrypt response:")
        print(json.dumps(encrypt_json, indent=2))
        ciphertext = extract_batch_value(encrypt_json, "ciphertext")
        print("\nCiphertext passed into decrypt:")
        print(ciphertext)

        if args.sleep_seconds_before_decrypt > 0:
            import time
            print(f"\nSleeping {args.sleep_seconds_before_decrypt} seconds before decrypt to exercise token lifetime behavior...")
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
        decrypt_json = decrypt_response.json()
        print("\nDecrypt response:")
        print(json.dumps(decrypt_json, indent=2))
        plaintext_base64 = extract_batch_value(decrypt_json, "plaintext")
        decoded_bytes = base64.b64decode(plaintext_base64)
        try:
            decoded_text = decoded_bytes.decode("utf-8")
        except UnicodeDecodeError:
            decoded_text = "<binary data; inspect Base64 output instead>"
        print("\nDecoded plaintext (Base64):")
        print(plaintext_base64)
        print("\nDecoded plaintext (UTF-8 text rendering):")
        print(decoded_text)
        print()

        if iteration < args.repeat and args.sleep_seconds_between_iterations > 0:
            import time
            print(f"Sleeping {args.sleep_seconds_between_iterations} seconds before next iteration...")
            time.sleep(args.sleep_seconds_between_iterations)
            print()


if __name__ == "__main__":
    main()