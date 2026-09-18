import os
import streamlit as st
import requests
import json

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Verdant AI", layout="wide")
st.title("Verdant AI - Biodiversity Intelligence")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trace" not in st.session_state:
    st.session_state.trace = None

# Sidebar for structured inputs
with st.sidebar:
    st.header("Structured Inputs (Optional)")
    rainfall = st.number_input("Rainfall (mm)", min_value=0, value=None)
    ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=None)
    slope = st.number_input("Slope (%)", min_value=0.0, value=None)
    land_use = st.selectbox("Land Use", ["", "arable", "pasture", "orchard", "forest", "degraded", "wetland"])
    has_water = st.checkbox("Has adjacent water body?")
    
    st.markdown("---")
    if st.button("Reset Session"):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.session_state.trace = None
        st.rerun()

# Main chat area
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "recommendations" in msg and msg["recommendations"]:
            for rec in msg["recommendations"]:
                with st.expander(f"🌲 {rec.get('intervention_name', 'Intervention')}"):
                    st.write("**What to do:**", rec.get("what_to_do", ""))
                    st.write("**Scientific Explanation:**", rec.get("scientific_explanation", ""))
                    st.write("**Metrics Improved:**", ", ".join(rec.get("metrics_improved", [])))
                    st.write("**Citations:**", ", ".join(rec.get("evidence_citations", [])))

if user_input := st.chat_input("Describe your land parcel or ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    structured_data = {}
    if rainfall is not None: structured_data["rainfall"] = rainfall
    if ph is not None: structured_data["ph"] = ph
    if slope is not None: structured_data["slope_percent"] = slope
    if land_use: structured_data["land_use"] = land_use
    structured_data["has_water_body"] = has_water

    payload = {
        "session_id": st.session_state.session_id,
        "user_input": user_input,
        "structured_inputs": structured_data
    }
    
    with st.spinner("Analyzing..."):
        try:
            resp = requests.post(f"{API_URL}/chat", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.session_id = data["session_id"]
                
                reply_content = data.get("clarifying_question") or data.get("message", "")
                recs = data.get("recommendations", [])
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply_content,
                    "recommendations": recs
                })
                
                # Fetch trace
                trace_resp = requests.get(f"{API_URL}/trace/{st.session_state.session_id}")
                if trace_resp.status_code == 200:
                    st.session_state.trace = trace_resp.json()
                
                st.rerun()
            else:
                st.error("API Error")
        except Exception as e:
            st.error(f"Connection failed: {e}")

# Trace Panel
if st.session_state.trace:
    with st.expander("🔍 System Retrieval Trace", expanded=False):
        t = st.session_state.trace
        st.write(f"**Cards Evaluated:** {t.get('evaluated_cards', 0)}")
        st.write(f"**Cards Passed:** {t.get('passed_cards', 0)}")
        
        if t.get("rejections"):
            st.write("### Rejections (Hard Rules)")
            for r in t["rejections"]:
                st.write(f"- **{r['card_id']}**: {r['reason']}")
                
        if t.get("scores"):
            st.write("### Scores (Feasible Interventions)")
            st.json(t["scores"])
            
        if t.get("retrieved_chunks"):
            st.write("### Retrieved Evidence (ChromaDB)")
            for c in t["retrieved_chunks"]:
                st.info(f"**{c.get('source_id')} (Page {c.get('page')})** Score: {c.get('score'):.3f}\n\n{c.get('snippet')}")
