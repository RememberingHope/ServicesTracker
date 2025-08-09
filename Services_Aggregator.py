# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 13:24:49 2025

@author: jrember
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import imaplib
import email
import os
import sqlite3
import csv
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

DB_FILE = "aggregated_services.db"
ATTACH_DIR = "attachments"

# Encryption helpers (compatible with Services_Tracker.py)
def get_fernet_key_from_pin(pin, salt=None):
    """Derive a Fernet key from PIN using PBKDF2 for better security."""
    if salt is None:
        # Use a fixed salt for backward compatibility
        # In production, should use random salt stored with encrypted data
        salt = b'sped_tracker_salt_v1'
    
    # Use PBKDF2 with 100,000 iterations for key derivation
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(pin.encode('utf-8')))
    return key

def decrypt_data(encrypted_text, pin):
    """Decrypt data using PIN-derived key."""
    key = get_fernet_key_from_pin(pin)
    f = Fernet(key)
    try:
        decrypted = f.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
        return decrypted
    except Exception:
        # Try with legacy SHA256 for backward compatibility
        try:
            # Old method for existing encrypted data
            hash = hashlib.sha256(pin.encode('utf-8')).digest()
            legacy_key = base64.urlsafe_b64encode(hash)
            f_legacy = Fernet(legacy_key)
            decrypted = f_legacy.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
            return decrypted
        except:
            return None

class ServiceAggregatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Service Log Aggregator")
        self.geometry("950x600")
        self.resizable(True, True)
        self.imap_server = tk.StringVar(value="imap.office365.com")
        self.email_user = tk.StringVar()
        self.email_pass = tk.StringVar()
        self.subject = tk.StringVar(value="SPED Service Log")
        self.pin = tk.StringVar()
        self.data = []
        self.create_widgets()
        self.init_db()

    def create_widgets(self):
        # Email Login
        frame = tk.LabelFrame(self, text="Email Settings")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="IMAP Server:").grid(row=0, column=0, sticky="e")
        tk.Entry(frame, textvariable=self.imap_server, width=22).grid(row=0, column=1, sticky="w", padx=2)
        tk.Label(frame, text="Email:").grid(row=0, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.email_user, width=24).grid(row=0, column=3, sticky="w", padx=2)
        tk.Label(frame, text="Password:").grid(row=0, column=4, sticky="e")
        tk.Entry(frame, textvariable=self.email_pass, show="*", width=20).grid(row=0, column=5, sticky="w", padx=2)

        tk.Label(frame, text="Subject Filter:").grid(row=1, column=0, sticky="e")
        tk.Entry(frame, textvariable=self.subject, width=22).grid(row=1, column=1, sticky="w", padx=2)
        tk.Label(frame, text="Decrypt PIN (if used):").grid(row=1, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.pin, show="*", width=24).grid(row=1, column=3, sticky="w", padx=2)
        tk.Button(frame, text="Fetch & Aggregate", command=self.fetch_and_aggregate).grid(row=1, column=5, padx=12, sticky="w")

        # Data Table
        self.tree = ttk.Treeview(self, columns=("Timestamp", "Student", "Service", "Duration", "Event", "Score"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="w")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Export to CSV", command=self.export_csv).pack(side="left")
        tk.Button(btn_frame, text="Show Summary", command=self.show_summary).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Clear Table", command=self.clear_table).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Exit", command=self.destroy).pack(side="right")
        self.status = tk.Label(self, text="Ready", anchor="w")
        self.status.pack(fill="x", padx=10, pady=5)

    def init_db(self):
        if not os.path.exists(ATTACH_DIR):
            os.makedirs(ATTACH_DIR)
        self.conn = sqlite3.connect(DB_FILE)
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                student TEXT,
                service TEXT,
                duration REAL,
                event TEXT,
                score REAL,
                goal_id TEXT,
                device_id TEXT,
                source_email TEXT,
                source_file TEXT,
                schema_version INTEGER DEFAULT 1,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, student, service, device_id)
            )
        ''')
        
        # Create import log table
        c.execute('''
            CREATE TABLE IF NOT EXISTS import_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_uid TEXT,
                filename TEXT,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                record_count INTEGER,
                duplicates_skipped INTEGER,
                status TEXT
            )
        ''')
        self.conn.commit()

    def fetch_and_aggregate(self):
        self.status.config(text="Connecting to mail server...")
        self.update_idletasks()
        # Clear table and data
        self.clear_table()
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server.get())
            mail.login(self.email_user.get(), self.email_pass.get())
            mail.select("inbox")
            # Search for emails with specified subject
            search_criteria = f'(SUBJECT "{self.subject.get()}")'
            status, messages = mail.search(None, search_criteria)
            email_ids = messages[0].split()
            self.status.config(text=f"Found {len(email_ids)} emails. Downloading attachments...")
            self.update_idletasks()
            for email_id in email_ids:
                _, msg_data = mail.fetch(email_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        for part in msg.walk():
                            if part.get_content_maintype() == "multipart":
                                continue
                            if part.get("Content-Disposition") is None:
                                continue
                            filename = part.get_filename()
                            if filename and filename.endswith(".csv"):
                                filepath = os.path.join(ATTACH_DIR, filename)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                self.import_csv(filepath, self.email_user.get(), filename)
            mail.logout()
            self.load_data_to_table()
            
            # Get import summary
            cur = self.conn.cursor()
            cur.execute('''
                SELECT SUM(record_count), SUM(duplicates_skipped) 
                FROM import_log 
                WHERE datetime(imported_at) > datetime('now', '-1 minute')
            ''')
            result = cur.fetchone()
            total_imported = result[0] or 0
            total_skipped = result[1] or 0
            
            self.status.config(text=f"Imported {total_imported} records from {len(email_ids)} emails ({total_skipped} duplicates skipped)")
            messagebox.showinfo("Import Complete", 
                              f"Fetched data from {len(email_ids)} emails\n\n"
                              f"Records imported: {total_imported}\n"
                              f"Duplicates skipped: {total_skipped}")
        except Exception as e:
            self.status.config(text="Error fetching emails")
            messagebox.showerror("Error", f"Could not fetch emails: {e}")

    def import_csv(self, filepath, source_email=None, source_file=None):
        records_imported = 0
        duplicates_skipped = 0
        
        with open(filepath, newline="") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            for row in reader:
                # Decrypt each field if pin is provided and value is not empty
                if self.pin.get():
                    # Only attempt decryption on fields that are not empty
                    row = [self.try_decrypt(cell) if cell else "" for cell in row]
                
                if self.save_service(row, source_email, source_file):
                    records_imported += 1
                else:
                    duplicates_skipped += 1
        
        # Log the import
        with self.conn:
            self.conn.execute('''
                INSERT INTO import_log (filename, record_count, duplicates_skipped, status)
                VALUES (?, ?, ?, ?)
            ''', (source_file, records_imported, duplicates_skipped, 'success'))
        
        return records_imported, duplicates_skipped

    def try_decrypt(self, value):
        # Try to decrypt, else return as is
        decrypted = decrypt_data(value, self.pin.get())
        return decrypted if decrypted is not None else value

    def save_service(self, row, source_email=None, source_file=None):
        # row: [ID, Timestamp, Student, Service, Duration, Event, Score, Goal_ID, Device_ID, Reported]
        # Store all relevant fields from new schema
        if len(row) >= 7:
            # Convert duration and score to float
            duration_val = None
            if row[4]:
                try:
                    duration_val = float(row[4])
                except (ValueError, TypeError):
                    duration_val = None
            
            score_val = None
            if row[6]:
                try:
                    score_val = float(row[6])
                except (ValueError, TypeError):
                    score_val = None
            
            goal_id = row[7] if len(row) > 7 else None
            device_id = row[8] if len(row) > 8 else None
            
            try:
                with self.conn:
                    self.conn.execute('''
                        INSERT OR IGNORE INTO services (timestamp, student, service, duration, event, score, 
                                            goal_id, device_id, source_email, source_file, schema_version)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (row[1], row[2], row[3], duration_val, row[5], score_val, 
                         goal_id, device_id, source_email, source_file))
                return True  # Successfully inserted
            except sqlite3.IntegrityError:
                return False  # Duplicate, skipped

    def load_data_to_table(self):
        self.tree.delete(*self.tree.get_children())
        cur = self.conn.cursor()
        cur.execute("SELECT timestamp, student, service, duration, event, score FROM services")
        self.data = cur.fetchall()
        for row in self.data:
            self.tree.insert("", "end", values=row)

    def export_csv(self):
        if not self.data:
            messagebox.showinfo("No Data", "No data to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Student", "Service", "Duration", "Event", "Score"])
            for row in self.data:
                writer.writerow(row)
        messagebox.showinfo("Exported", f"Data exported to {path}")

    def show_summary(self):
        cur = self.conn.cursor()
        cur.execute("SELECT student, COUNT(*), SUM(CAST(duration AS FLOAT)) FROM services GROUP BY student")
        summary = cur.fetchall()
        text = "Student | # Services | Total Duration\n"
        text += "\n".join(f"{s} | {c} | {d or 0}" for s, c, d in summary)
        messagebox.showinfo("Summary", text)

    def clear_table(self):
        self.tree.delete(*self.tree.get_children())
        # Clear DB for a new aggregation session
        with self.conn:
            self.conn.execute("DELETE FROM services")
        self.data = []

if __name__ == "__main__":
    app = ServiceAggregatorApp()
    app.mainloop()
