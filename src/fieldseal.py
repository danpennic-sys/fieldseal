#!/usr/bin/env python3
"""
FieldSeal — local-first job logger and QuantumGuard evidence pack generator.
Compatible with QuantumGuard CONTRACT-v1, VeriQuote, JobSeal, Evidence-Core.
Offline after key setup. Deterministic payload hashing.
"""
import argparse
import json
import hashlib
import base64
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Note: cryptography not installed. Using stub signatures. pip install cryptography for real Ed25519.")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_or_create_key(key_path: Path) -> tuple:
    """Returns (private_key_or_None, public_key_hex)"""
    if not CRYPTO_AVAILABLE:
        # Stub for demo
        return None, "00" * 32
    if key_path.exists():
        with open(key_path, "rb") as f:
            priv = serialization.load_pem_private_key(f.read(), password=None)
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return priv, pub_bytes.hex()
    else:
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_path.write_bytes(pem)
        return priv, pub_bytes.hex()

def sign_payload(priv, payload_hash_hex: str) -> str:
    if not CRYPTO_AVAILABLE or priv is None:
        return "00" * 64  # stub
    hash_bytes = bytes.fromhex(payload_hash_hex)
    sig = priv.sign(hash_bytes)
    return sig.hex()

def build_evidence_pack(job: dict, priv, pub_hex: str) -> dict:
    # Deterministic canonical payload (sorted keys, no wall-clock if possible, but include logged timestamp as field)
    payload_obj = {
        "version": "1",
        "type": "field_job_log",
        "job_id": job.get("job_id", "unknown"),
        "client": job.get("client", ""),
        "location": job.get("location", ""),
        "notes": job.get("notes", ""),
        "status": job.get("status", "completed"),
        "media_hashes": job.get("media_hashes", []),
        "logged_at": job.get("logged_at", datetime.now(timezone.utc).isoformat()),
        "operator": job.get("operator", "field-tech")
    }
    payload_bytes = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
    payload_hash = sha256_hex(payload_bytes)
    signature = sign_payload(priv, payload_hash)

    pack = {
        "version": "1",
        "payload": payload_b64,
        "payload_hash": payload_hash,
        "signature": signature,
        "public_key": pub_hex,
        "alg": "ed25519"
    }
    return pack

def demo():
    sample = {
        "job_id": "JOB-2026-001",
        "client": "Acme HVAC Repair",
        "location": "123 Main St, Springfield MO",
        "notes": "Replaced capacitor. Unit cooling properly. Customer signed off.",
        "status": "completed",
        "media_hashes": ["a1b2c3d4e5f6..."],  # placeholder
        "operator": "tech-dan"
    }
    key_path = Path.home() / ".fieldseal_key.pem"
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(sample, priv, pub_hex)
    print(json.dumps(pack, indent=2))
    print("\n# Verify with: qg verify <this.json>  (from QuantumGuard)")

def main():
    parser = argparse.ArgumentParser(description="FieldSeal — local field job evidence logger")
    parser.add_argument("--demo", action="store_true", help="Run demo and print sealed pack")
    parser.add_argument("--job", type=str, help="Path to job JSON file")
    parser.add_argument("--out", type=str, help="Output sealed pack path")
    parser.add_argument("--key", type=str, default=str(Path.home() / ".fieldseal_key.pem"), help="Private key path")
    args = parser.parse_args()

    if args.demo:
        demo()
        return

    if not args.job:
        parser.print_help()
        return

    with open(args.job) as f:
        job = json.load(f)

    key_path = Path(args.key)
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(job, priv, pub_hex)

    out_path = args.out or "sealed_fieldseal.json"
    with open(out_path, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Sealed pack written to {out_path}")
    print(f"Payload hash: {pack['payload_hash']}")
    print("Verify with QuantumGuard: qg verify", out_path)

if __name__ == "__main__":
    main()
