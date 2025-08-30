import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyperclip
import secrets
import string

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Password Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.master_password = None
        self.fernet = None
        self.data_file = "passwords.encrypted"
        self.key_file = "key.key"
        
        self.setup_ui()
        
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.login_frame = ttk.Frame(self.notebook, padding=10)
        self.main_frame = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.login_frame, text="Login")
        self.notebook.add(self.main_frame, text="Password Manager")
        
        self.setup_login_frame()
        self.setup_main_frame()
        
        self.notebook.hide(1)
        
    def setup_login_frame(self):
        ttk.Label(self.login_frame, text="Master Password:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        self.master_pwd_var = tk.StringVar()
        master_pwd_entry = ttk.Entry(self.login_frame, textvariable=self.master_pwd_var, show="•", width=30)
        master_pwd_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(self.login_frame, text="Create New Vault", command=self.create_new_vault).grid(row=2, column=0, columnspan=2, pady=10)
        
        master_pwd_entry.bind('<Return>', lambda event: self.login())
        
    def setup_main_frame(self):
        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 10))
        
        right_frame = ttk.Frame(self.main_frame)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW)
        
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        ttk.Label(left_frame, text="Service:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.service_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.service_var, width=20).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.username_var, width=20).grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(left_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.password_var, show="•", width=20).grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Button(left_frame, text="Generate Password", command=self.generate_password).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(left_frame, text="Add/Update", command=self.save_password).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(left_frame, text="Delete", command=self.delete_password).grid(row=5, column=0, columnspan=2, pady=5)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        ttk.Button(left_frame, text="Export Passwords", command=self.export_passwords).grid(row=7, column=0, columnspan=2, pady=5)
        ttk.Button(left_frame, text="Import Passwords", command=self.import_passwords).grid(row=8, column=0, columnspan=2, pady=5)
        ttk.Button(left_frame, text="Change Master Password", command=self.change_master_password).grid(row=9, column=0, columnspan=2, pady=5)
        
        ttk.Label(right_frame, text="Saved Passwords:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        columns = ("Service", "Username", "Password")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=1, column=0, sticky=tk.NSEW, pady=5)
        scrollbar.grid(row=1, column=1, sticky=tk.NS)
        
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Copy Username", command=self.copy_username).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy Password", command=self.copy_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Show Password", command=self.toggle_password_visibility).pack(side=tk.LEFT, padx=5)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
    def derive_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
        
    def create_new_vault(self):
        password = self.master_pwd_var.get()
        if not password:
            messagebox.showerror("Error", "Please enter a master password")
            return
            
        salt = secrets.token_bytes(16)
        key = self.derive_key(password, salt)
        self.fernet = Fernet(key)
        
        with open(self.key_file, 'wb') as f:
            f.write(salt)
            
        self.master_password = password
        self.passwords = {}
        self.save_data()
        
        messagebox.showinfo("Success", "New vault created successfully")
        self.notebook.hide(0)
        self.notebook.select(1)
        
    def login(self):
        password = self.master_pwd_var.get()
        if not password:
            messagebox.showerror("Error", "Please enter the master password")
            return
            
        if not os.path.exists(self.key_file) or not os.path.exists(self.data_file):
            messagebox.showerror("Error", "No vault found. Please create a new vault.")
            return
            
        try:
            with open(self.key_file, 'rb') as f:
                salt = f.read()
                
            key = self.derive_key(password, salt)
            self.fernet = Fernet(key)
            
            with open(self.data_file, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.fernet.decrypt(encrypted_data)
            self.passwords = json.loads(decrypted_data.decode())
            
            self.master_password = password
            self.notebook.hide(0)
            self.notebook.select(1)
            self.update_treeview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid master password: {str(e)}")
            
    def save_data(self):
        if not self.fernet:
            return
            
        data = json.dumps(self.passwords).encode()
        encrypted_data = self.fernet.encrypt(data)
        
        with open(self.data_file, 'wb') as f:
            f.write(encrypted_data)
            
    def save_password(self):
        service = self.service_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not service or not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if service not in self.passwords:
            self.passwords[service] = {}
            
        self.passwords[service][username] = password
        self.save_data()
        self.update_treeview()
        
        self.service_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        
        messagebox.showinfo("Success", "Password saved successfully")
        
    def delete_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a password to delete")
            return
            
        item = self.tree.item(selected[0])
        service = item['values'][0]
        username = item['values'][1]
        
        if service in self.passwords and username in self.passwords[service]:
            del self.passwords[service][username]
            if not self.passwords[service]:
                del self.passwords[service]
                
            self.save_data()
            self.update_treeview()
            messagebox.showinfo("Success", "Password deleted successfully")
            
    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for service, credentials in self.passwords.items():
            for username, password in credentials.items():
                self.tree.insert("", tk.END, values=(service, username, "•" * 12))
                
    def on_item_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        self.service_var.set(item['values'][0])
        self.username_var.set(item['values'][1])
        
        service = item['values'][0]
        username = item['values'][1]
        if service in self.passwords and username in self.passwords[service]:
            self.password_var.set(self.passwords[service][username])
            
    def copy_username(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an entry first")
            return
            
        item = self.tree.item(selected[0])
        username = item['values'][1]
        pyperclip.copy(username)
        messagebox.showinfo("Success", "Username copied to clipboard")
        
    def copy_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an entry first")
            return
            
        item = self.tree.item(selected[0])
        service = item['values'][0]
        username = item['values'][1]
        
        if service in self.passwords and username in self.passwords[service]:
            password = self.passwords[service][username]
            pyperclip.copy(password)
            messagebox.showinfo("Success", "Password copied to clipboard")
            
    def toggle_password_visibility(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        service = item['values'][0]
        username = item['values'][1]
        
        if service in self.passwords and username in self.passwords[service]:
            password = self.passwords[service][username]
            if item['values'][2] == "•" * 12:
                self.tree.set(selected[0], "Password", password)
            else:
                self.tree.set(selected[0], "Password", "•" * 12)
                
    def generate_password(self):
        length = 16
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(length))
        self.password_var.set(password)
        pyperclip.copy(password)
        messagebox.showinfo("Password Generated", "A strong password has been generated and copied to clipboard")
        
    def export_passwords(self):
        if not self.passwords:
            messagebox.showerror("Error", "No passwords to export")
            return
            
        try:
            with open("passwords_export.json", "w") as f:
                json.dump(self.passwords, f, indent=4)
                
            messagebox.showinfo("Success", "Passwords exported to passwords_export.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export passwords: {str(e)}")
            
    def import_passwords(self):
        try:
            with open("passwords_export.json", "r") as f:
                imported_passwords = json.load(f)
                
            for service, credentials in imported_passwords.items():
                if service not in self.passwords:
                    self.passwords[service] = {}
                    
                for username, password in credentials.items():
                    self.passwords[service][username] = password
                    
            self.save_data()
            self.update_treeview()
            messagebox.showinfo("Success", "Passwords imported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import passwords: {str(e)}")
            
    def change_master_password(self):
        new_password = tk.simpledialog.askstring("Change Master Password", "Enter new master password:", show="•")
        if not new_password:
            return
            
        salt = secrets.token_bytes(16)
        key = self.derive_key(new_password, salt)
        new_fernet = Fernet(key)
        
        with open(self.key_file, 'wb') as f:
            f.write(salt)
            
        data = json.dumps(self.passwords).encode()
        encrypted_data = new_fernet.encrypt(data)
        
        with open(self.data_file, 'wb') as f:
            f.write(encrypted_data)
            
        self.fernet = new_fernet
        self.master_password = new_password
        
        messagebox.showinfo("Success", "Master password changed successfully")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()