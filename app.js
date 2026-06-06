// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

// DOM Elements
const apiKeyInput = document.getElementById('api-key');
const toggleKeyBtn = document.getElementById('toggle-key-visibility');
const jobDescriptionInput = document.getElementById('job-description');
const dropZone = document.getElementById('drop-zone');
const resumeUpload = document.getElementById('resume-upload');
const fileNameDisplay = document.getElementById('file-name');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const resultsSection = document.getElementById('results-section');
const resultsContent = document.getElementById('results-content');

// Markdown parser
const md = window.markdownit({
    html: true,
    linkify: true,
    typographer: true
});

let extractedResumeText = "";

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load API key from local storage if exists
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) {
        apiKeyInput.value = savedKey;
    }
});

// Toggle API Key Visibility
toggleKeyBtn.addEventListener('click', () => {
    const type = apiKeyInput.getAttribute('type') === 'password' ? 'text' : 'password';
    apiKeyInput.setAttribute('type', type);
    const icon = toggleKeyBtn.querySelector('i');
    icon.classList.toggle('fa-eye');
    icon.classList.toggle('fa-eye-slash');
});

// File Upload Handling
dropZone.addEventListener('click', () => resumeUpload.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    handleFiles(files);
});

resumeUpload.addEventListener('change', function() {
    handleFiles(this.files);
});

async function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    if (file.type !== "application/pdf") {
        alert("Please upload a PDF file.");
        return;
    }

    fileNameDisplay.innerHTML = `<span style="color: var(--success)"><i class="fa-solid fa-check-circle"></i> ${file.name} uploaded successfully</span>`;
    
    // Extract text immediately to save time later
    try {
        extractedResumeText = await extractTextFromPDF(file);
    } catch (error) {
        console.error("PDF Extraction Error:", error);
        fileNameDisplay.innerHTML = `<span style="color: var(--error)"><i class="fa-solid fa-triangle-exclamation"></i> Error extracting text from PDF.</span>`;
        extractedResumeText = "";
    }
}

async function extractTextFromPDF(file) {
    const fileReader = new FileReader();
    return new Promise((resolve, reject) => {
        fileReader.onload = async function() {
            const typedarray = new Uint8Array(this.result);
            try {
                const pdf = await pdfjsLib.getDocument(typedarray).promise;
                let fullText = "";
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    const pageText = textContent.items.map(item => item.str).join(' ');
                    fullText += pageText + " ";
                }
                resolve(fullText);
            } catch (error) {
                reject(error);
            }
        };
        fileReader.readAsArrayBuffer(file);
    });
}

// Analyze Button Click
analyzeBtn.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();
    const jobDescription = jobDescriptionInput.value.trim();

    if (!apiKey) {
        alert("Please enter your Google Gemini API Key.");
        return;
    }
    
    if (!jobDescription) {
        alert("Please enter the target job description.");
        return;
    }

    if (!extractedResumeText) {
        alert("Please upload a valid PDF resume.");
        return;
    }

    // Save API key
    localStorage.setItem('gemini_api_key', apiKey);

    // UI State: Loading
    analyzeBtn.disabled = true;
    loadingOverlay.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    // API Call
    try {
        const promptText = `
        You are an expert Talent Acquisition Specialist and Technical Recruiter.
        I will provide you with a Job Description and a candidate's Resume.
        Your task is to analyze the resume against the job description and provide a structured review.
        
        **Job Description:**
        ${jobDescription}
        
        **Resume:**
        ${extractedResumeText}
        
        Please provide your analysis in the following format using Markdown:
        
        ### 1. ATS Match Score
        [Provide a percentage score (e.g., 85%) of how well the resume matches the job description, with a brief sentence explaining why.]
        
        ### 2. Missing Keywords
        [List the important keywords, skills, or qualifications from the job description that are missing in the resume. Use a bulleted list.]
        
        ### 3. Actionable Feedback
        [Provide 3-5 specific bullet points on how the candidate can improve their resume for this specific role.]
        
        ### 4. Practice Interview Questions
        [Generate 3 tailored interview questions based on the candidate's resume and the job requirements. Briefly explain what the interviewer would be looking for in the answer.]
        `;

        // Gemini REST API Request
        // Using gemini-1.5-flash for fast and accurate processing
        const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=${apiKey}`;
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: promptText
                    }]
                }]
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error?.message || 'Failed to communicate with Gemini API');
        }

        const markdownText = data.candidates[0].content.parts[0].text;
        
        // Render Markdown to HTML
        resultsContent.innerHTML = md.render(markdownText);
        
        // Show results
        loadingOverlay.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error("API Error:", error);
        alert(`Analysis Error: ${error.message}`);
        loadingOverlay.classList.add('hidden');
    } finally {
        analyzeBtn.disabled = false;
    }
});
