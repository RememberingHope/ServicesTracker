# SPED & MTSS Services Tracking Suite - Implementation Brief

## System Overview

This suite consists of three **independent** Python applications designed to work together through a data pipeline, but deployed on separate computers:

1. **QR Code Maker** - Creates encrypted QR codes for service tracking
2. **Services Tracker** - Kiosk app for logging services via QR scanning
3. **Services Aggregator** - Dashboard for collecting and analyzing service data

## Deployment Architecture

```
[Admin Computer]
├── QR_Code_Maker.py      (Creates QR cards with various PINs)
└── Services_Aggregator.py (Pulls data from multiple email sources)

[Classroom Kiosk A]
└── Services_Tracker.py    (PIN: 1234, Email: roomA@school.edu)

[Classroom Kiosk B]
└── Services_Tracker.py    (PIN: 5678, Email: roomB@school.edu)

[Resource Room Kiosk]
└── Services_Tracker.py    (PIN: 1234, Email: resource@school.edu)
```

## Data Flow

1. **QR Creation** (Admin Computer)
   - Admin creates QR codes with specific PINs for different purposes
   - Cards are printed and distributed to classrooms
   - Different card sets may use different PINs

2. **Service Tracking** (Kiosk Computers)
   - Staff scans QR codes to log services
   - Each kiosk has its own PIN configuration
   - Data is saved locally and emailed as CSV attachments
   - Multiple kiosks may use the same PIN if they share card sets

3. **Data Aggregation** (Admin Computer)
   - Aggregator monitors multiple email accounts
   - Downloads CSV attachments from all trackers
   - May encounter data with different PINs from different sources
   - Compiles unified reports and analytics

## Security Model

### PIN Encryption Purpose
- **Primary Goal**: Prevent unauthorized QR code scanning with phone cameras
- **Not For**: Application-level security or user authentication
- **Implementation**: Symmetric encryption using PIN-derived keys

### PIN Management
- **QR Code Maker**: PIN entered per batch of QR codes created
- **Services Tracker**: PIN stored in OS keyring for the kiosk session
- **Services Aggregator**: PIN entered when decrypting specific data sources

### Data Security Levels
1. **QR Codes**: Encrypted with PIN (protects printed cards)
2. **CSV Files**: May contain encrypted fields
3. **Email Transit**: Uses SMTP/TLS
4. **Local Storage**: SQLite databases (consider encryption at rest)

## Critical Fixes Required

### Priority 1: Security Vulnerabilities
- [x] Replace `eval()` with `json.loads()` in Services_Tracker.py
- [x] Move PIN storage from database to OS keyring
- [ ] Implement PBKDF2 key derivation instead of simple SHA-256
- [ ] Validate all JSON input against schema

### Priority 2: Data Integrity
- [ ] Change duration/score columns from TEXT to REAL in databases
- [ ] Add schema_version field for future migrations
- [ ] Implement duplicate detection in aggregator
- [ ] Add data validation before database insertion

### Priority 3: Reliability
- [ ] Add error recovery for failed email sends
- [ ] Implement local backup of service logs
- [ ] Add connection retry logic for email operations
- [ ] Create audit logs for all data operations

## JSON Schema Specification

### QR Code Payload (v1)
```json
{
  "v": 1,
  "type": "service|goal|behavior",
  "student": "First Last",
  "student_key": "ABC123",
  "service": "Reading Support",
  "default_duration": 30,
  "goal_id": "G-2025-001",
  "metadata": {
    "created": "2025-01-15T10:00:00Z",
    "creator": "admin_id"
  }
}
```

### CSV Export Format
```csv
id,timestamp,student,service,duration,event,score,goal_id,device_id,schema_version
1,2025-01-15 10:30:00,John Doe,Reading,30,session,85,G-2025-001,KIOSK-A,1
```

## Database Schemas

### Services Tracker (services_data.db)
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    student_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    service TEXT,
    duration REAL,  -- Changed from TEXT
    event TEXT,
    score REAL,     -- Changed from TEXT
    goal_id TEXT,
    device_id TEXT,
    schema_version INTEGER DEFAULT 1,
    reported INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Services Aggregator (aggregated_services.db)
```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    student TEXT NOT NULL,
    student_key TEXT,
    service TEXT,
    duration REAL,  -- Changed from TEXT
    event TEXT,
    score REAL,     -- Changed from TEXT
    goal_id TEXT,
    source_email TEXT,
    source_file TEXT,
    device_id TEXT,
    schema_version INTEGER DEFAULT 1,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, student, service, duration, device_id)  -- Prevent duplicates
);

CREATE TABLE import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_uid TEXT,
    filename TEXT,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_count INTEGER,
    status TEXT
);
```

## Enhanced Features Roadmap

### Phase 1: Core Improvements (Immediate)
- [ ] Fix security vulnerabilities
- [ ] Update database schemas
- [ ] Add JSON validation
- [ ] Improve error handling

