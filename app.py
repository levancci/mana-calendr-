import streamlit as st
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from my_agent.agent import timetable_agent
from calendar_tools import construct_google_calendar_client
import os

st.set_page_config(page_title="ADK Timetable Scheduler", layout="wide")

# Helper to run async code in Streamlit
def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # If an event loop is already running (e.g. in some notebook/server envs)
        return asyncio.get_event_loop().run_until_complete(coro)

async def run_agent(agent_runner, user_text, session_id):
    # Construct the content object expected by ADK
    content = types.Content(role='user', parts=[types.Part(text=user_text)])
    
    # ADK uses async generators for responses
    events = agent_runner.run_async(
        user_id="streamlit_user", 
        session_id=session_id, 
        new_message=content
    )
    
    final_text = ""
    async for event in events:
        # Check for final response or tool outputs
        if hasattr(event, 'content') and event.content and event.content.parts:
             for part in event.content.parts:
                 if part.text:
                     final_text += part.text
    return final_text

def main():
    st.title("🇬🇭 Visual Timetable Scheduler (ADK Powered)")
    st.markdown("Upload your timetable. This agent uses **Google Gemini** to see the image and **ADK** to schedule recurring events.")

    # --- Sidebar ---
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

    # --- Session State ---
    if "session_id" not in st.session_state:
        st.session_state.session_id = "session_001"
        st.session_state.session_service = InMemorySessionService()
        st.session_state.runner = Runner(
            agent=timetable_agent,
            app_name="timetable_app",
            session_service=st.session_state.session_service
        )
        # Create session once
        run_async(st.session_state.session_service.create_session(
            app_name="timetable_app", 
            user_id="streamlit_user", 
            session_id=st.session_state.session_id
        ))
        st.session_state.chat_history = []

    # --- Chat UI ---
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    col1, col2 = st.columns([1, 3])
    with col1:
        uploaded_file = st.file_uploader("Upload Timetable", type=["jpg", "png", "jpeg"])
    
    user_input = st.chat_input("Type 'Schedule this' or ask questions...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            if uploaded_file:
                st.image(uploaded_file, caption="Attached Timetable", width=300)

        with st.chat_message("assistant"):
            with st.spinner("Agent is working..."):
                try:
                    # Note: Passing images in Streamlit to ADK often requires 
                    # converting the file to a specific Part or Blob type supported by the Model.
                    # For simplicity, we pass the text prompt first. 
                    # If you need image support, you append a Blob part to the 'content' object 
                    # inside the run_agent function.
                    
                    response_text = run_async(run_agent(
                        st.session_state.runner, 
                        user_input, 
                        st.session_state.session_id
                    ))

                    st.markdown(response_text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})

                except Exception as e:
                    st.error(f"Agent Error: {e}")

if __name__ == "__main__":
    main()