import requests

# Base URL
base_url = "https://iit-api-1.onrender.com"

# Endpoint to check
endpoint = "/api/job-descriptions"

# Set headers with your API key
headers = {
    "Authorization": "Bearer napi_0mgqs6es15ugo29dv8n0ql3exbtuaksx21p752zd8odxovsy26p8pmrxnhbqw6o0"
}

# Make the GET request
response = requests.get(
    base_url + endpoint,
    headers=headers
)

# Print the response status code
print(f"Status Code: {response.status_code}")

# Print the raw response content
print(f"Response Content: {response.text}")

# Try to parse JSON only if the content seems valid
if response.text.strip():
    try:
        print(f"JSON Response: {response.json()}")
    except requests.exceptions.JSONDecodeError:
        print("Could not parse response as JSON")