import streamlit as st
import asyncio
import nest_asyncio; nest_asyncio.apply() # Uncomment if you see event loop errors
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from my_agent.agent import timetable_agent
from calendar_tools import construct_google_calendar_client
import os

st.set_page_config(page_title="ADK Timetable Scheduler", layout="wide")

def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        return asyncio.get_event_loop().run_until_complete(coro)

async def run_agent(agent_runner, user_text, session_id):
    content = types.Content(role='user', parts=[types.Part(text=user_text)])
    events = agent_runner.run_async(
        user_id="streamlit_user", 
        session_id=session_id, 
        new_message=content
    )
    final_text = ""
    async for event in events:
        if hasattr(event, 'content') and event.content and event.content.parts:
             for part in event.content.parts:
                 if part.text:
                     final_text += part.text
    return final_text

def main():
    st.title("🇬🇭 Visual Timetable Scheduler (ADK Powered)")
    st.markdown("Upload your timetable. Click **Schedule** to sync events to your Google Calendar.")

    # --- Session State ---
    if "session_id" not in st.session_state:
        st.session_state.session_id = "session_001"
        st.session_state.session_service = InMemorySessionService()
        st.session_state.runner = Runner(
            agent=timetable_agent,
            app_name="timetable_app",
            session_service=st.session_state.session_service
        )
        run_async(st.session_state.session_service.create_session(
            app_name="timetable_app", 
            user_id="streamlit_user", 
            session_id=st.session_state.session_id
        ))
        st.session_state.chat_history = []

    # --- UI Layout ---
    col1, col2 = st.columns([1, 3])
    with col1:
        uploaded_file = st.file_uploader("Upload Timetable", type=["jpg", "png", "jpeg"])
    
    # Simple Action Button (No chat input required for user)
    if st.button("📅 Schedule Events", type="primary"):
        if not uploaded_file:
            st.error("Please upload an image first.")
            return

        with st.spinner("Checking Authorization & Analyzing..."):
            # 1. Check Authorization ON CLICK
            if not os.path.exists('token files/token_calendar_v3.pickle'):
                st.warning("Google Calendar authorization required. A browser window will open...")
                try:
                    # This will trigger the browser popup flow
                    construct_google_calendar_client('credentials.json')
                    st.success("Authorized! Proceeding with scheduling...")
                except Exception as e:
                    st.error(f"Authorization failed: {e}")
                    return

            # 2. Run Agent
            try:
                # Prompt the agent to look at the image and schedule
                user_instruction = "Analyze this timetable image and schedule all recurring classes for the semester."
                
                # Note: For real image support, ensure your ADK setup handles the file bytes.
                # Here we assume the agent execution flow logic remains as previously set up.
                response_text = run_async(run_agent(
                    st.session_state.runner, 
                    user_instruction, 
                    st.session_state.session_id
                ))

                st.markdown("### Agent Response")
                st.markdown(response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})

            except Exception as e:
                st.error(f"Agent Error: {e}")

if __name__ == "__main__":
    main()