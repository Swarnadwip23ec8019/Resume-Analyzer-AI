import streamlit as st
import os
from dotenv import load_dotenv
import resume_analyzer

# Load environment variables
load_dotenv()

# Set page config for better aesthetics
st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve aesthetics
st.markdown("""
<style>
    /* Premium Dark Theme & Glassmorphism for Streamlit */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.15), transparent 30%),
            radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.15), transparent 30%);
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Gradient Title */
    div[data-testid="stVerticalBlock"] > div.element-container:nth-child(1) h1 {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Primary Button */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 20px -10px rgba(139, 92, 246, 0.5) !important;
        display: block;
        margin: 0 auto;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 25px -10px rgba(139, 92, 246, 0.7) !important;
    }

    /* Inputs and Text Areas */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    }

    /* File Uploader */
    .stFileUploader>div>div {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 2px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebar"] input[type="password"] {
        background: rgba(15, 23, 42, 0.6) !important;
        color: white !important;
        border-radius: 8px !important;
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

if st.button("Analyze Resume"):
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
