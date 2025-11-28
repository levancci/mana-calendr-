import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from my_agent.agent import timetable_agent
from calendar_tools import construct_google_calendar_client
import os

st.set_page_config(page_title="ADK Timetable Scheduler", layout="wide")

def main():
    st.title("🇬🇭 Visual Timetable Scheduler (ADK Powered)")
    st.markdown("Upload your timetable. This agent uses **Google Gemini** to see the image and **ADK** to schedule recurring events on your Google Calendar.")

    # --- Sidebar: Auth & Setup ---
    with st.sidebar:
        st.header("Setup")
        if os.path.exists('token files/token_calendar_v3.pickle'):
            st.success("Calendar Connected ✅")
        else:
            if st.button("Connect Google Calendar"):
                try:
                    construct_google_calendar_client('credentials.json')
                    st.success("Authorized! Refresh page.")
                except Exception as e:
                    st.error(f"Auth Error: {e}")

    # --- Session State: ADK Runner ---
    if "runner" not in st.session_state:
        # The Runner manages the chat session and state for us
        st.session_state.runner = Runner(
            app_name="scheduler-app",
            agent=timetable_agent,
            session_service=InMemorySessionService()
        )
        st.session_state.chat_history = []

    # --- Chat Interface ---
    # Display History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Inputs ---
    col1, col2 = st.columns([1, 3])
    with col1:
        uploaded_file = st.file_uploader("Upload Timetable", type=["jpg", "png", "jpeg"])
    
    # We use a chat input for natural language instructions
    user_input = st.chat_input("Type 'Schedule this' or ask questions...")

    if user_input:
        # 1. Handle User Input
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            if uploaded_file:
                st.image(uploaded_file, caption="Attached Timetable", width=300)

        # 2. Run ADK Agent
        with st.chat_message("assistant"):
            with st.spinner("Agent is working..."):
                try:
                    # Prepare attachments if any
                    attachments = []
                    if uploaded_file:
                        # ADK supports passing the file object directly or bytes
                        # We pass the raw bytes content for the model
                        attachments = [uploaded_file] 

                    # Run the agent
                    response = st.session_state.runner.run(
                        input=user_input,
                        attachments=attachments
                    )

                    # Display Response
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})

                except Exception as e:
                    st.error(f"Agent Error: {e}")

if __name__ == "__main__":
    main()