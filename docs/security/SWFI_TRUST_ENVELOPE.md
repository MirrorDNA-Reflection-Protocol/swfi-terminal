# SWFI Trust Envelope v0.1

## Position

SWFI should not invent a new cipher.

SWFI should build a proprietary trust and encryption system on top of proven primitives, strict key custody, signed provenance, and export-aware access controls.

That gives SWFI a defensible security posture without taking on irresponsible cryptographic risk.

## Design Goals

- protect `Key People`, contact data, exports, and AI transcripts at field level
- preserve search and workflow usability
- support tenant and client isolation
- sign records and exports so trust can be verified
- support rotation, revocation, and audit without data loss

## Approved Primitives

Use only standard, modern primitives:

- `XChaCha20-Poly1305` for application-layer record encryption where nonce safety and developer ergonomics matter
- `AES-256-GCM` where HSM, KMS, or compliance rails require it
- `Ed25519` for detached signatures on records, manifests, and audit attestations
- `HMAC-SHA256` for blind indexes and stable lookup tokens
- `HKDF-SHA256` for bounded derivation from already-trusted parent keys when needed

Do not:

- create a custom cipher
- create a custom hash
- create a custom signing scheme
- reuse one key across tenants or protection domains

## Protection Domains

Separate keys and policy by data domain:

- `public_profile`
- `restricted_profile`
- `person_contact`
- `transaction_confidential`
- `rfp_mandate`
- `export_bundle`
- `ai_transcript`
- `audit_ledger`

## Key Hierarchy

### 1. Root key

- lives only in `KMS` or `HSM`
- never leaves the custody boundary
- wraps tenant master keys

### 2. Tenant master key (`TMK`)

- one per tenant or top-level data boundary
- wrapped by the root key
- never used directly for record encryption

### 3. Domain protection key (`DPK`)

- one per tenant x domain
- examples:
  - `tenant_a/person_contact`
  - `tenant_a/export_bundle`
  - `tenant_a/ai_transcript`
- used only to wrap short-lived data encryption keys

### 4. Data encryption key (`DEK`)

- generated per record version, bundle, or transcript object
- used once for payload encryption
- stored only in wrapped form alongside the encrypted object

### 5. Blind index key (`BIK`)

- separate from encryption keys
- one per tenant x indexed field family
- used for deterministic HMAC lookup tokens

### 6. Signing key (`SIG`)

- tenant-scoped or system-scoped signing key
- signs:
  - record manifests
  - export manifests
  - provenance envelopes
  - audit attestations

## Object Classes

### Public profile objects

- may remain plaintext
- should still be signed for provenance and integrity

### Restricted profile objects

- encrypt sensitive subfields only
- example:
  - private notes
  - unreleased allocation evidence
  - customer-linked workflow state

### People and contact objects

- default to encrypted storage
- blind indexes for:
  - normalized email
  - domain
  - phone token
  - entity id

### Export bundles

- always encrypted and signed
- decryption key must be bundle-scoped
- expiry and revocation metadata required

### AI transcripts and prompt bundles

- encrypted at rest
- signed summary manifest
- raw provider exchanges retained only under explicit policy and TTL

## Envelope Format

Every protected object should carry a trust envelope beside or around the record payload.

### Required fields

- `schema_version`
- `object_type`
- `object_id`
- `object_version`
- `tenant_id`
- `classification`
- `cipher_suite`
- `key_wrap_mode`
- `wrapped_dek`
- `nonce`
- `aad`
- `ciphertext`
- `blind_indexes`
- `signatures`
- `provenance`
- `created_at`
- `key_version`

### Example envelope

```json
{
  "schema_version": "swfi.trust_envelope.v1",
  "object_type": "person_contact",
  "object_id": "person_598cdaa6",
  "object_version": "2026-04-22T10:30:00Z",
  "tenant_id": "swfi_core",
  "classification": "restricted_pii",
  "cipher_suite": "xchacha20-poly1305",
  "key_wrap_mode": "kms+wrapped_dek",
  "wrapped_dek": "base64...",
  "nonce": "base64...",
  "aad": {
    "entity_id": "entity_123",
    "field_scope": ["email", "phone", "direct_notes"],
    "key_version": "person_contact.v3"
  },
  "ciphertext": "base64...",
  "blind_indexes": {
    "email_hmac": "hex...",
    "domain_hmac": "hex...",
    "entity_hmac": "hex..."
  },
  "signatures": [
    {
      "algorithm": "ed25519",
      "signing_scope": "manifest",
      "key_id": "sig.swfi_core.v2",
      "signature": "base64..."
    }
  ],
  "provenance": {
    "source_system": "swfi_sandbox_api/people",
    "retrieved_at": "2026-04-22T10:28:10Z",
    "confidence": "high"
  },
  "created_at": "2026-04-22T10:30:00Z",
  "key_version": "person_contact.v3"
}
```

## Blind Index Rules

Blind indexes are required when SWFI needs lookup without plaintext disclosure.

Allowed use:

- exact email lookup
- exact domain lookup
- exact entity linkage
- stable export dedupe

Not allowed:

- free-text search over encrypted fields without a separate search service
- fuzzy search using raw decrypted data in the application layer

## Export Bundle Format

Exports should use a signed bundle, not raw CSV attachment logic alone.

### Export components

- payload file
- manifest file
- signature file
- wrapped bundle key
- expiration policy

### Export manifest fields

- `bundle_id`
- `tenant_id`
- `client_id`
- `created_at`
- `expires_at`
- `row_count`
- `field_list`
- `classification`
- `source_snapshot_ids`
- `hashes`
- `signatures`

## AI Transcript Protection

### Protect

- prompt bundle
- retrieved evidence set
- model output
- reviewer edits
- final published answer

### Rules

- redact secrets and credentials before provider submission
- encrypt full prompt/result logs at rest
- sign the published answer manifest
- separate internal model trace from client-visible answer
- apply TTL to raw provider payload retention

## Rotation

### Rotate on schedule

- signing keys: every 6 to 12 months
- domain protection keys: every 90 to 180 days
- blind index keys: only with planned reindex migration

### Rotate immediately on

- suspected key exposure
- staff departure with privileged custody
- provider compromise
- tenant separation event

## Revocation

A revoked bundle or key must cause:

- export download denial
- audit event append
- UI-visible invalidation state
- optional forced reissue with new bundle id

## Logging

Never log:

- plaintext contact fields
- decrypted transcript bodies
- raw DEKs
- wrapped key material beyond stable identifiers

Always log:

- object id
- tenant id
- key version
- actor
- action
- result
- timestamp

## Implementation Path

### Phase 1

- signed manifests
- bundle-scoped export encryption
- field-level person/contact encryption
- blind indexes for email/domain/entity

### Phase 2

- AI transcript envelopes
- tenant-scoped signing
- revocation service

### Phase 3

- hardware-backed signing
- automated key rotation orchestration
- customer-specific key custody options

## Product Claim

SWFI should describe this as:

`field-level protected institutional intelligence with signed provenance and controlled export delivery`

Not:

`our own encryption algorithm`
