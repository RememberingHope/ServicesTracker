# -*- coding: utf-8 -*-
"""
Created on Tue May 27 12:48:43 2025

@author: jrember
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import cv2
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os
import sqlite3
import csv
import keyring
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
import json

DB_FILE = "services_data.db"
KEYRING_SERVICE = "sped_service_app"
KEYRING_PIN_KEY = "encryption_pin"  # Key for storing PIN in keyring
PROVIDERS = {
    "Microsoft": {
        "email_key": "microsoft_email",
        "password_key": "microsoft_password",
        "smtp_server": "smtp.office365.com",
        "smtp_port": 587,
        "use_ssl": False,
        "needs_starttls": True,
        "friendly": "Microsoft 365/Outlook"
    },
    "Google": {
        "email_key": "google_email",
        "password_key": "google_password",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 465,
        "use_ssl": True,
        "needs_starttls": False,
        "friendly": "Google Workspace/Gmail"
    }
}

# ------------------ Encryption Logic ---------------------
def get_fernet_key_from_pin(pin, salt=None):
    """Derive a Fernet key from PIN using PBKDF2 for better security."""
    if salt is None:
        # Use a fixed salt for backward compatibility
        # In production, should use random salt stored with encrypted data
        salt = b'sped_tracker_salt_v1'
    
    # Use PBKDF2 with 100,000 iterations for key derivation
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(pin.encode('utf-8')))
    return key

def encrypt_data(data, pin):
    """Encrypt data using PIN-derived key."""
    key = get_fernet_key_from_pin(pin)
    f = Fernet(key)
    return f.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_data(encrypted_text, pin):
    """Decrypt data using PIN-derived key."""
    key = get_fernet_key_from_pin(pin)
    f = Fernet(key)
    try:
        decrypted = f.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
        return decrypted
    except InvalidToken:
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

# ------------------ Database Handling ---------------------
class ServiceDB:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    timestamp TEXT,
                    service TEXT,
                    duration REAL,
                    event TEXT,
                    score REAL,
                    goal_id TEXT,
                    device_id TEXT,
                    schema_version INTEGER DEFAULT 1,
                    reported INTEGER DEFAULT 0,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            conn.commit()

    def get_students(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM students ORDER BY name")
            return c.fetchall()

    def add_student(self, name):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO students (name) VALUES (?)", (name,))
            conn.commit()
            c.execute("SELECT id FROM students WHERE name=?", (name,))
            return c.fetchone()[0]

    def log_service(self, student_id, service, duration, event, score, goal_id=None):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            # Convert duration and score to float if they're not empty
            duration_val = None
            if duration:
                try:
                    duration_val = float(duration)
                except ValueError:
                    duration_val = None
            
            score_val = None
            if score:
                try:
                    score_val = float(score)
                except ValueError:
                    score_val = None
            
            # Get device ID from environment or use default
            import platform
            device_id = platform.node() or "UNKNOWN"
            
            c.execute('''INSERT INTO services
                (student_id, timestamp, service, duration, event, score, goal_id, device_id, schema_version, reported)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0)''',
                (student_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), service, 
                 duration_val, event, score_val, goal_id, device_id))
            conn.commit()

    def get_services(self, student_id=None, only_new=False):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            q = "SELECT s.id, s.timestamp, st.name, s.service, s.duration, s.event, s.score, s.goal_id, s.device_id, s.reported FROM services s JOIN students st ON s.student_id=st.id"
            params = []
            if student_id:
                q += " WHERE s.student_id=?"
                params.append(student_id)
                if only_new:
                    q += " AND s.reported=0"
            elif only_new:
                q += " WHERE s.reported=0"
            q += " ORDER BY s.timestamp"
            c.execute(q, params)
            return c.fetchall()

    def mark_services_reported(self, service_ids):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.executemany("UPDATE services SET reported=1 WHERE id=?", [(sid,) for sid in service_ids])
            conn.commit()

    def get_setting(self, key):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM settings WHERE key=?", (key,))
            result = c.fetchone()
            return result[0] if result else ""

    def set_setting(self, key, value):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
            conn.commit()

    def clear_setting(self, key):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM settings WHERE key=?", (key,))
            conn.commit()

# ------------------ QR and Email Functions ---------------------
def scan_qr_code():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    data = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        data, bbox, _ = detector.detectAndDecode(frame)
        cv2.imshow("Scan QR Code (press q to cancel)", frame)
        if data:
            cap.release()
            cv2.destroyAllWindows()
            return data
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return None

def send_email(filename, recipient, sender, password, smtp_settings):
    msg = EmailMessage()
    msg["Subject"] = "SPED Service Log"
    msg["From"] = sender
    msg["To"] = recipient
    with open(filename, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=os.path.basename(filename))
    if smtp_settings["use_ssl"]:
        with smtplib.SMTP_SSL(smtp_settings["smtp_server"], smtp_settings["smtp_port"]) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(smtp_settings["smtp_server"], smtp_settings["smtp_port"]) as smtp:
            if smtp_settings["needs_starttls"]:
                smtp.starttls()
            smtp.login(sender, password)
            smtp.send_message(msg)

# ------------------ Keypad for Numeric Input ---------------------
class Keypad(tk.Toplevel):
    _is_open = False

    def __init__(self, entry, parent=None, *args, **kwargs):
        if Keypad._is_open:
            return
        Keypad._is_open = True
        super().__init__(parent, *args, **kwargs)
        self.title("Keypad")
        self.geometry("400x500")
        self.entry = entry
        self.configure(bg="#e0e0e0")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close_keypad)
        self.build_keys()
        self.center_window()
        self.entry.selection_range(0, tk.END)
        self.entry.icursor(tk.END)
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    def build_keys(self):
        btn_font = ("Arial", 32)
        frame = tk.Frame(self, bg="#e0e0e0")
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            'Back', '0', 'Done'
        ]
        for i, b in enumerate(buttons):
            cmd = lambda x=b: self.key_press(x)
            btn = tk.Button(frame, text=b, command=cmd, font=btn_font, width=4, height=2)
            row, col = divmod(i, 3)
            btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        for i in range(4):
            frame.rowconfigure(i, weight=1)
        for i in range(3):
            frame.columnconfigure(i, weight=1)

    def key_press(self, key):
        if key == "Back":
            current = self.entry.get()
            self.entry.delete(0, tk.END)
            self.entry.insert(0, current[:-1])
        elif key == "Done":
            self.close_keypad()
        else:
            if self.entry.selection_present():
                self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, key)
            self.entry.selection_clear()

    def close_keypad(self):
        Keypad._is_open = False
        self.destroy()

# ------------------ Main App ---------------------
class TouchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = ServiceDB()
        self.title("SPED Service QR Logger")
        self.attributes("-fullscreen", True)
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, '-topmost', False)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.selected_provider = tk.StringVar(value="Microsoft")
        # Load PIN from OS keyring instead of database
        try:
            self.pin = keyring.get_password(KEYRING_SERVICE, KEYRING_PIN_KEY) or ""
        except Exception:
            self.pin = ""
        self.current_goal_id = None  # Store goal_id from QR code
        self.create_menu()
        self.create_widgets()
        self.reset_fields()

    # --- Menu ---
    def create_menu(self):
        menubar = tk.Menu(self)

        provider_menu = tk.Menu(menubar, tearoff=0)
        provider_menu.add_radiobutton(label="Microsoft 365/Outlook", variable=self.selected_provider, value="Microsoft")
        provider_menu.add_radiobutton(label="Google Workspace/Gmail", variable=self.selected_provider, value="Google")
        menubar.add_cascade(label="SMTP Provider", menu=provider_menu)

        cred_menu = tk.Menu(menubar, tearoff=0)
        cred_menu.add_command(label="Set Microsoft Email Credentials", command=lambda: self.set_email_credentials("Microsoft"))
        cred_menu.add_command(label="Set Google Email Credentials", command=lambda: self.set_email_credentials("Google"))
        cred_menu.add_separator()
        cred_menu.add_command(label="Clear Microsoft Credentials", command=lambda: self.clear_email_credentials("Microsoft"))
        cred_menu.add_command(label="Clear Google Credentials", command=lambda: self.clear_email_credentials("Google"))
        menubar.add_cascade(label="Email Credentials", menu=cred_menu)

        # Encryption menu
        encryption_menu = tk.Menu(menubar, tearoff=0)
        encryption_menu.add_command(label="Set/Change PIN", command=self.set_pin)
        encryption_menu.add_command(label="Clear PIN (No Encryption)", command=self.clear_pin)
        menubar.add_cascade(label="Encryption", menu=encryption_menu)

        self.config(menu=menubar)

    def set_pin(self):
        pin = simpledialog.askstring("Set PIN", "Enter new PIN for decrypting QR codes:", show="*", parent=self)
        if not pin:
            return
        self.pin = pin
        # Store PIN in OS keyring instead of database
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_PIN_KEY, pin)
            messagebox.showinfo("PIN Set", "PIN set successfully. Only QR codes created with this PIN can be read.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PIN to secure storage: {e}", parent=self)

    def clear_pin(self):
        self.pin = ""
        # Remove PIN from OS keyring
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_PIN_KEY)
        except keyring.errors.PasswordDeleteError:
            pass  # PIN was not stored
        except Exception:
            pass
        messagebox.showinfo("PIN Cleared", "Encryption disabled. App will treat QR codes as plain text.", parent=self)

    def set_email_credentials(self, provider):
        smtp = PROVIDERS[provider]
        email = simpledialog.askstring(f"Set {smtp['friendly']} Email", f"Enter your {smtp['friendly']} address:",
                                       parent=self)
        if not email:
            return
        pw = simpledialog.askstring(
            "Set Password",
            f"Enter your password (or app password if using MFA/2FA) for {smtp['friendly']}:",
            show="*",
            parent=self
        )
        if not pw:
            return
        keyring.set_password(KEYRING_SERVICE, smtp["email_key"], email)
        keyring.set_password(KEYRING_SERVICE, smtp["password_key"], pw)
        messagebox.showinfo("Saved", f"{smtp['friendly']} credentials saved securely.", parent=self)

    def clear_email_credentials(self, provider):
        smtp = PROVIDERS[provider]
        try:
            keyring.delete_password(KEYRING_SERVICE, smtp["email_key"])
        except keyring.errors.PasswordDeleteError:
            pass
        try:
            keyring.delete_password(KEYRING_SERVICE, smtp["password_key"])
        except keyring.errors.PasswordDeleteError:
            pass
        messagebox.showinfo("Cleared", f"{smtp['friendly']} credentials cleared.", parent=self)

    # --- Widgets ---
    def create_widgets(self):
        self.label = tk.Label(self, text="Scan QR Code to Start", font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        self.scan_btn = tk.Button(
            self, text="Scan QR", command=self.handle_scan,
            font=("Arial", 20), height=2, width=18, bg="#6699FF"
        )
        self.scan_btn.pack(pady=10)

        # Student selector
        sframe = tk.Frame(self)
        slabel = tk.Label(sframe, text="Student:", font=("Arial", 20), width=10, anchor="w")
        self.student_combo = ttk.Combobox(sframe, font=("Arial", 20), width=18)
        self.student_combo['values'] = [name for _, name in self.db.get_students()]
        self.student_combo.pack(side=tk.LEFT, padx=10, pady=10)
        slabel.pack(side=tk.LEFT, padx=10, pady=10)
        sframe.pack(pady=4)

        add_btn = tk.Button(sframe, text="+", font=("Arial", 16, "bold"), width=2, command=self.add_student_popup)
        add_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Service fields
        self.fields = {}
        for f in ["Service", "Duration", "Event"]:
            frame = tk.Frame(self)
            lbl = tk.Label(frame, text=f+":", font=("Arial", 20), width=10, anchor="w")
            ent = tk.Entry(frame, font=("Arial", 20), width=18)
            lbl.pack(side=tk.LEFT, padx=10, pady=10)
            ent.pack(side=tk.LEFT, padx=10, pady=10)
            frame.pack(pady=4)
            self.fields[f] = ent
            if f == "Duration":
                ent.bind("<Button-1>", lambda event, e=ent: self.show_keypad(e))

        frame = tk.Frame(self)
        lbl = tk.Label(frame, text="Score:", font=("Arial", 20), width=12, anchor="w")
        self.score_entry = tk.Entry(frame, font=("Arial", 20), width=8)
        lbl.pack(side=tk.LEFT, padx=10, pady=10)
        self.score_entry.pack(side=tk.LEFT, padx=10, pady=10)
        frame.pack(pady=4)
        self.score_entry.bind("<Button-1>", lambda event, e=self.score_entry: self.show_keypad(e))

        self.timestamp_var = tk.StringVar()
        self.timestamp_label = tk.Label(self, textvariable=self.timestamp_var, fg="blue", font=("Arial", 16, "bold"))
        self.timestamp_label.pack(pady=8)

        self.save_btn = tk.Button(
            self, text="Save Log", command=self.save_entry, state=tk.DISABLED,
            font=("Arial", 20), height=2, width=18, bg="#33CC99"
        )
        self.save_btn.pack(pady=10)

        # Email and export buttons frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=8)
        
        self.email_new_btn = tk.Button(
            button_frame, text="Send New Data", command=lambda: self.email_csv(only_new=True),
            font=("Arial", 18), height=2, width=12, bg="#33CC99"
        )
        self.email_new_btn.pack(side=tk.LEFT, padx=5)
        
        self.email_all_btn = tk.Button(
            button_frame, text="Send All Data", command=lambda: self.email_csv(only_new=False),
            font=("Arial", 18), height=2, width=12, bg="#FFBB33"
        )
        self.email_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = tk.Button(
            button_frame, text="Export Backup", command=self.export_local_backup,
            font=("Arial", 18), height=2, width=12, bg="#6699FF"
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

        self.exit_btn = tk.Button(
            self, text="Exit", command=self.destroy,
            font=("Arial", 20, "bold"), height=2, width=18, bg="#FF3333", fg="white"
        )
        self.exit_btn.pack(pady=20)

    # --- Student Management ---
    def add_student_popup(self):
        name = simpledialog.askstring("Add Student", "Enter student name:", parent=self)
        if name:
            self.db.add_student(name)
            students = [name for _, name in self.db.get_students()]
            self.student_combo['values'] = students
            self.student_combo.set(name)

    # --- Keypad ---
    def show_keypad(self, entry):
        if not Keypad._is_open:
            Keypad(entry, self)

    # --- Field Management ---
    def reset_fields(self):
        for ent in self.fields.values():
            ent.delete(0, tk.END)
        self.score_entry.delete(0, tk.END)
        self.timestamp_var.set("")
        self.current_goal_id = None
        self.save_btn.config(state=tk.DISABLED)

    # --- QR Scan ---
    def handle_scan(self):
        data = scan_qr_code()
        if not data:
            messagebox.showinfo("Scan Cancelled", "No QR code detected.", parent=self)
            return

        student_name = ""
        parsed = {}

        # Handle encrypted QR if PIN is set
        if self.pin:
            decrypted = decrypt_data(data, self.pin)
            if not decrypted:
                messagebox.showerror("Decryption Error", "Failed to decrypt QR code. Wrong PIN or not encrypted.", parent=self)
                return
            data = decrypted

        # Try JSON/CSV: Expecting either {"student": ...} or student,service,duration,...
        try:
            if data.startswith("{"):
                # JSON - Safe parsing instead of eval()
                try:
                    parsed = json.loads(data)
                    student_name = parsed.get("student", "").strip()
                    
                    # Validate schema version
                    schema_version = parsed.get("v", 0)
                    if schema_version != 1:
                        messagebox.showwarning("Version Warning", 
                                             f"QR code uses schema version {schema_version}. Some features may not work correctly.", 
                                             parent=self)
                except json.JSONDecodeError:
                    messagebox.showerror("Invalid QR Code", "QR code contains invalid JSON data.", parent=self)
                    return
            else:
                # CSV
                parts = [x.strip() for x in data.split(",")]
                if parts:
                    student_name = parts[0]
                keys = ["Service", "Duration", "Event", "Score"]
                for i, key in enumerate(keys, start=1):  # Start from 1 (student)
                    if i < len(parts):
                        parsed[key] = parts[i]

            # Auto-add/select student if found in QR code
            if student_name:
                self.db.add_student(student_name)
                students = [name for _, name in self.db.get_students()]
                self.student_combo['values'] = students
                self.student_combo.set(student_name)
            else:
                self.student_combo.set("")

            # Map JSON fields to form fields
            for key in ["Service", "Duration", "Event"]:
                self.fields[key].delete(0, tk.END)
                value = ""
                if key == "Duration":
                    value = str(parsed.get("default_duration", "") or parsed.get("duration", ""))
                elif key == "Service":
                    value = parsed.get("service", "")
                elif key == "Event":
                    value = parsed.get("event", "")
                self.fields[key].insert(0, value)
            
            self.score_entry.delete(0, tk.END)
            self.score_entry.insert(0, parsed.get("score", "") or parsed.get("Score", ""))
            
            # Store goal_id for later use when saving
            self.current_goal_id = parsed.get("goal_id", None)

        except Exception as e:
            print("QR parse error:", e)
            for ent in self.fields.values():
                ent.delete(0, tk.END)
            self.score_entry.delete(0, tk.END)
            self.student_combo.set("")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_var.set("Timestamp: " + now)
        self.save_btn.config(state=tk.NORMAL)

    # --- Saving Log ---
    def save_entry(self):
        student_name = self.student_combo.get().strip()
        if not student_name:
            messagebox.showerror("No Student", "Please select or add a student before saving.", parent=self)
            return
        student_id = self.db.add_student(student_name)
        service = self.fields["Service"].get().strip()
        duration = self.fields["Duration"].get().strip()
        event = self.fields["Event"].get().strip()
        score = self.score_entry.get().strip()
        self.db.log_service(student_id, service, duration, event, score, self.current_goal_id)
        messagebox.showinfo("Saved", f"Log entry saved for {student_name}.", parent=self)
        self.reset_fields()

    # --- Email Reports ---
    def email_csv(self, only_new=None):
        students = self.db.get_students()
        student_names = [name for _, name in students]
        student_names.insert(0, "All Students")
        student_name = simpledialog.askstring(
            "Select Student", f"Enter student name for report:\n(Or type 'All Students' to send all)", 
            initialvalue=student_names[0], parent=self)
        if not student_name:
            return
        if student_name not in student_names:
            messagebox.showerror("Error", "Student not found.", parent=self)
            return
        student_id = None if student_name == "All Students" else \
            [sid for sid, name in students if name == student_name][0]

        # If only_new not specified via button, ask user
        if only_new is None:
            choice = simpledialog.askstring(
                "Send New or All?", "Type 'new' for only new services or 'all' for all services:", 
                initialvalue="new", parent=self)
            if not choice:
                return
            only_new = (choice.lower().strip() == "new")

        services = self.db.get_services(student_id, only_new=only_new)
        if not services:
            messagebox.showinfo("No Data", "No service data to send for this selection.", parent=self)
            return

        tmpfile = "to_send_report.csv"
        with open(tmpfile, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Timestamp", "Student", "Service", "Duration", "Event", "Score", "Goal_ID", "Device_ID", "Reported"])
            for row in services:
                writer.writerow(row)

        smtp = PROVIDERS[self.selected_provider.get()]
        last_email = self.db.get_setting("last_recipient_email")
        recipient = simpledialog.askstring(
            "Recipient Email", "Email to send to:", initialvalue=last_email, parent=self)
        if not recipient:
            os.remove(tmpfile)
            return

        username = keyring.get_password(KEYRING_SERVICE, smtp["email_key"])
        password = keyring.get_password(KEYRING_SERVICE, smtp["password_key"])
        if not username or not password:
            messagebox.showerror("No Credentials", f"No credentials found for {smtp['friendly']}.\nPlease set credentials using the menu.", parent=self)
            os.remove(tmpfile)
            return

        try:
            send_email(tmpfile, recipient, username, password, smtp)
            messagebox.showinfo("Sent", f"Report sent to {recipient} using {smtp['friendly']}.", parent=self)
            service_ids = [row[0] for row in services]
            self.db.mark_services_reported(service_ids)
            self.db.set_setting("last_recipient_email", recipient)
        except Exception as e:
            messagebox.showerror("Error", f"Could not send email: {e}", parent=self)
        finally:
            os.remove(tmpfile)
    
    def export_local_backup(self):
        """Export all data to a local CSV file for backup"""
        from tkinter import filedialog
        
        # Get all services
        services = self.db.get_services(only_new=False)
        if not services:
            messagebox.showinfo("No Data", "No service data to export.", parent=self)
            return
        
        # Ask where to save
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"services_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            parent=self
        )
        
        if not filename:
            return
        
        # Write CSV
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Timestamp", "Student", "Service", "Duration", "Event", "Score", "Goal_ID", "Device_ID", "Reported"])
                for row in services:
                    writer.writerow(row)
            
            messagebox.showinfo("Export Complete", 
                              f"Backup saved successfully!\n\n"
                              f"File: {filename}\n"
                              f"Records: {len(services)}", 
                              parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not save backup: {e}", parent=self)

if __name__ == "__main__":
    app = TouchApp()
    app.mainloop()
