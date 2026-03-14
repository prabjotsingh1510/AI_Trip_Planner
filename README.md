# 🌏 Agentic AI Trip Planner

The Agentic AI Trip Planner is an intelligent, multi-agent travel assistant that generates highly detailed, personalized travel itineraries using real-time data. It provides day-by-day schedules, personalized hotel and flight recommendations, budget tracking, and interactive map visualizations.

## ✨ Features
- **Intelligent Itinerary Generation:** Get day-by-day travel plans, including attractions, activities, and dining recommendations.
- **Dynamic Budget Parsing:** Visualize your estimated expenses (Accommodation, Transportation, Food, Activities) via an interactive Donut chart.
- **Interactive Map Visualization:** See exactly where your planned destinations and accommodations are plotted on a live map.
- **Agentic Workflow Simulation:** A multi-agent framework manages tasks behind the scenes—from destination research to itinerary formatting.
- **Export to PDF:** Download and save a pristine copy of your detailed itinerary to your device.

## 🛠️ Technology Stack
- **Frontend:** Streamlit, Streamlit-Folium, Plotly Express
- **Backend:** FastAPI, Python 3.11+
- **AI & Agents:** LangGraph, LangChain, OpenAI / Groq (or configured LLM provider)

---

## 🚀 Running the Project Locally

To run the AI Trip Planner on your local machine, you need to spin up both the **FastAPI Backend** and the **Streamlit Frontend**.

### 1. Prerequisites
Ensure you have Python 3.11+ installed. Clone this repository and navigate into the project directory.

```bash
git clone https://github.com/prabjotsingh1510/AI_Trip_Planner.git
cd AI_Trip_Planner
```

### 2. Set Up the Virtual Environment & Dependencies
Create a virtual environment and install the required dependencies:

**Windows:**
```bash
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
You will need to configure your API keys for the language models and tools.
Create a `.env` file in the root directory and add the necessary environment variables (e.g., `OPENAI_API_KEY`, `TAVILY_API_KEY`, `GROQ_API_KEY`, etc.) as defined by your application logic.

### 4. Start the FastAPI Backend
Open a terminal (with your virtual environment activated) and run:

```bash
uvicorn main:app --reload --port 8000
```
*The backend should now be running at `http://localhost:8000`.*

### 5. Start the Streamlit Frontend
Open a **new** terminal window (activate the virtual environment again) and run:

```bash
streamlit run streamlit_app.py
```
*Your browser should automatically open the dashboard at `http://localhost:8501`. If it doesn't, navigate to that URL manually.*

---

## ☁️ Deployment
This application is configured for easy deployment. The FastAPI backend can be deployed to services like Render or Heroku, while the frontend is perfectly tailored for Streamlit Community Cloud. If deploying locally or somewhere else, you can point the frontend to the correct backend by setting the `API_URL` environment variable.