import streamlit as st
import datetime
import requests
import os
import json
import re
import time
import threading
import queue
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium
from markdown_pdf import MarkdownPdf, Section
import tempfile

# Backend Point: Use environment variable for deployment, fallback to localhost for local runs
BASE_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Agentic AI Trip Planner",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for UI/UX improvements
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Hide header and top right menu */
    div[data-testid="stHeader"] {
        display: none;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Modern Card styling */
    .metric-card {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        text-align: center;
        transition: transform 0.2s ease;
        color: var(--text-color);
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #3b82f6;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 14px;
        color: var(--text-color);
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Recommendation Card styling */
    .rec-card {
        background-color: var(--secondary-background-color);
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 12px;
        color: var(--text-color);
    }
    
    .rec-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 5px;
        color: var(--text-color);
    }
    
    .rec-badge {
        display: inline-block;
        padding: 4px 8px;
        background-color: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    /* Timeline styling */
    .timeline-title {
        font-size: 20px;
        color: var(--text-color);
        font-weight: 600;
        margin-bottom: 15px;
    }
    .timeline-event {
        margin-bottom: 10px;
        padding-left: 15px;
        border-left: 2px solid #3b82f6;
        color: var(--text-color);
    }
    
    /* Global Text Fixes */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trip_data" not in st.session_state:
    st.session_state.trip_data = None
if "trip_markdown" not in st.session_state:
    st.session_state.trip_markdown = None

def fetch_plan(payload, result_queue):
    """Fetch data from the backend in a separate thread."""
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        if response.status_code == 200:
            result_queue.put({"status": "success", "data": response.json().get("answer", "")})
        else:
            result_queue.put({"status": "error", "error": f"Error: {response.text}"})
    except Exception as e:
        result_queue.put({"status": "error", "error": str(e)})

def render_metric_card(label, value, icon=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
    
def render_rec_card(item):
    st.markdown(f"""
    <div class="rec-card">
        <div class="rec-title">{item.get('name', 'Unknown')}</div>
        <div style="margin-bottom: 8px;">
            <span class="rec-badge">{item.get('category', 'Place')}</span>
            <span style="font-size: 14px; color: #f59e0b;">★ {item.get('rating', 'N/A')}</span>
        </div>
        <div style="font-size: 14px; color: #4b5563;">{item.get('description', '')}</div>
    </div>
    """, unsafe_allow_html=True)

def create_pdf_bytes(markdown_text):
    """Convert markdown string to a PDF byte stream."""
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(markdown_text))
    
    # Generate a temporary file path but don't hold it open (Windows lock issue)
    tmp_path = os.path.join(tempfile.gettempdir(), f"trip_itinerary_{int(time.time())}.pdf")
    
    try:
        # MarkdownPdf uses a synchronous save to path
        pdf.save(tmp_path)
        
        # Read the generated file back into bytes
        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()
    finally:
        # Always attempt to clean up the temporary file
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass
        
    return pdf_bytes



# Main Area Header
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <img src='https://cdn-icons-png.flaticon.com/512/3225/3225110.png' width='80'>
    <h1 style='color: var(--text-color); margin-top: 10px;'>Agentic AI Trip Planner</h1>
    <p style='font-size: 18px; color: #6c757d;'>Your highly intelligent, multi-agent powered travel assistant.</p>
</div>
""", unsafe_allow_html=True)
st.divider()

# Chat Interface
st.subheader("💬 Chat with AI Travel Planner")

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("E.g. Plan a 3 day trip to Goa under ₹25000...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        q = queue.Queue()
        payload = {"question": user_input}
        t = threading.Thread(target=fetch_plan, args=(payload, q))
        t.start()
        
        # Simulated Agent Workflow Visualizer
        workflow_steps = [
            ("🔍 Destination Research Agent is analyzing the location...", 3.0),
            ("🏠 Hotel Finder Agent is sourcing accommodations...", 3.0),
            ("📅 Itinerary Planner Agent is generating the daily schedule...", 4.0),
            ("💰 Budget Analyzer Agent is calculating expenses...", 3.0),
            ("🎨 Formatting the JSON and Markdown response...", 2.0)
        ]
        
        with st.status("🤖 Multi-Agent System initializing...", expanded=True) as status_container:
            for step_text, wait_time in workflow_steps:
                st.write(step_text)
                
                # Check queue frequently while waiting
                start = time.time()
                done = False
                while time.time() - start < wait_time:
                    if not q.empty():
                        done = True
                        break
                    time.sleep(0.5)
                
                if done: break
                
            # If backend is slow, keep waiting
            if q.empty():
                st.write("⏳ AI is finalizing the massive travel plan. This may take a minute...")
                while q.empty():
                    time.sleep(1.0)
            
            status_container.update(label="Trip plan generated successfully!", state="complete", expanded=False)
            
        # Process Results
        result = q.get()
        if result["status"] == "error":
            st.error(result["error"])
        else:
            raw_text = result["data"]
            
            # Extract JSON block securely via regex and forcefully truncate it out of the visible markdown
            json_pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL | re.IGNORECASE)
            json_match = json_pattern.search(raw_text)
            
            parsed_data = None
            clean_markdown = raw_text
            
            if json_match:
                try:
                    parsed_data = json.loads(json_match.group(1))
                    # Remove the JSON completely from the visible text output
                    clean_markdown = raw_text[:json_match.start()]
                    
                    # Robustly remove any conversational preamble right before the JSON block
                    lines = clean_markdown.split('\n')
                    while lines and (not lines[-1].strip() or re.search(r'(?i)(json|structured data|here is the)', lines[-1])):
                        lines.pop()
                    clean_markdown = '\n'.join(lines).strip()
                    
                except Exception as e:
                    st.warning("Could not parse structured data from the agent response. Fallback to raw text.")
            
            # Clean up LangGraph Tool Call leakage (e.g., `(<function=search_restaurants>{"place": "Paris"})`)
            function_leak_pattern = re.compile(r'\(\<function=[^>]+>\{[^}]+\}\)', re.IGNORECASE)
            clean_markdown = function_leak_pattern.sub('', clean_markdown)
            
            # Clean up alternate tool call formats that might leak like `<function=...>` without parentheses
            alt_leak_pattern = re.compile(r'\<function=[^>]+>\{[^}]+\}', re.IGNORECASE)
            clean_markdown = alt_leak_pattern.sub('', clean_markdown)

            # Strip any trailing whitespace or generic formatting artifacts that often accompany appended data blocks
            clean_markdown = re.sub(r'(\n\s*)+\Z', '', clean_markdown).strip()
            
            st.session_state.trip_data = parsed_data
            st.session_state.trip_markdown = clean_markdown
            
            st.session_state.messages.append({"role": "assistant", "content": "I have planned your trip! See the interactive dashboard below for the detailed itinerary, budget charts, and map."})
            st.markdown("I have planned your trip! The detailed dashboard below has been updated.")
            
            # Need to rerun to show the dashboard
            time.sleep(1.5)
            st.rerun()

st.divider()

# Only show the dashboard if we have parsed JSON data
if st.session_state.trip_data and st.session_state.trip_markdown:
    data = st.session_state.trip_data
    
    # 1. Dashboard Metrics
    st.subheader("📊 Trip Overview")
    m1, m2, m3, m4 = st.columns(4)
    ov = data.get("trip_overview", {})
    with m1:
        render_metric_card("Duration", f"{ov.get('trip_duration_days', 'N/A')} Days", "🕰️")
    with m2:
        render_metric_card("Budget", f"{ov.get('currency', 'INR')} {ov.get('total_estimated_budget', 'N/A')}", "💰")
    with m3:
        render_metric_card("Attractions", f"{ov.get('total_attractions', 0)} Places", "📸")
    with m4:
        render_metric_card("Restaurants", f"{ov.get('total_restaurants', 0)} Places", "🍽️")
        
    st.write("")
    st.write("")
    
    t1, t2 = st.columns([2, 1])
    
    with t1:
        # 2. Detailed Itinerary
        st.subheader("📅 Detailed Itinerary")
        st.markdown(st.session_state.trip_markdown, unsafe_allow_html=True)
        
        # 3. Map Visualization
        map_data = data.get("destination_map", {})
        if "center_lat" in map_data and "center_lon" in map_data:
            st.subheader("🗺️ Destination Map")
            # Upgrade map tiles for a more vivid aesthetic
            m = folium.Map(location=[map_data["center_lat"], map_data["center_lon"]], zoom_start=11, tiles="OpenStreetMap")
            
            for marker in map_data.get("markers", []):
                is_hotel = marker.get("type", "").lower() == "hotel"
                
                # Custom HTML marker to make pins "pop"
                icon_html = f"""
                <div style="background-color: {'#e11d48' if is_hotel else '#2563eb'}; 
                            color: white; border-radius: 50%; width: 30px; height: 30px;
                            display: flex; justify-content: center; align-items: center;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.3); font-size: 14px;
                            border: 2px solid white;">
                    {"🏨" if is_hotel else "📍"}
                </div>
                """
                custom_icon = folium.DivIcon(html=icon_html, icon_size=(30, 30), icon_anchor=(15, 15))
                
                folium.Marker(
                    [marker["lat"], marker["lon"]], 
                    popup=folium.Popup(f"<b>{marker.get('name')}</b><br>{marker.get('type', 'Location').title()}", max_width=200),
                    tooltip=marker.get("name"),
                    icon=custom_icon
                ).add_to(m)
                
            st_folium(m, width=700, height=400, returned_objects=[])

    with t2:
        # 4. Budget Chart
        st.subheader("💸 Budget Distribution")
        budget_dist = data.get("budget_distribution", {})
        if budget_dist:
            df = pd.DataFrame(list(budget_dist.items()), columns=['Category', 'Cost'])
            # Create an appealing Donut Chart instead of a generic flat Pie
            fig = px.pie(df, values='Cost', names='Category', hole=0.55, 
                         color_discrete_sequence=px.colors.qualitative.Bold)
            
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hoverinfo='label+percent+value',
                marker=dict(line=dict(color='#ffffff', width=2))
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=0, r=0), 
                height=350,
                showlegend=False,
                annotations=[dict(text=f"Total<br>{ov.get('currency', '')} {ov.get('total_estimated_budget', '')}", 
                             x=0.5, y=0.5, font_size=18, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
            
        # 5. Recommendation Cards
        st.subheader("⭐ Top Recommendations")
        recs = data.get("recommendations", [])
        for rec in recs:
            render_rec_card(rec)
            
        # 6. Export Options
        st.write("")
        st.subheader("📥 Export Plan")
        with st.container(border=True):
            st.markdown("<p style='font-size: 14px; color: #6c757d; margin-bottom: 10px;'>Save a copy of your full itinerary and budget structure to your device.</p>", unsafe_allow_html=True)
            try:
                pdf_data = create_pdf_bytes(st.session_state.trip_markdown)
                st.download_button(
                    label="📁 Download PDF Itinerary",
                    data=pdf_data,
                    file_name=f"Trip_Plan_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.warning(f"PDF generation failed. Fallback to base Markdown.")
                st.download_button(
                    label="📝 Download Plan",
                    data=st.session_state.trip_markdown,
                    file_name=f"Trip_Plan_{datetime.datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
