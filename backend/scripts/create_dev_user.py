#!/usr/bin/env python3
"""
Development Provisioning Tool
DO NOT run in production.

This script creates a local development user to test the /auth/login flow end-to-end.

Usage:
  python scripts/create_dev_user.py
  python scripts/create_dev_user.py --role admin

The resulting user can authenticate via the standard POST /auth/login endpoint.
"""
import sys
import os
import argparse
import getpass
import re

# Add the backend root to sys.path so we can import 'app' modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import get_password_hash

def main():
    if settings.ENVIRONMENT.lower() == "production":
        print("ERROR: Cannot run development provisioning script in production environment.")
        sys.exit(1)

    print("=== Sovereign AI Workbench - Development User Provisioning ===")
    print("This tool creates a local development user. Do NOT use in production.\n")

    parser = argparse.ArgumentParser(description="Create a development user.")
    parser.add_argument("--role", type=str, help="Role to assign to the user")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        # 1. Username
        while True:
            username = input("Username: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            if db.query(User).filter(User.username == username).first():
                print(f"Error: Username '{username}' is already registered.")
                # We do not silently overwrite to maintain idempotency/safety
                return
            break

        # 2. Email
        while True:
            email = input("Email: ").strip()
            if not email or "@" not in email:
                print("Please enter a valid email address (must contain '@').")
                continue
            if db.query(User).filter(User.email == email).first():
                print(f"Error: Email '{email}' is already registered.")
                return
            break

        # 3. Full Name
        full_name = input("Full Name (optional): ").strip()

        # 4. Password
        while True:
            if sys.stdin.isatty():
                password = getpass.getpass("Password: ")
            else:
                print("Password: ", end="", flush=True)
                password = input()
            if not password:
                print("Password cannot be empty.")
                continue
                
            if sys.stdin.isatty():
                confirm = getpass.getpass("Confirm Password: ")
            else:
                print("Confirm Password: ", end="", flush=True)
                confirm = input()
                
            if password != confirm:
                print("Passwords do not match. Try again.")
                continue
            break

        # 5. Role Assignment
        assigned_role_name = args.role
        role_input = None
        if not assigned_role_name:
            existing_roles = [r.name for r in db.query(Role).all()]
            print(f"\nExisting roles in DB: {', '.join(existing_roles) if existing_roles else 'None'}")
            
            if "user" in existing_roles:
                default_role = "user"
            else:
                non_admin_roles = [r for r in existing_roles if r.lower() != "admin"]
                default_role = non_admin_roles[0] if non_admin_roles else "user"
                
            role_input = input(f"Role to assign [{default_role}]: ").strip()
            assigned_role_name = role_input if role_input else default_role

        if assigned_role_name.lower() == "admin" and not args.role and not role_input:
            # Failsafe in case default_role somehow became admin
            assigned_role_name = "user"

        role = db.query(Role).filter(Role.name == assigned_role_name).first()
        if not role:
            print(f"Role '{assigned_role_name}' does not exist.")
            create = input(f"Create role '{assigned_role_name}'? [y/N]: ").strip().lower()
            if create == 'y':
                role = Role(name=assigned_role_name, description=f"Development role: {assigned_role_name}")
                db.add(role)
                db.flush() # ensure role gets an ID
            else:
                print("Aborting.")
                return

        # 6. Database Transaction
        print("\nProvisioning user...")
        
        user = User(
            username=username,
            email=email,
            full_name=full_name if full_name else None,
            password_hash=get_password_hash(password),
            is_active=True
        )
        db.add(user)
        db.flush()

        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
        
        # Commit only when everything is valid
        db.commit()
        
        print(f"Success! User '{username}' created with role '{assigned_role_name}'.")
        print("You can now authenticate via POST /auth/login.")

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        db.rollback()
    except Exception as e:
        db.rollback()
        print(f"\nError provisioning user: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