### Phase 2: QR Code Maker Enhancements
- [ ] Template system for common card types
- [ ] Batch QR generation
- [ ] Print layout templates (3x5 cards, etc.)
- [ ] QR code testing interface
- [ ] Export QR sets with metadata

### Phase 3: Services Tracker Improvements
- [ ] One-tap recording mode
- [ ] Soft delete with undo
- [ ] Automatic daily backups
- [ ] Offline mode with sync queue
- [ ] Session timer for duration tracking
- [ ] Quick-access buttons for frequent services

### Phase 4: Aggregator Dashboard Features
- [ ] Multi-source PIN management
- [ ] Duplicate detection and merging
- [ ] Data visualization charts
- [ ] PDF report generation
- [ ] Student progress tracking
- [ ] Goal achievement analytics
- [ ] Export to compliance reporting formats

### Phase 5: System-Wide Enhancements
- [ ] REST API for direct data submission (replace SMTP)
- [ ] Web-based dashboard option
- [ ] Mobile companion app for tablets
- [ ] Integration with SIS systems
- [ ] Automated compliance reporting

## Testing Requirements

### Unit Tests
- Encryption/decryption with various PINs
- JSON schema validation
- Database operations
- CSV parsing and generation
- Email sending/receiving

### Integration Tests
- Full workflow: QR creation → scanning → emailing → aggregation
- Multiple PIN scenarios
- Network failure recovery
- Data consistency across apps

### User Acceptance Criteria
- QR scan to save: < 3 seconds
- Email send success rate: > 99%
- Data aggregation accuracy: 100%
- PIN mismatch handling: Clear error messages
- Kiosk mode stability: 24/7 operation

## Deployment Checklist

### QR Code Maker + Aggregator (Admin Computer)
- [ ] Python 3.8+ installed
- [ ] Required packages: tkinter, PIL, qrcode, cryptography, imaplib
- [ ] Email account credentials for aggregation
- [ ] Printer access for QR cards

### Services Tracker (Kiosk Computers)
- [ ] Python 3.8+ installed
- [ ] Required packages: tkinter, opencv-python, cryptography, keyring
- [ ] Webcam for QR scanning
- [ ] SMTP credentials configured
- [ ] Kiosk mode auto-start configured
- [ ] Touchscreen (optional but recommended)

## Dependencies

```txt
# Core Requirements
tkinter (built-in)
sqlite3 (built-in)

# QR Code Maker
qrcode[pil]>=7.3
Pillow>=9.0
cryptography>=41.0

# Services Tracker
opencv-python>=4.5
cryptography>=41.0
keyring>=23.0

# Services Aggregator
cryptography>=41.0
matplotlib>=3.5  # For future charts
reportlab>=3.6   # For future PDF generation
```

## Configuration Management

### Environment Variables (Optional)
```bash
# Services Tracker
SPED_TRACKER_DB="services_data.db"
SPED_TRACKER_KIOSK_ID="KIOSK-A"
SPED_TRACKER_BACKUP_DIR="./backups"

# Aggregator
SPED_AGGREGATOR_DB="aggregated_services.db"
SPED_AGGREGATOR_ATTACH_DIR="./attachments"
```

### Settings Storage
- **Credentials**: OS Keyring (never in plaintext)
- **PINs**: OS Keyring for Tracker, runtime memory for others
- **Preferences**: SQLite settings table
- **Email configs**: OS Keyring

## Maintenance Procedures

### Daily
- Verify kiosk apps are running
- Check email send queue
- Review error logs

### Weekly
- Run aggregator to compile reports
- Clear old CSV attachments
- Backup databases

### Monthly
- Update QR card sets as needed
- Review PIN security
- Check for software updates
- Audit data accuracy

## Support Documentation

### Common Issues
1. **PIN Mismatch**: Verify same PIN used for QR creation and tracker
2. **Email Failed**: Check SMTP credentials and network connection
3. **QR Won't Scan**: Ensure good lighting and camera focus
4. **Duplicate Data**: Check if multiple trackers sending to same email

### Troubleshooting Steps
1. Check error messages in app
2. Verify PIN configuration
3. Test email credentials
4. Review local database for data
5. Check network connectivity

## Version History

- **v1.0** - Initial implementation with basic features
- **v1.1** - Security fixes (eval removal, keyring storage)
- **v1.2** - (Planned) PBKDF2 encryption, JSON validation
- **v2.0** - (Future) REST API, web dashboard

## Notes for Developers

1. **Each app is standalone** - No shared code dependencies
2. **PIN compatibility** - All apps must use identical encryption methods
3. **Schema versioning** - Always include version field for future migrations
4. **Error handling** - Fail gracefully, log errors, provide user feedback
5. **Privacy first** - Minimize PII in QR codes, use student keys when possible

---

*Last Updated: [Current Date]*
*Document Version: 1.0*