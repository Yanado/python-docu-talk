import sys
import os

import streamlit as st

# Get absolute path to project root
root_dir = os.path.dirname(os.path.abspath(__file__))

# Add all relevant paths
sys.path.insert(0, root_dir)  # Make root directory first in path
for path in ["src/frontend", "src/backend"]:
    abs_path = os.path.join(root_dir, path)
    if abs_path not in sys.path:
        sys.path.append(abs_path)

from src.frontend.st_docu_talk import StreamlitDocuTalk  # noqa: E402

if "app" not in st.session_state:
    st.session_state["app"] = StreamlitDocuTalk()
    st.rerun()

app : StreamlitDocuTalk = st.session_state["app"]

if app.auth.logged_in is False:
    pg = st.navigation(
        [
            st.Page("src/frontend/pages/auth.py", title="Auth")
        ],
        position="hidden"
    )
else:
    pg = st.navigation(
        [
            st.Page("src/frontend/pages/home.py", title="Home", default=True),
            st.Page("src/frontend/pages/chatbot.py", title="Docu Talk"),
            st.Page("src/frontend/pages/create-chatbot.py", title="Create Chat Bot"),
            st.Page("src/frontend/pages/settings.py", title="Settings"),
            st.Page("src/frontend/pages/chatbot-settings.py", title="Chat Bot Settings")
        ],
        position="hidden"
    )

pg.run()
