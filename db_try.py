import requests

base_url = "https://iit-api-1.onrender.com"
endpoint = "/upload/resume"
resume_file_path = "resume.pdf"

with open(resume_file_path, "rb") as file:
    # Try with different field names
    files = {"resume": (resume_file_path, file, "application/pdf")}
    
    headers = {
        "Authorization": "Bearer napi_0mgqs6es15ugo29dv8n0ql3exbtuaksx21p752zd8odxovsy26p8pmrxnhbqw6o0"
    }
    
    response = requests.post(
        base_url + endpoint,
        files=files,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")