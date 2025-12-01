# 📅 Clarity
> **From Paper to Plan: The Agentic Schedule Automator.**

[![Powered by Google ADK](https://img.shields.io/badge/Powered%20by-Google%20ADK-4285F4?style=flat-square&logo=google)](https://github.com/google/adk-python)
[![Model](https://img.shields.io/badge/Model-Gemini%201.5%20Pro-8E44AD?style=flat-square)](https://deepmind.google/technologies/gemini/)
[![Built With](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)

---

### ![unnamed](https://github.com/user-attachments/assets/aeab0592-7230-417a-91cc-3ee6dcd67abe)

---

## 🚩 The Problem: Administrative Burnout
Every semester, students and professionals face the same nightmare: taking a static image of a timetable (a screenshot, a printed grid, or a handwritten note) and manually inputting every single recurring event into their digital calendar.

It’s boring, error-prone, and time-consuming. A single mistake in setting recurrence rules can mess up your schedule for months. We have self-driving cars, so why are we still manually typing "Calculus 101" thirty times into a calendar app?

## 💡 The Solution
**Clarity** is an intelligent AI agent that cures this administrative burnout.

It is a **"Vision-to-Action"** system. You simply upload an image of your schedule, and the agent visually "reads" the grid, understands time slots, and autonomously syncs your entire semester to Google Calendar.

**Key Capabilities:**
* **👀 Multimodal Vision:** Uses **Gemini 1.5 Pro** to visually interpret complex grid layouts that baffle standard OCR.
* **🔄 Complex Recurrence:** Automatically calculates `RRULE` (recurrence rules) to schedule classes for the next 3 months.
* **🏝️ Holiday Intelligence:** Checks against a database of public holidays (e.g., Farmer's Day, Christmas) and adds `EXDATE` exceptions so you don't show up to class when school is closed.
* **🛡️ Human-in-the-Loop:** Includes "Lazy Authentication" and an "Undo" feature, ensuring the AI never modifies your calendar without permission or a safety net.

---

## 🏗️ Architecture

This project is built on a modular **Agentic Workflow** using Google's **Agent Development Kit (ADK)**.

### <img width="2816" height="1536" alt="Gemini_Generated_Image_d0lkf2d0lkf2d0lk" src="https://github.com/user-attachments/assets/bb813713-1bd5-43d1-9e0b-b18fc979f0b2" />


**The Stack:**
1.  **Frontend (Streamlit):** Manages the user interface and the asynchronous event loop (`nest_asyncio`) for real-time agent interaction.
2.  **Orchestrator (Google ADK):** The `Runner` and `InMemorySessionService` manage the state and conversation history between the user and the model.
3.  **Brain (Gemini 1.5 Pro):** A Vertex AI model that accepts raw image bytes to perform visual reasoning and extraction.
4.  **Tools (`tools.py`):** Custom Python functions that handle date math, holiday exclusions, and API calls.
5.  **Integration (Google Calendar API):** Uses OAuth 2.0 for secure, user-authorized calendar access.

---

## 🚀 Setup & Installation

Follow these steps to run the agent locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/mana-calendr.git](https://github.com/levancci/mana-calendr-.git)
cd mana-calendr 
```


### 2. Install Dependencies
Make sure you have Python 3.10+ installed.

```bash

pip install -r requirements.txt
```
###3. Google Cloud Setup
Go to the Google Cloud Console.

Create a new project and enable the Google Calendar API.

Configure the OAuth Consent Screen (add your email as a test user).

Create OAuth Client ID credentials (Desktop App).

Download the JSON file, rename it to credentials.json, and place it in the root directory.

### 4. Configure Environment
Create a .env file in the root directory and add your Google Cloud Project details:

```Code snippet

GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
```
(Note: Ensure you have authenticated via CLI: gcloud auth application-default login)

### 5. Run the Agent
```Bash

streamlit run app.py 
```
🎮 How to Use
![Screenshot 2025-12-01 181839](https://github.com/user-attachments/assets/246dd542-0588-4c31-99cb-292433ac4158)

Upload: Drag and drop your timetable image into the app.

Schedule: Click the "✨ Schedule My Semester" button.

Authorize: If it's your first time, a browser window will pop up asking for permission to access your calendar.

Relax: Watch as the agent analyzes the image and populates your calendar.

Undo (Optional): Made a mistake? Use the "Undo Last Batch" button to instantly wipe the events created in the current session.

### 🛡️ Safety & Security
Least Privilege: The agent only requests calendar scope when explicitly triggered by the user.

Local Token Storage: OAuth tokens are stored locally (token files/) and are never sent to external servers.

Session Isolation: The ADK Runner isolates sessions, preventing data leakage between potential users.

