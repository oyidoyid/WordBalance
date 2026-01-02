import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, auth as admin_auth
import os

# -------------------- Firebase Admin Setup --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

# -------------------- Pyrebase Config --------------------
firebase_config = {
    "apiKey": "AIzaSyCKIl9qhmg_cRAXH2WSKlzwn6YFE3zRlfw",
    "authDomain": "wordbalance-5c81f.firebaseapp.com",
    "projectId": "wordbalance-5c81f",
    "storageBucket": "wordbalance-5c81f.firebasestorage.app",
    "databaseURL": "https://wordbalance-5c81f-default-rtdb.firebaseio.com",
    "messagingSenderId": "102142109232",
    "appId": "1:102142109232:web:d35ce85bb41944b1f0eff5"
}

firebase = pyrebase.initialize_app(firebase_config)
pyrebase_auth = firebase.auth()

# -------------------- Google Login Function --------------------
def google_login():
    if "user" in st.session_state:
        return st.session_state.user

    st.subheader("🔐 Login with Google")
    
    login_button = st.button("Continue with Google")

    if login_button:
        try:
            # Open Google OAuth popup (Pyrebase handles redirect automatically)
            user = pyrebase_auth.sign_in_with_google()
            
            # Get email from token
            user_info = pyrebase_auth.get_account_info(user['idToken'])
            email = user_info['users'][0]['email']
            display_name = user_info['users'][0].get('displayName', email.split("@")[0])
            
            # Check if Firebase user exists, else create
            try:
                firebase_user = admin_auth.get_user_by_email(email)
            except admin_auth.UserNotFoundError:
                firebase_user = admin_auth.create_user(
                    email=email,
                    display_name=display_name
                )

            # Save user in session
            st.session_state.user = {
                "email": firebase_user.email,
                "uid": firebase_user.uid,
                "name": firebase_user.display_name
            }

            # Rerun app to load dashboard
            st.experimental_rerun()
        
        except Exception as e:
            st.error(f"Login failed: {e}")

    return None
