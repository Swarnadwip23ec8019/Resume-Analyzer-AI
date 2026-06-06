import streamlit as st
import os
from dotenv import load_dotenv
import resume_analyzer

# Load environment variables
load_dotenv()

# Set page config for better aesthetics
st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve aesthetics
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #2b2b2b;
        font-family: 'Inter', sans-serif;
    }
    h2, h3 {
        color: #4a4a4a;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTextArea>div>div>textarea {
        border-radius: 5px;
    }
    .stFileUploader>div>div>button {
        color: #4CAF50;
        border-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Smart Resume Analyzer & Interview Prep")
st.markdown("""
Welcome! Upload your resume and paste the job description you are targeting. 
Our AI will analyze your profile and provide a match score, missing keywords, and tailored interview prep.
""")

# Check for API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    st.sidebar.warning("⚠️ GEMINI_API_KEY is missing or invalid.")
    st.sidebar.markdown("Please set your Gemini API key in the `.env` file to use this app.")
    user_api_key = st.sidebar.text_input("Or enter your API key here:", type="password")
    if user_api_key:
        os.environ["GEMINI_API_KEY"] = user_api_key
        import google.generativeai as genai
        genai.configure(api_key=user_api_key)
        st.sidebar.success("API Key loaded for this session!")

# Create two columns layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Target Job Description")
    job_description = st.text_area(
        "Paste the job description here:",
        height=300,
        placeholder="e.g., We are looking for a Software Engineer with experience in Python, React, and AWS..."
    )

with col2:
    st.subheader("2. Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    
    if uploaded_file is not None:
        st.success("Resume uploaded successfully!")
        # We can optionally show a preview or just wait for analysis

st.markdown("---")

if st.button("🚀 Analyze Resume"):
    if not job_description.strip():
        st.error("Please provide a job description.")
    elif uploaded_file is None:
        st.error("Please upload your resume.")
    elif not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
        st.error("Please provide a valid Gemini API key in the sidebar or `.env` file.")
    else:
        with st.spinner("Our AI is analyzing your resume... Please wait."):
            # 1. Extract text
            resume_text = resume_analyzer.extract_text_from_pdf(uploaded_file)
            
            if resume_text.startswith("Error"):
                st.error(resume_text)
            else:
                # 2. Analyze using Gemini
                analysis_result = resume_analyzer.analyze_resume(resume_text, job_description)
                
                # 3. Display results
                st.subheader("📊 Analysis Results")
                st.markdown(analysis_result)

st.sidebar.markdown("---")
st.sidebar.markdown("**Powered by:**")
st.sidebar.markdown("- Streamlit")
st.sidebar.markdown("- Google Gemini API")
