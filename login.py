import streamlit as st
import requests

# Dev FitCloud URL for authentication
fitcloud_url = "https://aws-dev.fitcloud.co.kr"

st.session_state.fitcloud_url = "https://aws-dev.fitcloud.co.kr"
st.session_state.session_id = ""

# saltware code
st.session_state.corpId = "KDjAqAG0TnEAAAFK5eqDUL0A"

st.set_page_config(initial_sidebar_state="collapsed")
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)


def authenticate(username, password, mfa_code):
    # Prepare data for authentication
    data = {"userId": username, "password": password, "mfaCode": mfa_code}

    # Make a POST login request to the Dev FitCloud
    response = requests.post(fitcloud_url+"/login", json=data)

    # Check the response status
    if response.status_code == 200:
        # Parse the JSON response
        json_data = response.json()

        # Check if the authentication was successful
        if json_data.get("result", {}).get("validLogin", False):
            # Return the session ID along with the success flag
            return True, json_data.get("session_id", "")
        else:
            # Return failure with an empty session ID
            return False, ""
    else:
        # Return failure with an empty session ID
        return False, ""

def main():
    st.title("FitCloud login")

    # Input fields for username, password, and MFA code
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    mfa_code = st.text_input("MFA Code:")

    # Check if the login button is clicked
    if st.button("Login"):
        # Authenticate user
        success, session_id = authenticate(username, password, mfa_code)
        if success:
            # Add the rest of your Streamlit app code here after successful login

            # save session id
            st.session_state.session_id = session_id
            # Clear current content
            st.empty()

            # move to chatbot page
            st.switch_page('pages/chatbot.py')
           

        else:
            st.error("Invalid username, password, or MFA code. Please try again.")

if __name__ == "__main__":
    main()