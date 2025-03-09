import requests
import json

def extract_resume_data():
    """Extract and display resume data from the API"""
    base_url = "https://iit-api-1.onrender.com"
    endpoint = "/api/resumes"
    
    headers = {
        "Authorization": "Bearer napi_0mgqs6es15ugo29dv8n0ql3exbtuaksx21p752zd8odxovsy26p8pmrxnhbqw6o0"
    }

    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print("\n=== Resume Data ===")
        for i, record in enumerate(data, 1):
            print(f"\nResume #{i}:")
            print("Technical Skills:", record.get('technicalSkills', []))
            print("Experience:", record.get('experience', []))
            print("Education:", record.get('education', []))
            
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")

def extract_job_description_data():
    """Extract and display job description data from the API"""
    base_url = "https://iit-api-1.onrender.com"
    endpoint = "/api/job-descriptions"
    
    headers = {
        "Authorization": "Bearer napi_0mgqs6es15ugo29dv8n0ql3exbtuaksx21p752zd8odxovsy26p8pmrxnhbqw6o0"
    }

    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print("\n=== Job Description Data ===")
        for i, record in enumerate(data, 1):
            print(f"\nJob #{i}:")
            print("Required Skills:", record.get('requiredSkills', []))
            print("Preferred Skills:", record.get('preferredSkills', []))
            
            # Extract and parse experience requirements
            exp_req_str = record.get('experienceRequirements', '{}')
            try:
                exp_req = json.loads(exp_req_str) if isinstance(exp_req_str, str) else exp_req_str
                min_years = exp_req.get('minimum_years', 'Not specified')
                print(f"Minimum Years of Experience: {min_years}")
            except json.JSONDecodeError:
                print("Experience Requirements: Could not parse JSON")
            
            # Extract and parse education requirements
            edu_req_str = record.get('educationRequirements', '{}')
            try:
                edu_req = json.loads(edu_req_str) if isinstance(edu_req_str, str) else edu_req_str
                min_degree = edu_req.get('minimum_degree',[])
                pref_fields = edu_req.get('preferred_fields', [])
                print(f"Minimum Degree Required: {min_degree}")
                print(f"Preferred Fields: {pref_fields}")
            except json.JSONDecodeError:
                print("Education Requirements: Could not parse JSON")
            
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")

if __name__ == "__main__":
    # Extract both resume and job description data
    extract_resume_data()
    extract_job_description_data()