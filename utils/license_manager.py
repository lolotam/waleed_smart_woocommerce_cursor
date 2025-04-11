import os
import json
import base64
import datetime
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

from config import Config
from utils.machine_id import get_machine_fingerprint, get_simplified_fingerprint

# Encryption key derivation constant (DO NOT CHANGE)
# This is used to derive the encryption key from a secret
SALT = b'WaleedSmartWooCommerce2023'  # Fixed salt

def _derive_key(password):
    """Derive a Fernet key from a password"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def _encrypt_data(data, password):
    """Encrypt data using a password-derived key"""
    key = _derive_key(password)
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode()).decode()

def _decrypt_data(encrypted_data, password):
    """Decrypt data using a password-derived key"""
    try:
        key = _derive_key(password)
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data.encode())
        return json.loads(decrypted.decode())
    except Exception:
        return None

def _get_license_secret():
    """Get the secret used for license encryption"""
    # This would normally be a hardcoded value or fetched from somewhere secure
    # For this application, we'll use a derived value from the app code itself
    app_code = open(os.path.join(Config.BASE_DIR, 'app.py'), 'rb').read()
    return hashlib.sha256(app_code).hexdigest()[:32]

def validate_license():
    """
    Validate the installed license
    
    Returns:
        bool: True if the license is valid, False otherwise
    """
    if not os.path.exists(Config.LICENSE_FILE):
        return False
    
    try:
        # Read the license file
        with open(Config.LICENSE_FILE, 'r') as f:
            encrypted_license = f.read().strip()
        
        # Decrypt the license data
        secret = _get_license_secret()
        license_data = _decrypt_data(encrypted_license, secret)
        
        if not license_data:
            return False
        
        # Check if the license matches this machine
        machine_fingerprint = get_machine_fingerprint()
        simple_fingerprint = get_simplified_fingerprint()
        
        if license_data.get('fingerprint') != machine_fingerprint and \
           license_data.get('simple_fingerprint') != simple_fingerprint:
            return False
        
        # Check if the license is expired (trial licenses)
        if license_data.get('type') == 'trial':
            expiry_date = datetime.datetime.fromisoformat(license_data.get('expiry_date'))
            if expiry_date < datetime.datetime.now():
                return False
        
        return True
    except Exception:
        return False

def get_license_info():
    """
    Get information about the current license
    
    Returns:
        dict: License information or None if no valid license
    """
    if not os.path.exists(Config.LICENSE_FILE):
        return None
    
    try:
        # Read the license file
        with open(Config.LICENSE_FILE, 'r') as f:
            encrypted_license = f.read().strip()
        
        # Decrypt the license data
        secret = _get_license_secret()
        license_data = _decrypt_data(encrypted_license, secret)
        
        if not license_data:
            return None
        
        # Strip out sensitive information
        return {
            'name': license_data.get('name'),
            'email': license_data.get('email'),
            'type': license_data.get('type'),
            'issue_date': license_data.get('issue_date'),
            'expiry_date': license_data.get('expiry_date') if license_data.get('type') == 'trial' else None,
        }
    except Exception:
        return None

def save_license(license_key):
    """
    Save and validate a license key
    
    Args:
        license_key (str): The license key to save
    
    Returns:
        bool: True if the license was saved successfully, False otherwise
    """
    try:
        # Decrypt the license key
        secret = _get_license_secret()
        license_data = _decrypt_data(license_key, secret)
        
        if not license_data:
            return False
        
        # Verify the license matches this machine
        machine_fingerprint = get_machine_fingerprint()
        simple_fingerprint = get_simplified_fingerprint()
        
        if license_data.get('fingerprint') != machine_fingerprint and \
           license_data.get('simple_fingerprint') != simple_fingerprint:
            return False
        
        # Save the license key
        with open(Config.LICENSE_FILE, 'w') as f:
            f.write(license_key)
        
        return True
    except Exception:
        return False

def clear_license():
    """Remove the current license"""
    if os.path.exists(Config.LICENSE_FILE):
        os.remove(Config.LICENSE_FILE) 