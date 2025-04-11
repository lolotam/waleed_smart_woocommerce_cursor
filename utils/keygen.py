import os
import json
import datetime
import argparse
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# This utility is for admin/developer use only and should not be distributed with the application

# Constants
SALT = b'WaleedSmartWooCommerce2023'  # Must match the salt in license_manager.py

def derive_key(password):
    """Derive a Fernet key from a password"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_data(data, password):
    """Encrypt data using a password-derived key"""
    key = derive_key(password)
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode()).decode()

def get_license_secret():
    """Get the secret used for license encryption"""
    # This would normally be a hardcoded value or fetched from somewhere secure
    # For this keygen, we'll prompt for it or use from environment
    secret = os.environ.get('LICENSE_SECRET')
    if not secret:
        # In a real application, this would be a fixed value matching the one in license_manager.py
        # For this project, we'll just derive it the same way as the application does
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(os.path.dirname(script_dir), 'app.py')
        if os.path.exists(app_path):
            app_code = open(app_path, 'rb').read()
            secret = hashlib.sha256(app_code).hexdigest()[:32]
        else:
            raise ValueError("Could not determine license secret. Set LICENSE_SECRET environment variable.")
    return secret

def generate_trial_key(machine_fingerprint, simple_fingerprint, name, email, days_valid=30):
    """
    Generate a trial license key
    
    Args:
        machine_fingerprint (str): The machine fingerprint
        simple_fingerprint (str): The simplified machine fingerprint
        name (str): The user's name
        email (str): The user's email
        days_valid (int): The number of days the trial is valid for
    
    Returns:
        str: The encrypted license key
    """
    # Create license data
    issue_date = datetime.datetime.now()
    expiry_date = issue_date + datetime.timedelta(days=days_valid)
    
    license_data = {
        'fingerprint': machine_fingerprint,
        'simple_fingerprint': simple_fingerprint,
        'name': name,
        'email': email,
        'type': 'trial',
        'issue_date': issue_date.isoformat(),
        'expiry_date': expiry_date.isoformat(),
    }
    
    # Encrypt the license data
    secret = get_license_secret()
    return encrypt_data(license_data, secret)

def generate_full_key(machine_fingerprint, simple_fingerprint, name, email):
    """
    Generate a full license key
    
    Args:
        machine_fingerprint (str): The machine fingerprint
        simple_fingerprint (str): The simplified machine fingerprint
        name (str): The user's name
        email (str): The user's email
    
    Returns:
        str: The encrypted license key
    """
    # Create license data
    license_data = {
        'fingerprint': machine_fingerprint,
        'simple_fingerprint': simple_fingerprint,
        'name': name,
        'email': email,
        'type': 'full',
        'issue_date': datetime.datetime.now().isoformat(),
    }
    
    # Encrypt the license data
    secret = get_license_secret()
    return encrypt_data(license_data, secret)

def main():
    """Command-line interface for generating license keys"""
    parser = argparse.ArgumentParser(description='Generate license keys for Waleed Smart WooCommerce')
    parser.add_argument('--type', choices=['trial', 'full'], required=True, help='License type')
    parser.add_argument('--name', required=True, help='User\'s name')
    parser.add_argument('--email', required=True, help='User\'s email')
    parser.add_argument('--days', type=int, default=30, help='Days valid (for trial)')
    parser.add_argument('--fingerprint', required=True, help='Machine fingerprint')
    parser.add_argument('--simple-fingerprint', required=True, help='Simplified machine fingerprint')
    parser.add_argument('--output', help='Output file (if not provided, prints to stdout)')
    
    args = parser.parse_args()
    
    # Generate the license key
    if args.type == 'trial':
        license_key = generate_trial_key(
            args.fingerprint, 
            args.simple_fingerprint, 
            args.name, 
            args.email, 
            args.days
        )
    else:
        license_key = generate_full_key(
            args.fingerprint, 
            args.simple_fingerprint, 
            args.name, 
            args.email
        )
    
    # Output the license key
    if args.output:
        with open(args.output, 'w') as f:
            f.write(license_key)
        print(f"License key written to {args.output}")
    else:
        print(license_key)

if __name__ == "__main__":
    main() 