# SWFI Crypto Governance v0.1

## Purpose

Cryptography without governance becomes fragile theater.

SWFI needs governance for:

- key custody
- rotation
- access approval
- export issuance
- AI transcript handling
- incident response
- evidence and audit review

## Non-Negotiable Rules

- no custom cryptographic primitives
- no plaintext storage of restricted contact or transcript payloads
- no direct use of root or tenant master keys for record encryption
- no export release without manifest signing
- no provider transcript retention outside policy
- no secret material in application logs

## Roles

### 1. Security authority

- owns crypto policy
- approves primitive choices
- approves key lifecycle standards
- signs off on rotation and revocation events

### 2. Platform operator

- runs the services
- cannot access root keys directly
- can request export issuance and operational rotation

### 3. Data steward

- approves field classifications
- decides which fields require encryption, signing, or blind indexing

### 4. Reviewer / analyst

- can view authorized decrypted material through product workflows
- cannot export unrestricted raw payloads without policy approval

### 5. Client admin

- receives client-scoped bundles
- can validate signatures
- cannot access other tenant material

## Classification Policy

Every field family must be assigned one of:

- `public`
- `internal`
- `restricted`
- `restricted_pii`
- `export_confidential`

### Required treatment

- `public`: sign if important, encrypt optional
- `internal`: sign, encrypt if workflow-sensitive
- `restricted`: encrypt and sign
- `restricted_pii`: encrypt, sign, and blind-index only where justified
- `export_confidential`: encrypt, sign, expire, and revoke-capable

## Key Governance

### Root key

- hardware or KMS-backed only
- dual-control for rotation or destruction
- never visible to app operators

### Tenant master keys

- generated and wrapped under root
- one tenant per key domain
- access only through KMS/HSM policy

### Signing keys

- separate from encryption keys
- versioned
- revocable
- visible in manifests by key id only

## Rotation Governance

Rotation events require:

- ticket or change record
- actor identity
- reason
- impacted domains
- rollback posture
- completion attestation

### Safe rotation pattern

1. create new key version
2. mark as write-primary
3. continue read support for previous version
4. re-encrypt or re-sign in background
5. retire old version after verification window

## Export Governance

Exports are the highest-risk surface.

### Required controls

- client-scoped bundle id
- signed manifest
- expiration timestamp
- revocation capability
- actor attribution
- purpose label

### Export approvals

- self-service only for approved low-risk bundles
- stepped approval for high-risk or broad contact exports
- mandatory audit event for every issuance and download

## AI Governance Interlock

The AI system must obey the crypto system.

### Required rules

- prompt context built from authorized decrypted records only
- raw prompt bundles encrypted at rest
- provider request logs minimized
- published answer signed as a separate object
- reviewer edits stored in the audit trail

### Provider rules

- OpenAI is primary
- Anthropic is first fallback
- Gemini is second fallback
- deterministic SWFI fallback remains available if providers fail

## Incident Response

### Trigger conditions

- suspected key leak
- export bundle exposure
- unauthorized transcript access
- compromised operator account
- tenant isolation breach

### Required actions

1. freeze affected export issuance
2. revoke active bundle keys if needed
3. rotate affected domain keys
4. preserve signed audit trail
5. issue impact summary
6. restore only after verification

## Audit Requirements

Every critical crypto event must log:

- event id
- actor id
- role
- tenant id
- object or bundle id
- key version
- action
- result
- timestamp

Examples:

- envelope created
- envelope decrypted
- export issued
- export downloaded
- key rotated
- key revoked
- transcript purged

## Change Management

Any change to:

- cipher suite
- key hierarchy
- provider retention rules
- export issuance logic
- transcript retention

must require:

- security review
- test evidence
- rollback path
- version bump in the trust-envelope spec

## Success Standard

SWFI should be able to say:

`restricted institutional data is encrypted, signed, versioned, auditable, and revocable under a governed key system`

and defend every part of that claim.
