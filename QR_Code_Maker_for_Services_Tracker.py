# -*- coding: utf-8 -*-
"""
Created on Sat May 31 10:17:07 2025

@author: jrember
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import qrcode
import base64
import hashlib
from cryptography.fernet import Fernet
import json
from datetime import datetime

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

def encrypt_data(data, pin):
    """Encrypt data using PIN-derived key."""
    key = get_fernet_key_from_pin(pin)
    f = Fernet(key)
    return f.encrypt(data.encode('utf-8')).decode('utf-8')

class QRCodeGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Code Generator for Service Tracker")
        self.geometry("500x800")  # Taller window for templates
        self.resizable(False, False)
        
        # Templates for common QR types
        self.templates = {
            "Service Session": {
                "type": "service",
                "service": "",
                "default_duration": 30,
                "event": "session"
            },
            "Goal Tracking": {
                "type": "goal",
                "goal_id": "",
                "service": "",
                "default_duration": 15,
                "measurement_type": "percentage"
            },
            "Behavior Event": {
                "type": "behavior",
                "event": "incident",
                "severity": "minor"
            },
            "Custom": {}
        }

        # --- Scrollable content ---
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, borderwidth=0, height=700)
        vscroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.content = tk.Frame(canvas)

        self.content.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.content, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

        # UI Elements (add to self.content, not self)
        # Template Selection
        tk.Label(self.content, text="Template:", font=("Arial", 14, "bold")).pack(pady=(20,2))
        self.template_var = tk.StringVar(value="Service Session")
        self.template_combo = ttk.Combobox(self.content, textvariable=self.template_var, 
                                          values=list(self.templates.keys()), 
                                          font=("Arial", 12), width=30, state="readonly")
        self.template_combo.pack(pady=2)
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_change)
        
        # QR Label
        tk.Label(self.content, text="QR Label (for printing):", font=("Arial", 14)).pack(pady=(15,2))
        self.label_entry = tk.Entry(self.content, font=("Arial", 14), width=32)
        self.label_entry.pack(pady=2)
        
        # JSON Fields Frame
        tk.Label(self.content, text="QR Data Fields:", font=("Arial", 14, "bold")).pack(pady=(15,2))
        self.fields_frame = tk.Frame(self.content)
        self.fields_frame.pack(pady=5)
        
        # Student Name
        tk.Label(self.fields_frame, text="Student Name:", font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=2)
        self.student_entry = tk.Entry(self.fields_frame, font=("Arial", 12), width=25)
        self.student_entry.grid(row=0, column=1, padx=2, pady=2)
        
        # Service
        tk.Label(self.fields_frame, text="Service:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=2)
        self.service_entry = tk.Entry(self.fields_frame, font=("Arial", 12), width=25)
        self.service_entry.grid(row=1, column=1, padx=2, pady=2)
        
        # Duration
        tk.Label(self.fields_frame, text="Default Duration:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=2)
        self.duration_entry = tk.Entry(self.fields_frame, font=("Arial", 12), width=25)
        self.duration_entry.insert(0, "30")
        self.duration_entry.grid(row=2, column=1, padx=2, pady=2)
        
        # Goal ID (optional)
        tk.Label(self.fields_frame, text="Goal ID (optional):", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=2)
        self.goal_entry = tk.Entry(self.fields_frame, font=("Arial", 12), width=25)
        self.goal_entry.grid(row=3, column=1, padx=2, pady=2)
        
        # Custom JSON (for advanced users)
        tk.Label(self.content, text="Custom JSON (advanced):", font=("Arial", 12)).pack(pady=(10,2))
        self.json_text = tk.Text(self.content, font=("Courier", 10), width=45, height=4)
        self.json_text.pack(pady=2)

        tk.Label(self.content, text="PIN (optional for encryption):", font=("Arial", 14)).pack(pady=(10,2))
        self.pin_entry = tk.Entry(self.content, font=("Arial", 14), width=32, show="*")
        self.pin_entry.pack(pady=2)

        self.qr_canvas = tk.Canvas(self.content, width=300, height=330, bg="white", bd=0, highlightthickness=0)
        self.qr_canvas.pack(pady=25)

        self.gen_btn = tk.Button(self.content, text="Generate QR Code", command=self.generate_qr, font=("Arial", 14), width=22, bg="#33CC99")
        self.gen_btn.pack(pady=(10,8))

        self.save_btn = tk.Button(self.content, text="Save QR Code", command=self.save_qr, font=("Arial", 14), width=22, state=tk.DISABLED, bg="#6699FF")
        self.save_btn.pack(pady=(5,20))

        self.generated_image = None  # PIL image object

        # Mousewheel scrolling (Windows/Mac/Linux)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux scroll down
    
    def on_template_change(self, event=None):
        """Update fields based on selected template."""
        template_name = self.template_var.get()
        template = self.templates.get(template_name, {})
        
        if template_name != "Custom":
            # Pre-fill template values
            self.service_entry.delete(0, tk.END)
            self.service_entry.insert(0, template.get("service", ""))
            self.duration_entry.delete(0, tk.END)
            self.duration_entry.insert(0, str(template.get("default_duration", 30)))

    def generate_qr(self):
        label = self.label_entry.get().strip()
        pin = self.pin_entry.get().strip()
        
        # Build JSON data from fields
        json_data = {}
        
        # Check if custom JSON is provided
        custom_json = self.json_text.get("1.0", tk.END).strip()
        if custom_json:
            try:
                json_data = json.loads(custom_json)
            except json.JSONDecodeError as e:
                messagebox.showerror("Invalid JSON", f"Custom JSON is invalid: {e}")
                return
        else:
            # Build from form fields
            student = self.student_entry.get().strip()
            if not student:
                messagebox.showerror("Missing Student", "Please enter a student name.")
                return
            
            json_data = {
                "v": 1,  # Schema version
                "type": self.templates.get(self.template_var.get(), {}).get("type", "service"),
                "student": student,
                "service": self.service_entry.get().strip(),
                "default_duration": int(self.duration_entry.get() or 30),
                "created": datetime.now().isoformat()
            }
            
            # Add optional fields
            goal_id = self.goal_entry.get().strip()
            if goal_id:
                json_data["goal_id"] = goal_id
        
        # Convert to JSON string
        text = json.dumps(json_data, separators=(',', ':'))

        # Encrypt if PIN is provided
        data_to_encode = text
        if pin:
            try:
                data_to_encode = encrypt_data(text, pin)
            except Exception as e:
                messagebox.showerror("Encryption Error", f"Error encrypting text: {e}")
                return

        # Generate QR code
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(data_to_encode)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Add label above QR code (if present)
        if label:
            img_w, img_h = qr_img.size
            label_img = Image.new("RGB", (img_w, 40), "white")
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(label_img)
                # Use system font, fallback if arial not found
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                tw = draw.textlength(label, font=font)
                tx = (img_w - tw)//2 if tw < img_w else 0
                draw.text((tx, 10), label, fill="black", font=font)
            except Exception:
                pass  # Draw nothing if font fails

            combined = Image.new("RGB", (img_w, img_h+40), "white")
            combined.paste(label_img, (0,0))
            combined.paste(qr_img, (0,40))
            qr_img = combined

        self.generated_image = qr_img

        # Show QR code in the canvas
        img = qr_img.resize((300, 300), Image.LANCZOS)
        self.tk_qr_img = ImageTk.PhotoImage(img)
        self.qr_canvas.delete("all")
        self.qr_canvas.create_image(150, 150, image=self.tk_qr_img)
        if label:
            self.qr_canvas.create_text(150, 20, text=label, fill="black", font=("Arial", 14, "bold"))
        self.save_btn.config(state=tk.NORMAL)

    def save_qr(self):
        if not self.generated_image:
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG Image", "*.png")],
                                                title="Save QR Code")
        if filepath:
            self.generated_image.save(filepath)
            messagebox.showinfo("Saved", f"QR code saved as:\n{filepath}")

if __name__ == "__main__":
    try:
        import qrcode
        from PIL import Image, ImageTk
    except ImportError:
        import sys
        sys.exit("Please install 'qrcode' and 'Pillow' packages (pip install qrcode[pil] pillow cryptography)")

    app = QRCodeGeneratorApp()
    app.mainloop()
