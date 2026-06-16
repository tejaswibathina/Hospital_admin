import json
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(BASE_DIR, "admin_auth.json")


def hash_password(password):
    return hashlib.sha256(password.strip().encode()).hexdigest()


def create_default_admin():
    default_data = {
        "username": "admin",
        "password": hash_password("admin123")
    }

    with open(AUTH_FILE, "w") as file:
        json.dump(default_data, file, indent=4)


def load_admin():
    if not os.path.exists(AUTH_FILE):
        create_default_admin()

    with open(AUTH_FILE, "r") as file:
        return json.load(file)


def verify_login(username, password):
    admin = load_admin()

    entered_username = username.strip()
    entered_password_hash = hash_password(password)

    saved_username = admin["username"].strip()
    saved_password_hash = admin["password"].strip()

    return (
        entered_username == saved_username
        and entered_password_hash == saved_password_hash
    )


def change_admin_password(old_password, new_password):
    admin = load_admin()

    if hash_password(old_password) != admin["password"].strip():
        return False, "Old password is incorrect."

    admin["password"] = hash_password(new_password)

    with open(AUTH_FILE, "w") as file:
        json.dump(admin, file, indent=4)

    return True, "Password changed successfully."