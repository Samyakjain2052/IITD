from huggingface_hub import login
from sentence_transformers import SentenceTransformer, util
import torch
import re
from datetime import datetime
import json
import requests

class MatchingSystem:
    def __init__(self, huggingface_token, api_token):
        """Initialize the matching system"""
        self.model = self._initialize_model(huggingface_token)
        self.api_token = api_token
        self.base_url = "https://iit-api-1.onrender.com"
    
    def _initialize_model(self, token):
        """Initialize the sentence transformer model"""
        login(token)
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def get_api_data(self):
        """Fetch data from API endpoints"""
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }

        try:
            # Get resumes
            resume_response = requests.get(
                f"{self.base_url}/api/resumes",
                headers=headers
            )
            resume_response.raise_for_status()
            resumes = resume_response.json()

            # Get job descriptions
            job_response = requests.get(
                f"{self.base_url}/api/job-descriptions",
                headers=headers
            )
            job_response.raise_for_status()
            jobs = job_response.json()

            return resumes, jobs

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return [], []

    def calculate_skills_match(self, resume_skills, job_skills):
        """Calculate similarity between resume skills and job requirements"""
        if not resume_skills or not job_skills:
            return 0.0
        
        resume_embeddings = self.model.encode(resume_skills, convert_to_tensor=True)
        job_embeddings = self.model.encode(job_skills, convert_to_tensor=True)
        
        similarity_matrix = util.cos_sim(resume_embeddings, job_embeddings)
        return float(torch.mean(torch.max(similarity_matrix, dim=1)[0]))

    def parse_experience(self, experience_text):
        """Extract years of experience from text"""
        if not experience_text:
            return 0
            
        years_pattern = r'\((\d{4})\s*-\s*(\d{4})\)'
        match = re.search(years_pattern, experience_text)
        
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            current_year = datetime.now().year
            
            if end_year > current_year:
                years = current_year - start_year
            else:
                years = end_year - start_year
            return max(0, years)
        return 0

    def calculate_experience_match(self, job_min_years, resume_experience):
        """Calculate experience match score"""
        if not resume_experience:
            return 0.0
            
        resume_years = self.parse_experience(resume_experience[0])
        
        try:
            min_years = int(job_min_years) if job_min_years != "Not specified" else 0
            if resume_years < min_years:
                return max(0, resume_years / min_years)
            return 1.0
        except (ValueError, TypeError):
            return 0.0

    def calculate_education_match(self, resume_education, job_education):
        """Calculate education match score"""
        if not resume_education or not job_education:
            return 0.0
        
        resume_edu = " ".join(resume_education) if isinstance(resume_education, list) else str(resume_education)
        job_min_degree = job_education.get('minimum_degree', '')
        job_pref_fields = job_education.get('preferred_fields', [])
        
        # Create embeddings
        resume_embedding = self.model.encode([resume_edu], convert_to_tensor=True)
        job_embedding = self.model.encode([job_min_degree] + job_pref_fields, convert_to_tensor=True)
        
        # Calculate similarity
        similarity = util.cos_sim(resume_embedding, job_embedding)
        return float(torch.max(similarity))

    def calculate_matches(self):
        """Calculate comprehensive match scores"""
        resumes, jobs = self.get_api_data()
        matches = []
        
        for resume in resumes:
            resume_name = resume.get('name', 'Unknown Candidate')
            
            for job in jobs:
                # Calculate individual scores
                skills_score = self.calculate_skills_match(
                    resume.get('technicalSkills', []),
                    job.get('requiredSkills', [])
                )
                
                # Handle experience requirements parsing
                exp_req_str = job.get('experienceRequirements', '{}')
                try:
                    exp_req = json.loads(exp_req_str) if isinstance(exp_req_str, str) else exp_req_str
                    min_years = exp_req.get('minimum_years', 'Not specified')
                except (json.JSONDecodeError, AttributeError):
                    min_years = 'Not specified'
                
                exp_score = self.calculate_experience_match(
                    min_years,
                    resume.get('experience', [])
                )
                
                # Handle education requirements parsing
                edu_req_str = job.get('educationRequirements', '{}')
                try:
                    edu_req = json.loads(edu_req_str) if isinstance(edu_req_str, str) else edu_req_str
                except (json.JSONDecodeError, AttributeError):
                    edu_req = {}
                
                edu_score = self.calculate_education_match(
                    resume.get('education', []),
                    edu_req
                )
                
                # Calculate weighted total score
                total_score = (
                    (skills_score * 0.35) +  # 35% weight for skills
                    (exp_score * 0.35) +     # 35% weight for experience
                    (edu_score * 0.30)       # 30% weight for education
                )
                
                matches.append({
                    'candidate_name': resume_name,
                    'job_title': job.get('title', 'Unknown Position'),
                    'skills_match': skills_score,
                    'experience_match': exp_score,
                    'education_match': edu_score,
                    'total_score': total_score,
                    'required_skills': job.get('requiredSkills', []),
                    'candidate_skills': resume.get('technicalSkills', [])
                })
        
        return sorted(matches, key=lambda x: x['total_score'], reverse=True)

def main():
    # API and Hugging Face tokens
    HUGGINGFACE_TOKEN = "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"
    API_TOKEN = "napi_0mgqs6es15ugo29dv8n0ql3exbtuaksx21p752zd8odxovsy26p8pmrxnhbqw6o0"
    
    # Initialize matching system
    matcher = MatchingSystem(HUGGINGFACE_TOKEN, API_TOKEN)
    
    # Calculate and display matches
    matches = matcher.calculate_matches()
    
    print("\n=== Match Results ===")
    for match in matches:
        print(f"\nCandidate: {match['candidate_name']}")
        print(f"Job: {match['job_title']}")
        print(f"Required Skills: {', '.join(match['required_skills'])}")
        print(f"Candidate Skills: {', '.join(match['candidate_skills'])}")
        print(f"Skills Match: {match['skills_match']:.2f}")
        print(f"Experience Match: {match['experience_match']:.2f}")
        print(f"Education Match: {match['education_match']:.2f}")
        print(f"Total Score: {match['total_score']:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    main()