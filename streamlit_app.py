import streamlit as st
import requests
import os
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a sustainability and packaging expert specializing in Life Cycle Assessment (LCA), ESG (Environmental, Social, Governance) reporting, "
    "and materiality analysis for packaging. Answer user questions as an industry authority, using up-to-date standards, real-world examples, and "
    "clear explanations tailored to packaging solutions."
)

def ask_groq(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"API Error {e.response.status_code}: {e.response.text}")
        else:
            st.error(f"Request failed: {e}")
        return None
    except KeyError as e:
        st.error(f"Unexpected API response format: {e}")
        return None

def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        st.error(f"Could not read PDF: {e}")
    return text

def summarize_and_benchmark_esg(text):
    prompt = (
        "Below is the extracted text from a company's ESG report. "
        "Please provide:\n"
        "1. A concise summary of the company's ESG performance.\n"
        "2. A benchmarking analysis compared to industry standards or leaders (if possible).\n"
        "3. Key recommendations for improvement.\n"
        "Here is the ESG report:\n"
        "-----\n"
        f"{text[:3500]}\n-----\n"
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    return ask_groq(messages)

def ai_sustainability_assessment(material, weight, recyclable, renewable):
    prompt = (
        f"Packaging parameters:\n"
        f"- Material: {material}\n"
        f"- Weight: {weight} grams\n"
        f"- Recyclable: {'Yes' if recyclable else 'No'}\n"
        f"- Made from renewable resources: {'Yes' if renewable else 'No'}\n\n"
        "Based on these, provide:\n"
        "1. A sustainability score out of 10 (with justification).\n"
        "2. A brief assessment and recommendations for improvement."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    return ask_groq(messages)

# --- Carbon Footprint Estimator ---
def estimate_carbon_footprint(material, weight, distance):
    # Example emission factors (kg CO2e per kg material, and per ton-km for transport)
    material_factors = {
        "Plastic": 2.5,
        "Glass": 1.2,
        "Aluminum": 10.0,
        "Paper": 1.0,
        "Bioplastic": 1.5,
        "Compostable": 1.2,
        "Other": 2.0
    }
    transport_factor = 0.1 / 1000  # 0.1 kg CO2e per ton-km, converted to per gram-km

    material_factor = material_factors.get(material, 2.0)
    # Convert grams to kg for material emissions
    material_emissions = (weight / 1000) * material_factor
    # Transport emissions: weight in grams * distance in km * transport_factor
    transport_emissions = weight * distance * transport_factor
    total_emissions = material_emissions + transport_emissions
    return material_emissions, transport_emissions, total_emissions

def carbon_footprint_tab():
    st.subheader("🌍 Carbon Footprint Estimator")
    st.markdown("Estimate the carbon footprint of your packaging based on material, weight, and transport distance.")

    material = st.selectbox("Material Type", ["Plastic", "Glass", "Aluminum", "Paper", "Bioplastic", "Compostable", "Other"], key="cf_material")
    weight = st.number_input("Weight (grams)", min_value=0.0, step=0.1, key="cf_weight")
    distance = st.number_input("Transport Distance (km)", min_value=0.0, step=0.1, key="cf_distance")

    if st.button("🌱 Estimate Carbon Footprint"):
        material_em, transport_em, total_em = estimate_carbon_footprint(material, weight, distance)
        st.markdown("### 🧮 Carbon Footprint Results")
        st.markdown(f"""
        <div class='result-box'>
        <b>Material Emissions:</b> {material_em:.3f} kg CO₂e<br>
        <b>Transport Emissions:</b> {transport_em:.3f} kg CO₂e<br>
        <b>Total Estimated Emissions:</b> <span style="color:#66bb6a;font-size:1.2em">{total_em:.3f} kg CO₂e</span>
        </div>
        """, unsafe_allow_html=True)
        st.info("Emission factors are approximate and for demonstration only.")

def main():
    st.set_page_config(
        page_title="Sustainability Packaging Chatbot",
        page_icon="🌱",
        layout="wide"
    )

    st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
        }
        .main-title {
            font-size: 3rem;
            color: #2E7D32;
            font-weight: 800;
        }
        .sub-header {
            font-size: 1.25rem;
            background: rgba(102, 187, 106, 0.15);
            padding: 16px 24px;
            border-left: 5px solid #66bb6a;
            margin-bottom: 24px;
            border-radius: 10px;
            color: #1b5e20;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(3px);
            transition: all 0.3s ease;
        }
        .chat-box{
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        .result-box {
            background-color: #1e1e1e;
            color: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            line-height: 1.6;
            font-size: 1.05rem;
        }
    </style>
    <h1 class='main-title'>🌱 Sustainability Packaging Chatbot</h1>
    <div class='sub-header'>Expert insights on LCA, ESG reporting, and packaging sustainability</div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat",
        "📄 ESG Report Analyzer",
        "♻️ Score Calculator",
        "🌍 Carbon Footprint Estimator"
    ])

    with st.sidebar:
        st.header("📘 About")
        st.markdown("""
        This assistant helps with:
        - 🌍 Life Cycle Assessment (LCA)
        - 📊 ESG reporting
        - ♻️ Sustainable packaging
        - 📋 Materiality analysis
        """)
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not set. Please check your .env file.")
        st.stop()

    with tab1:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Type your sustainability question here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            conversation = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = ask_groq(conversation)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.error("Could not get a response from the model.")

    with tab2:
        st.subheader("📄 ESG Report Analysis")
        st.markdown("Upload your ESG report (PDF) to get AI-powered benchmarking and insights.")

        uploaded_file = st.file_uploader("📤 Upload PDF", type="pdf")
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
            if st.button("🔍 Analyze Report"):
                with st.spinner("Extracting and analyzing..."):
                    text = extract_text_from_pdf(uploaded_file)
                    if text.strip():
                        result = summarize_and_benchmark_esg(text)
                        if result:
                            st.markdown("### 📊 ESG Summary")
                            st.markdown(f"<div class='result-box'>{result}</div>", unsafe_allow_html=True)
                            st.download_button("📥 Download Report", result, file_name="esg_analysis.txt")
                        else:
                            st.error("Failed to analyze report.")
                    else:
                        st.error("No readable text found in PDF.")

    with tab3:
        st.subheader("♻️ Sustainability Score Calculator")
        st.markdown("Evaluate your packaging impact using AI.")

        col1, col2 = st.columns(2)
        with col1:
            material = st.selectbox("Material Type", ["Plastic", "Glass", "Aluminum", "Paper", "Bioplastic", "Compostable", "Other"])
            weight = st.number_input("Weight (grams)", min_value=0.0, step=0.1)
        with col2:
            recyclable = st.radio("Is it recyclable?", ["Yes", "No"]) == "Yes"
            renewable = st.radio("From renewable sources?", ["Yes", "No"]) == "Yes"

        if st.button("📈 Get Sustainability Score"):
            with st.spinner("Generating analysis..."):
                result = ai_sustainability_assessment(material, weight, recyclable, renewable)
                if result:
                    st.markdown("### 🧠 AI Assessment")
                    st.markdown(f"<div class='result-box'>{result}</div>", unsafe_allow_html=True)
                else:
                    st.error("AI could not generate a response.")

    with tab4:
        carbon_footprint_tab()

if __name__ == "__main__":
    main()