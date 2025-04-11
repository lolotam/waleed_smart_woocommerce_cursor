import os
import argparse
from utils.machine_id import get_machine_fingerprint, get_simplified_fingerprint
from utils.keygen import generate_trial_key, generate_full_key

def main():
    """Generate a license key for the local machine"""
    parser = argparse.ArgumentParser(description='Generate a license key for the local machine')
    parser.add_argument('--type', choices=['trial', 'full'], default='trial', help='License type')
    parser.add_argument('--name', default='Demo User', help='User\'s name')
    parser.add_argument('--email', default='demo@example.com', help='User\'s email')
    parser.add_argument('--days', type=int, default=30, help='Days valid (for trial)')
    parser.add_argument('--save', action='store_true', help='Save the license key to the license file')
    
    args = parser.parse_args()
    
    # Get machine fingerprints
    machine_fingerprint = get_machine_fingerprint()
    simple_fingerprint = get_simplified_fingerprint()
    
    print(f"Machine Fingerprint: {machine_fingerprint}")
    print(f"Simplified Fingerprint: {simple_fingerprint}")
    
    # Generate the license key
    if args.type == 'trial':
        license_key = generate_trial_key(
            machine_fingerprint, 
            simple_fingerprint, 
            args.name, 
            args.email, 
            args.days
        )
        print(f"Generated {args.days}-day trial license for {args.name} ({args.email})")
    else:
        license_key = generate_full_key(
            machine_fingerprint, 
            simple_fingerprint, 
            args.name, 
            args.email
        )
        print(f"Generated full license for {args.name} ({args.email})")
    
    # Save or print the license key
    if args.save:
        from config import Config
        with open(Config.LICENSE_FILE, 'w') as f:
            f.write(license_key)
        print(f"License key saved to {Config.LICENSE_FILE}")
    else:
        print("\nLicense Key:")
        print(license_key)
        print("\nTo use this license, either:")
        print("1. Copy and paste it into the license activation screen, or")
        print("2. Run this script with --save to save it directly")

if __name__ == "__main__":
    main() 