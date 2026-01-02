import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
from streamlit.runtime.scriptrunner.script_runner import RerunException
from streamlit.runtime.scriptrunner import get_script_run_ctx
import os

# -------------------- Firebase Admin Setup --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)

# -------------------- Google OAuth Config --------------------
GOOGLE_CLIENT_ID = "48992185146-upbvm8mdsl2d18f35affa74is5llrdqe.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
REDIRECT_URI = "https://wordbalance.streamlit.app/"  # change to deployed URL when live

# -------------------- Google Login Function --------------------
def google_login():
    if "user" in st.session_state:
        return st.session_state.user

    st.subheader("🔐 Login with Google")

    # Step 1: Show Google login link
    login_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=email%20profile"
        "&access_type=offline"
    )

    st.markdown(f"[🔐 Continue with Google]({login_url})")

    # Step 2: Get code from URL params
    code = st.query_params.get("code")
    if code:
        code = code[0]  # streamlit query_params returns list

        # Step 3: Exchange code for access token
        try:
            token_req = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            ).json()

            access_token = token_req.get("access_token")
            if not access_token:
                st.error("Failed to get access token. Check Google OAuth setup.")
                return None

            # Step 4: Get user info from Google
            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                params={"access_token": access_token}
            ).json()

            email = userinfo["email"]
            display_name = userinfo.get("name", email.split("@")[0])

            # Step 5: Create Firebase user if not exists
            try:
                firebase_user = auth.get_user_by_email(email)
            except auth.UserNotFoundError:
                firebase_user = auth.create_user(email=email, display_name=display_name)

            # Step 6: Save user in session
            st.session_state.user = {
                "email": firebase_user.email,
                "uid": firebase_user.uid,
                "name": firebase_user.display_name
            }

            # Step 7: Clear code param and rerun
            st.query_params.clear()
            ctx = get_script_run_ctx()
            if ctx is not None:
                raise RerunException(ctx)

        except Exception as e:
            st.error(f"Login failed: {e}")

    return None
