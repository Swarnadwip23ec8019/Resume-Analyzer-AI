import os
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file object."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

def analyze_resume(resume_text, job_description):
    """
    Sends the resume and job description to the Gemini API to get a comprehensive analysis.
    """
    if not api_key:
        return "Error: GEMINI_API_KEY is not set. Please set it in your .env file."
    
    prompt = f"""
    You are an expert Talent Acquisition Specialist and Technical Recruiter.
    I will provide you with a Job Description and a candidate's Resume.
    Your task is to analyze the resume against the job description and provide a structured review.
    
    **Job Description:**
    {job_description}
    
    **Resume:**
    {resume_text}
    
    Please provide your analysis in the following format:
    
    ### 1. ATS Match Score
    [Provide a percentage score (e.g., 85%) of how well the resume matches the job description.]
    
    ### 2. Missing Keywords
    [List the important keywords, skills, or qualifications from the job description that are missing in the resume.]
    
    ### 3. Actionable Feedback
    [Provide 3-5 specific bullet points on how the candidate can improve their resume for this specific role.]
    
    ### 4. Practice Interview Questions
    [Generate 3 tailored interview questions based on the candidate's resume and the job requirements, and briefly explain what the interviewer would be looking for in the answer.]
    """
    
    try:
        # We use the gemini-flash-latest model
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating analysis from Gemini API: {e}"
