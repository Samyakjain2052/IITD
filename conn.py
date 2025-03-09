from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

# Import your matching system
from matching_system import MatchingSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Use your specific tokens
HUGGINGFACE_TOKEN = "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"
API_TOKEN = "napi_0mgqs6es15ugo29dv8n0ql3exbtuaksx21p752zd8odxovsy26p8pmrxnhbqw6o0"

# Initialize matching system with your tokens
matcher = MatchingSystem(HUGGINGFACE_TOKEN, API_TOKEN)

# API Routes
@app.route('/')
def home():
    return jsonify({
        'status': 'API is running',
        'endpoints': {
            'calculate_matches': '/api/calculate-matches',
            'get_matches': '/api/matches',
            'predict_job_type': '/api/job-type/<job_title>',
            'get_candidates': '/api/candidates',
            'get_jobs': '/api/jobs',
            'get_weights': '/api/weights',
            'calculate_skills_match': '/api/skills-match',
            'calculate_education_match': '/api/education-match',
            'calculate_experience_match': '/api/experience-match',
            'calculate_project_match': '/api/project-match'
        }
    })

@app.route('/api/calculate-matches', methods=['POST'])
def calculate_matches():
    """Calculate matches between resumes and jobs"""
    try:
        # You can customize the matching process based on request parameters
        request_data = request.json or {}
        candidate_id = request_data.get('candidateId')
        job_id = request_data.get('jobId')
        
        # For this example, we'll just use the existing calculate_matches method
        matches = matcher.calculate_matches()
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(matches)} match results',
            'matches': matches
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Get all matches"""
    try:
        matches = matcher.calculate_matches()
        return jsonify({
            'success': True,
            'matches': matches
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/job-type/<job_title>', methods=['GET'])
def predict_job_type(job_title):
    """Predict if a job is technical or non-technical"""
    try:
        job_type = matcher.predict_job_type(job_title)
        return jsonify({
            'success': True,
            'job_title': job_title,
            'job_type': job_type
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates from the API"""
    try:
        # Use the existing API method from the matcher
        resumes, _ = matcher.get_api_data()
        
        return jsonify({
            'success': True,
            'candidates': resumes
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs from the API"""
    try:
        # Use the existing API method from the matcher
        _, jobs = matcher.get_api_data()
        
        return jsonify({
            'success': True,
            'jobs': jobs
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/weights', methods=['GET'])
def get_weights():
    """Get current weights from the database"""
    try:
        weights = matcher.get_weights_from_db()
        return jsonify({
            'success': True,
            'weights': weights
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/skills-match', methods=['POST'])
def calculate_skills_match():
    """Calculate skills match score"""
    try:
        data = request.json
        resume_skills = data.get('resume_skills', [])
        job_skills = data.get('job_skills', [])
        
        score = matcher.calculate_skills_match(resume_skills, job_skills)
        
        return jsonify({
            'success': True,
            'skills_match_score': score
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/education-match', methods=['POST'])
def calculate_education_match():
    """Calculate education match score"""
    try:
        data = request.json
        resume_education = data.get('resume_education', [])
        job_education = data.get('job_education', {})
        
        score = matcher.calculate_education_match(resume_education, job_education)
        
        return jsonify({
            'success': True,
            'education_match_score': score
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/experience-match', methods=['POST'])
def calculate_experience_match():
    """Calculate experience match score"""
    try:
        data = request.json
        job_min_years = data.get('job_min_years', 'Not specified')
        resume_experience = data.get('resume_experience', [])
        
        score = matcher.calculate_experience_match(job_min_years, resume_experience)
        
        return jsonify({
            'success': True,
            'experience_match_score': score
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/project-match', methods=['POST'])
def calculate_project_match():
    """Calculate project match score"""
    try:
        data = request.json
        resume_projects = data.get('resume_projects', [])
        job_title = data.get('job_title', '')
        required_skills = data.get('required_skills', [])
        
        score = matcher.calculate_project_match(resume_projects, job_title, required_skills)
        
        return jsonify({
            'success': True,
            'project_match_score': score
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Run the app on port 5000
    app.run(debug=True, host='127.0.0.1', port=5000)