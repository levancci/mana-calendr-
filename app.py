import streamlit as st
import asyncio
import nest_asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from my_agent.agent import timetable_agent
from calendar_tools import construct_google_calendar_client, delete_calendar_event
import os

# Apply nest_asyncio to fix "no current event loop" errors
nest_asyncio.apply()

st.set_page_config(page_title="Mana Calendr", layout="centered")

def run_async(coro):
    """Helper to run async code safely in Streamlit."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

# Helper function to run the agent
async def run_agent_logic(runner, user_text, session_id):
    content = types.Content(role='user', parts=[types.Part(text=user_text)])
    
    # We must await the async generator
    events = runner.run_async(
        user_id="default_user", 
        session_id=session_id, 
        new_message=content
    )
    
    final_text = ""
    async for event in events:
        # Depending on ADK version, response structure might vary
        # This handles standard text responses
        if hasattr(event, 'content') and event.content and event.content.parts:
             for part in event.content.parts:
                 if part.text:
                     final_text += part.text
    return final_text

def main():
    st.title("📅 Mana Calendr")
    st.markdown("Upload your timetable and click **Schedule** to automatically sync classes to Google Calendar.")

    # --- Sidebar: Auth ---
    with st.sidebar:
        st.header("Status")
        if os.path.exists('token files/token_calendar_v3.pickle'):
            st.success("Calendar Connected ✅")
        else:
            st.warning("Not Connected ❌")
            if st.button("Connect Google Calendar"):
                try:
                    construct_google_calendar_client('credentials.json')
                    st.success("Authorized! Refresh page.")
                except Exception as e:
                    st.error(f"Auth Error: {e}")

    # --- Session Setup ---
    if "runner" not in st.session_state:
        session_service = InMemorySessionService()
        st.session_state.runner = Runner(
            agent=timetable_agent,
            app_name="mana_calendr_app",
            session_service=session_service
        )
        run_async(session_service.create_session(
            app_name="mana_calendr_app", 
            user_id="default_user", 
            session_id="session_1"
        ))
    
    # Initialize undo list if not present
    if "created_event_ids" not in st.session_state:
        st.session_state.created_event_ids = []

    # --- Simplified UI (No Chat Bar) ---
    uploaded_file = st.file_uploader("1. Upload Timetable Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="Timetable Preview", width=400)
        
        # One-Click Action Button
        if st.button("✨ Schedule My Semester", type="primary"):
            with st.spinner("Analyzing image and creating events..."):
                try:
                    prompt = "Analyze this timetable image. Extract all recurring classes and schedule them for the current semester, skipping holidays."
                    
                    # Run the agent
                    response_text = run_async(run_agent_logic(
                        st.session_state.runner, 
                        prompt, 
                        "session_1"
                    ))

                    st.success("Scheduling Complete!")
                    st.markdown(f"**Agent Report:**\n\n{response_text}")
                    
                except Exception as e:
                    error_msg = str(e)
                    if "cannot reuse already awaited coroutine" in error_msg:
                        st.warning("💡 Tip: You double-clicked! The scheduling likely finished. Check the output below or your calendar.")
                    else:
                        st.error(f"An error occurred: {e}")
                        st.info("Check that you have authenticated with Google Cloud (`gcloud auth application-default login`).")

    # --- UNDO SECTION ---
    # Only show if we have created events in this session
    if st.session_state.created_event_ids:
        st.markdown("---")
        st.warning("⚠️ **Testing Mode:** Did something go wrong? You can undo the events created in this session.")
        
        if st.button("Undo Last Batch (Delete Events)"):
            with st.spinner("Deleting events..."):
                count = 0
                # Iterate over a copy of the list
                for event_id in st.session_state.created_event_ids[:]:
                    success = delete_calendar_event('primary', event_id)
                    if success:
                        st.session_state.created_event_ids.remove(event_id)
                        count += 1
                
                if count > 0:
                    st.success(f"Successfully deleted {count} events.")
                else:
                    st.info("No events found to delete (or they were already deleted).")

if __name__ == "__main__":
    main()