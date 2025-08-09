# Special Education & MTSS Tracking Suite Development Brief

This suite consists of three interconnected Python desktop applications designed to streamline the capture, aggregation, and reporting of student service data for Special Education (SPED) and Multi-Tiered System of Supports (MTSS). The goal is to make data entry effortless for staff, ensure secure and accurate transport of data, and provide powerful analytics and reporting tools.

---

## **App 1: QR Code Maker for Services Tracker**

### **Purpose**

Generates QR codes that encapsulate structured data (e.g., IEP goals, behavioral events, or service information). The QR codes can be printed on cards and scanned in the Tracker app for quick, consistent data entry.

### **Current Features**

- UI for entering label and payload text.
- Optional encryption of payload with PIN-derived Fernet key.
- QR code rendered with top label and saved as PNG.
- Encryption method is consistent with Tracker and Aggregator apps.

### **Strengths**

- Encryption interoperability across all apps.
- Simple, functional QR generation.

### **Gaps / Risks**

- Payload is free-text with no enforced schema.
- No template builder for common goal/event cards.

### **Required Enhancements**

1. **Force JSON Schema**

   - All QR payloads must follow a standardized JSON schema.
   - Include a `schema_version` for forward compatibility.

2. **Template Builder**

   - Dropdown for common templates (Goal, Service, Behavior).
   - Auto-fill fields to reduce manual typing errors.

3. **Print Layout**

   - N-up print sheets for cards (3×5 or other common sizes).
   - Include both QR code and human-readable details.

4. **Security Improvements**

   - Salted key derivation (PBKDF2/Argon2) instead of deterministic SHA-256.
   - Optionally store salt inside QR payload.

---

## **App 2: Services Tracker (Kiosk)**

### **Purpose**

Touchscreen-optimized kiosk app for recording service events by scanning QR codes. Designed for constant display in classrooms.

### **Current Features**

- Full-screen kiosk mode with on-screen numeric keypad.
- QR scan populates data fields and timestamps the event.
- Stores student/service data in local SQLite DB.
- Can send service logs via SMTP (Gmail, Microsoft, etc.).
- Allows adding students on the fly.

### **Strengths**

- Practical one-tap workflow.
- Multi-provider SMTP support with saved credentials in OS keyring.
- Supports deleting events if entered in error.

### **Gaps / Risks**

- Uses `eval` for parsing QR JSON (critical security risk).
- Encryption PIN stored in DB as plaintext.
- Duration and score stored as text instead of numeric.
- Outbound CSV not encrypted at rest.

### **Required Enhancements**

1. **Security Fixes (High Priority)**

   - Replace `eval` with `json.loads`.
   - Validate schema before saving data.
   - Store encryption PIN in OS keyring.

2. **Data Model Updates**

   - Store `duration` and `score` as REAL (numeric) values.
   - Add `schema_version` and `device_id` columns.

3. **Workflow Improvements**

   - One-tap macros: only show fields requiring user input after scan.
   - Soft delete for error correction.
   - Daily local CSV backup.

4. **Security in Transit**

   - Long-term: Replace SMTP with HTTPS/Graph API upload.

---

## **App 3: Services Aggregator**

### **Purpose**

Pulls service logs from an email inbox, aggregates them into a local database, and provides dashboards for analysis and reporting.

### **Current Features**

- IMAP fetch of messages by subject.
- Downloads CSV attachments to `attachments/` folder.
- Imports data into SQLite `services` table.
- Optional decryption of fields if PIN is provided.
- Basic table view and CSV export.

### **Strengths**

- Simple, functional email-to-database pipeline.
- Compatible encryption handling with Tracker and QR Maker.

### **Gaps / Risks**

- Imports assume consistent CSV header order; no validation.
- Decrypts all fields indiscriminately.
- No duplicate detection.
- Limited charting/analysis.

### **Required Enhancements**

1. **Import Hardening**

   - Validate CSV headers before import.
   - Reject or flag mismatched files.
   - Log email UID and filename for audit trail.

2. **Schema Improvements**

   - Store duration/score as REAL.
   - Track `schema_version` for future migrations.

3. **Decryption Optimization**

   - Only decrypt known encrypted columns.

4. **Dashboard & Reporting**

   - Filters for student, service, date range, event type.
   - Matplotlib/Plotly charts (trends, totals, comparisons).
   - PDF export with charts and narrative summaries.

5. **Duplicate Detection**

   - Deduplicate by `(student, timestamp, service, duration, device_id)`.

---

## **Shared Architecture Goals**

### **Unified Data Model**

All apps should conform to a single SQLite schema, ready for migration to Postgres later.

```sql
students(id, student_key, name, grade, tags)
events(id, student_id, ts_utc, source, device_id, user_id, event_type,
       service, duration_minutes REAL, score REAL, notes, goal_id,
       raw_payload, schema_version)
goals(id, student_id, code, description, measurement_type, target,
      start_date, end_date)
reports(id, created_at, report_type, params_json, file_path)
```

### **Canonical QR Schema (JSON)**

```json
{
  "v": 1,
  "type": "goal|behavior|service",
  "student": "First Last",
  "student_key": "ABC123",
  "service": "Reading pull-out",
  "default_duration": 15,
  "event": "session_start|session_end|incident|success",
  "score": null,
  "goal_id": "G-2025-001"
}
```

- Always JSON.
- Encrypt entire JSON string if PIN is used.

### **Security & Privacy**

- Minimal PII in QR codes (prefer `student_key`).
- OS keyring for all secrets.
- No `eval` anywhere.
- TLS in transit; encrypted storage for sensitive fields.
- PDF reports must support redacted/initials-only mode.

---

## **Deployment Plan**

- Package each app with PyInstaller.
- Kiosk auto-launch via Task Scheduler.
- Aggregator as Tk app now, with possible future migration to Flask/FastAPI.
- QR Maker with print-friendly UI.

---

## **Testing Plan**

- Unit tests: QR schema round-trip, encryption helpers, CSV validation.
- Integration tests: simulated QR scan → tracker save → SMTP send → IMAP fetch → aggregator import → dashboard display.
- Usability: time "scan → save" under 3 seconds.
- Data integrity: deduplication, migration handling, invalid file rejection.

---

## **Immediate Next Steps**

1. Remove `eval` from Tracker and replace with `json.loads` + schema validation.
2. Move encryption PIN storage to OS keyring in Tracker.
3. Implement QR JSON schema and template builder in QR Maker.
4. Add CSV header validation and audit logging in Aggregator.
5. Migrate `duration` and `score` columns to REAL type in all DBs.

