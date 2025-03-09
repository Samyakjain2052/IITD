import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import fitz  # PyMuPDF for PDF extraction
import re
import json
import requests
from typing import Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio
import time

app = FastAPI(title="Resume ATS Scoring API", 
              description="API for scoring resumes against job descriptions")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize sentence transformer model (BERT-based) for text embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Lightweight model

class WeightsModel(BaseModel):
    skills: float = 0.5
    experience: float = 0.3
    education: float = 0.2

class ProcessResult(BaseModel):
    candidate_name: str
    candidate_email: str
    ats_score: float
    skill_match: Dict[str, List[str]]
    experience_match: float
    education_match: float
    processing_time: float

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file using PyMuPDF"""
    try:
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction error: {str(e)}")

def extract_candidate_info(resume_text):
    """Extract basic candidate information from resume text"""
    # Extract email using regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, resume_text)
    email = email_match.group(0) if email_match else "Not found"
    
    # Extract name (simplified approach - assume name is at the beginning)
    # In a real application, this would need more robust name extraction
    lines = resume_text.strip().split('\n')
    name = lines[0].strip() if lines else "Not found"
    
    return {"name": name, "email": email}

async def analyze_with_groq(text, prompt):
    """Use Groq API to analyze text based on prompt"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",  # Fast model with good performance
            "messages": [
                {"role": "system", "content": "You are an expert resume analyzer and recruiter."},
                {"role": "user", "content": f"{prompt}\n\nText to analyze:\n{text}"}
            ],
            "temperature": 0.1,  # Low temperature for more deterministic results
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise HTTPException(status_code=500, detail=f"Groq API error: {response.text}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Groq API: {str(e)}")

async def extract_skills(resume_text, job_description):
    """Extract and categorize skills using Groq API"""
    prompt = """
    Analyze the provided text and extract a comprehensive list of technical and soft skills. 
    Then, compare these skills with the job description that follows and categorize them as:
    1. Must-Have (skills explicitly required in the job description)
    2. Good-to-Have (skills that are beneficial but not explicitly required)
    3. Other (skills not relevant to the job description)
    
    Return the results in JSON format with these categories as keys and arrays of skills as values:
    {
        "must_have": ["skill1", "skill2", ...],
        "good_to_have": ["skill1", "skill2", ...],
        "other": ["skill1", "skill2", ...]
    }
    """
    
    combined_text = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"
    result = await analyze_with_groq(combined_text, prompt)
    
    try:
        # Extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        
        skills_data = json.loads(result)
        return skills_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing skills data: {str(e)}")

async def analyze_experience(resume_text, job_description):
    """Analyze experience match using Groq API"""
    prompt = """
    Analyze the candidate's years of experience and job roles from the resume text.
    Then compare with the job description requirements and provide:
    1. Total years of relevant experience
    2. A match score from 0.0 to 1.0 indicating how well the experience matches the job requirements
    3. Brief explanation of the score
    
    Return the results in JSON format:
    {
        "years": number,
        "score": number,
        "explanation": "string"
    }
    """
    
    combined_text = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"
    result = await analyze_with_groq(combined_text, prompt)
    
    try:
        # Extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
            
        experience_data = json.loads(result)
        return experience_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing experience data: {str(e)}")

async def analyze_education(resume_text, job_description):
    """Analyze education match using Groq API"""
    prompt = """
    Analyze the candidate's education from the resume text including degrees, institutions, and fields of study.
    Then compare with the job description requirements and provide:
    1. Highest degree obtained
    2. Field of study
    3. A match score from 0.0 to 1.0 indicating how well the education matches the job requirements
    
    Return the results in JSON format:
    {
        "highest_degree": "string",
        "field": "string",
        "score": number
    }
    """
    
    combined_text = f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"
    result = await analyze_with_groq(combined_text, prompt)
    
    try:
        # Extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
            
        education_data = json.loads(result)
        return education_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing education data: {str(e)}")

def calculate_skills_score(skills_data):
    """Calculate skills score based on matched skills"""
    must_have_count = len(skills_data.get("must_have", []))
    good_to_have_count = len(skills_data.get("good_to_have", []))
    total_skills = must_have_count + good_to_have_count + 1  # Add 1 to avoid division by zero
    
    # Weight must-have skills higher
    score = (must_have_count * 1.5 + good_to_have_count * 0.75) / total_skills
    return min(score, 1.0)  # Cap at 1.0

def calculate_ats_score(skills_score, experience_score, education_score, weights):
    """Calculate overall ATS score based on component scores and weights"""
    normalized_weights = {
        "skills": weights.skills / sum([weights.skills, weights.experience, weights.education]),
        "experience": weights.experience / sum([weights.skills, weights.experience, weights.education]),
        "education": weights.education / sum([weights.skills, weights.experience, weights.education])
    }
    
    ats_score = (
        skills_score * normalized_weights["skills"] +
        experience_score * normalized_weights["experience"] +
        education_score * normalized_weights["education"]
    )
    
    # Scale to 0-100
    return round(ats_score * 100, 1)

@app.post("/score-resume", response_model=ProcessResult)
async def score_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    weights: str = Form(...),
):
    """
    Score a resume against a job description with weighted criteria
    """
    start_time = time.time()
    
    try:
        # Parse weights
        weights_data = WeightsModel(**json.loads(weights))
        
        # Extract text from PDF
        contents = await resume.read()
        resume_text = extract_text_from_pdf(contents)
        
        # Extract basic candidate info
        candidate_info = extract_candidate_info(resume_text)
        
        # Process resume in parallel
        skills_task = asyncio.create_task(extract_skills(resume_text, job_description))
        experience_task = asyncio.create_task(analyze_experience(resume_text, job_description))
        education_task = asyncio.create_task(analyze_education(resume_text, job_description))
        
        # Wait for all tasks to complete
        skills_data = await skills_task
        experience_data = await experience_task
        education_data = await education_task
        
        # Calculate component scores
        skills_score = calculate_skills_score(skills_data)
        experience_score = experience_data["score"]
        education_score = education_data["score"]
        
        # Calculate final ATS score
        ats_score = calculate_ats_score(skills_score, experience_score, education_score, weights_data)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return ProcessResult(
            candidate_name=candidate_info["name"],
            candidate_email=candidate_info["email"],
            ats_score=ats_score,
            skill_match={
                "must_have": skills_data.get("must_have", []),
                "good_to_have": skills_data.get("good_to_have", []),
                "other": skills_data.get("other", [])
            },
            experience_match=experience_score,
            education_match=education_score,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)