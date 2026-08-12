from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional for dry-run
    def load_dotenv(*_args, **_kwargs):
        return False


REQUIRED = ("R2_ENDPOINT", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET")


@dataclass(frozen=True)
class Config:
    endpoint: str
    access_key_id: str
    secret_access_key: str
    bucket: str
    region: str
    key_prefix: str


def load_config() -> Config:
    load_dotenv(Path(__file__).with_name(".env"))
    return Config(
        endpoint=os.getenv("R2_ENDPOINT", "").rstrip("/"),
        access_key_id=os.getenv("R2_ACCESS_KEY_ID", ""),
        secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY", ""),
        bucket=os.getenv("R2_BUCKET", "workmate"),
        region=os.getenv("R2_REGION", "auto"),
        key_prefix=os.getenv("R2_TEST_KEY_PREFIX", "tests/r2-smoke").strip("/"),
    )


def missing(config: Config) -> list[str]:
    values = {
        "R2_ENDPOINT": config.endpoint,
        "R2_ACCESS_KEY_ID": config.access_key_id,
        "R2_SECRET_ACCESS_KEY": config.secret_access_key,
        "R2_BUCKET": config.bucket,
    }
    return [name for name in REQUIRED if not values[name]]


def dry_run(config: Config) -> dict:
    return {
        "dry_run": True,
        "endpoint_present": bool(config.endpoint),
        "access_key_present": bool(config.access_key_id),
        "secret_key_present": bool(config.secret_access_key),
        "bucket_present": bool(config.bucket),
        "region": config.region,
        "missing": missing(config),
    }


def put_with_presigned_url(url: str, payload: bytes) -> None:
    request = urllib.request.Request(
        url,
        data=payload,
        method="PUT",
        headers={"Content-Type": "audio/wav"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 201):
            raise RuntimeError(f"Presigned PUT failed with HTTP {response.status}")


def get_with_presigned_url(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Presigned GET failed with HTTP {response.status}")
        return response.read()


def lifecycle_status(client, bucket: str) -> dict:
    try:
        response = client.get_bucket_lifecycle_configuration(Bucket=bucket)
    except client.exceptions.ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "UNKNOWN")
        if code in {"NoSuchLifecycleConfiguration", "404"}:
            return {"status": "not_configured"}
        if code in {"AccessDenied", "403"}:
            return {"status": "not_permitted"}
        raise
    rules = response.get("Rules", [])
    return {
        "status": "configured" if rules else "empty",
        "rule_count": len(rules),
        "rule_ids": [rule.get("ID") for rule in rules if rule.get("ID")],
    }


def run(config: Config, require_lifecycle: bool = False) -> dict:
    if missing(config):
        raise RuntimeError("필수 R2 환경변수가 없습니다: " + ", ".join(missing(config)))

    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("실제 테스트 전 pip install -r requirements.txt를 실행하세요.") from exc

    client = boto3.client(
        "s3",
        endpoint_url=config.endpoint,
        aws_access_key_id=config.access_key_id,
        aws_secret_access_key=config.secret_access_key,
        region_name=config.region,
    )
    key = f"{config.key_prefix}/{uuid.uuid4().hex}.wav"
    payload = b"RIFF" + b"workmate-r2-smoke-test"
    expected_hash = hashlib.sha256(payload).hexdigest()
    result = {"bucket": config.bucket, "key": key, "checks": {}}

    try:
        put_url = client.generate_presigned_url(
            "put_object",
            Params={"Bucket": config.bucket, "Key": key, "ContentType": "audio/wav"},
            ExpiresIn=600,
        )
        put_with_presigned_url(put_url, payload)
        result["checks"]["presigned_put"] = "pass"

        head = client.head_object(Bucket=config.bucket, Key=key)
        result["checks"]["head_object"] = "pass"
        result["object"] = {
            "content_type": head.get("ContentType"),
            "content_length": head.get("ContentLength"),
        }

        get_url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": config.bucket, "Key": key},
            ExpiresIn=600,
        )
        downloaded = get_with_presigned_url(get_url)
        if hashlib.sha256(downloaded).hexdigest() != expected_hash:
            raise RuntimeError("다운로드한 객체 checksum이 업로드 데이터와 다릅니다.")
        result["checks"]["presigned_get_checksum"] = "pass"

        result["lifecycle"] = lifecycle_status(client, config.bucket)
        if require_lifecycle and result["lifecycle"]["status"] != "configured":
            raise RuntimeError("R2 Lifecycle 정책이 설정되어 있지 않습니다.")
        result["checks"]["lifecycle"] = result["lifecycle"]["status"]
    finally:
        try:
            client.delete_object(Bucket=config.bucket, Key=key)
            result["checks"]["delete_object"] = "pass"
        except Exception as exc:  # preserve the original failure
            result["cleanup_error"] = type(exc).__name__

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Cloudflare R2 Workmate smoke test")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-lifecycle", action="store_true")
    args = parser.parse_args()
    config = load_config()
    try:
        result = dry_run(config) if args.dry_run else run(config, args.require_lifecycle)
    except (RuntimeError, urllib.error.URLError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
