#!/usr/bin/env python3
"""
API Key Generator for Chaotic Encryption App

This script helps generate secure API keys for production use.
Run this script to generate new API keys with specific permissions.
"""

import hashlib
import secrets
import json
from datetime import datetime

def generate_api_key(name, permissions, rate_limit=100):
    """Generate a new API key with specified permissions"""
    
    # Generate a secure random key
    api_key = secrets.token_urlsafe(32)
    
    # Hash the key for storage
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Create key info
    key_info = {
        'name': name,
        'permissions': permissions,
        'rate_limit': rate_limit,
        'created_at': datetime.now().isoformat(),
        'last_used': None
    }
    
    return api_key, key_hash, key_info

def main():
    print("🔐 API Key Generator for Chaotic Encryption App")
    print("=" * 50)
    
    # Get key details from user
    name = input("Enter key name (e.g., 'Production Key 1'): ").strip()
    if not name:
        name = "Generated Key"
    
    print("\nAvailable permissions:")
    print("1. encrypt - Can encrypt images")
    print("2. decrypt - Can decrypt images") 
    print("3. download - Can download files")
    print("4. admin - Can manage API keys")
    
    permissions_input = input("\nEnter permissions (comma-separated, e.g., 'encrypt,decrypt,download'): ").strip()
    if not permissions_input:
        permissions = ['encrypt', 'decrypt']
    else:
        permissions = [p.strip() for p in permissions_input.split(',')]
    
    rate_limit_input = input("Enter rate limit (requests per hour, default 100): ").strip()
    try:
        rate_limit = int(rate_limit_input) if rate_limit_input else 100
    except ValueError:
        rate_limit = 100
    
    # Generate the key
    api_key, key_hash, key_info = generate_api_key(name, permissions, rate_limit)
    
    print("\n" + "=" * 50)
    print("✅ API Key Generated Successfully!")
    print("=" * 50)
    print(f"Key Name: {name}")
    print(f"Permissions: {', '.join(permissions)}")
    print(f"Rate Limit: {rate_limit} requests/hour")
    print(f"Created: {key_info['created_at']}")
    print("\n🔑 API Key (store securely - this is the only time you'll see it):")
    print(f"{api_key}")
    print("\n📋 For environment variable (API_KEYS):")
    
    # Create the JSON structure for environment variable
    env_json = {key_hash: key_info}
    print(json.dumps(env_json, indent=2))
    
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Store the API key securely - it cannot be recovered")
    print("2. Add the JSON to your API_KEYS environment variable")
    print("3. Never commit API keys to version control")
    print("4. Rotate keys regularly")
    print("5. Use HTTPS in production")
    
    # Save to file for reference
    with open('generated_api_key.txt', 'w') as f:
        f.write(f"API Key: {api_key}\n")
        f.write(f"Key Hash: {key_hash}\n")
        f.write(f"Key Info: {json.dumps(key_info, indent=2)}\n")
        f.write(f"Environment JSON: {json.dumps(env_json, indent=2)}\n")
    
    print(f"\n💾 Key details saved to: generated_api_key.txt")

if __name__ == "__main__":
    main()
