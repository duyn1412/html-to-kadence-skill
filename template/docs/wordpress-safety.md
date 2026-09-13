# WordPress Update Safety & Concurrency Protocol (v1.1.0)

> **Golden Rule**: Never execute an unverified, destructive overwrite on a live WordPress site. All mutations must follow optimistic concurrency control, local backup snapshots, draft-first staging, and round-trip serialization validation.

---

## 1. Optimistic Concurrency Control

When modifying an existing WordPress page via the REST API, multiple contributors or automated agents may be editing simultaneously. To prevent overwriting newer changes:

```
  ┌─────────────────────────────────────────────────────────────┐
  │ Step 1: Pre-conversion Fetch (GET /wp/v2/pages/{id}?context=edit)
  │ Store:                                                      │
  │   - live_content_raw                                        │
  │   - live_modified_gmt                                       │
  │   - content_sha256 = sha256(live_content_raw)               │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ Step 2: Conversion & QA Validation Pipeline                  │
  │   (Generate blocks, run QA Engine, achieve PASS)            │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
  ┌──────────────────────────────▼──────────────────────────────┐
  │ Step 3: Concurrency Verification Check                      │
  │ GET /wp/v2/pages/{id}?context=edit immediately before write │
  │ Check if current_sha256 == stored_sha256                    │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
        [MISMATCH]                               [MATCH]
   Live page was changed!                   Page is unchanged
   ABORT with error code:                   Proceed to update
   LIVE_CONTENT_CHANGED_ABORTED
```

### Abort Action: `LIVE_CONTENT_CHANGED_ABORTED`
If `current_sha256 !== stored_sha256` or `modified_gmt` has advanced:
1. Immediately abort the update.
2. Log the conflict details: timestamp of external change, user who modified (if available).
3. Do not proceed until human review or an explicit re-fetch & merge is triggered.

---

## 2. Local Backup & Snapshot Policy

Before any `PUT` or `POST` request modifying `content.raw` on WordPress:
1. Save the previous live state locally:
   ```
   .backups/pages/{pageId}_{timestamp}.raw.txt
   .backups/pages/{pageId}_{timestamp}.meta.json
   ```
2. The metadata snapshot records:
   - `page_id`: WordPress Post ID
   - `slug`: Page slug
   - `title`: Post title
   - `status`: Current status (`publish`, `draft`, etc.)
   - `modified_gmt`: ISO timestamp
   - `sha256`: SHA-256 hash of previous content

---

## 3. Draft-First Publishing Policy

Direct-to-production publishing is strictly prohibited during automated pipelines.
- **Default Publishing Status**: `draft`.
- If the page is already `publish`, updates must be made during maintenance windows or explicitly requested by the user.
- Even when updating a live page, automated scripts must generate a preview link and await human approval before marking the conversion complete.

---

## 4. Round-Trip Serialization QA

Gutenberg stores block content as HTML comments with JSON attributes in `post_content`. When WordPress saves a post:
1. The WP REST API runs content through sanitization and block processing filters.
2. Plugins (or core Gutenberg) may rewrite attributes or trigger block invalidation.

### Verification Flow:
```
  [Generated Block Markup]
            │
            ▼ (PUT /wp/v2/pages/{id})
  [WordPress Database]
            │
            ▼ (GET /wp/v2/pages/{id}?context=edit)
  [Fetched content.raw]
            │
            ▼
  [Compare AST / Normalization]
```

### Invariance Rules:
- If `ROUND_TRIP_CHANGED_MARKUP` occurs:
  - Check whether Kadence attributes were stripped (e.g. `uniqueID`, `fontSize`).
  - Verify that no HTML entity double-encoding occurred (`&amp;amp;`).
  - Verify that Gutenberg didn't inject block recovery comments (`<!-- wp:missing ... -->`).
- If material differences exist between sent and returned markup, flag `ROUND_TRIP_CHANGED_MARKUP` and reject the QA gate.

---

## 5. Emergency Rollback Procedures

If an automated update causes visual regression or editor errors on a live site:
1. **Immediate Restore from Backup Snapshot**:
   ```bash
   python3 scripts/restore-page.py --page-id 7898 --backup .backups/pages/7898_latest.raw.txt
   ```
2. **WordPress Core Revisions**:
   - Access `WP-Admin > Pages > Edit Page > Revisions`.
   - Restore the revision created immediately prior to the API update timestamp.
