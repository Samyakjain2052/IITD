import streamlit as st
import json
import re
from groq import Groq

# Set page configuration
st.set_page_config(
    page_title="Resume and Job Description Parser",
    page_icon="📄",
    layout="wide"
)

# Initialize Groq client with hardcoded API key
@st.cache_resource
def get_groq_client():
    # Replace this with your actual Groq API key
    api_key = "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"
    return Groq(api_key=api_key)

# Function to extract information from resume/job description
def extract_information(text, doc_type):
    client = get_groq_client()
    
    if doc_type == "Resume":
        system_prompt = """
        You are an expert at extracting information from resumes. 
        Extract key information from the provided resume and categorize it into structured fields.
        You must respond ONLY with a valid JSON object containing the following fields:
        
        {
          "name": "Full name of the candidate",
          "email": "Candidate's email address",
          "phone": "Contact number(s) mentioned",
          "experience": {
            "years": "Total years of experience (approximate if not explicitly stated)",
            "positions": [
              {
                "title": "Job title",
                "company": "Company name",
                "duration": "Employment period",
                "responsibilities": ["List of key responsibilities or achievements"]
              }
            ]
          },
          "education": [
            {
              "degree": "Degree obtained",
              "institution": "University/College name",
              "year": "Year of completion"
            }
          ],
          "skills": {
            "technical": ["List of technical skills"],
            "soft": ["List of soft skills if mentioned"]
          },
          "projects": [
            {
              "title": "Project title",
              "description": "Brief description",
              "technologies": ["Technologies used"]
            }
          ],
          "certifications": ["List of professional certifications"],
          "links": {
            "linkedin": "LinkedIn URL if available",
            "github": "GitHub URL if available",
            "portfolio": "Portfolio URL if available"
          },
          "summary": "Brief candidate profile or objective statement"
        }
        
        If any field is not available, use an empty string, empty array, or null as appropriate.
        Do not include any explanations or notes outside the JSON object.
        """
    else:  # Job Description
        system_prompt = """
        You are an expert at extracting information from job descriptions.
        Extract key information from the provided job description and categorize it into structured fields.
        You must respond ONLY with a valid JSON object containing the following fields:
        
        {
          "job_title": "Title of the position",
          "company": "Name of the company",
          "location": "Job location (remote/hybrid/onsite and geographical location)",
          "employment_type": "Full-time, part-time, contract, etc.",
          "salary_range": "Salary information if provided",
          "required_experience": "Years of experience required",
          "required_education": "Education requirements",
          "required_skills": ["List of required skills"],
          "preferred_skills": ["List of preferred/nice-to-have skills"],
          "responsibilities": ["List of job responsibilities"],
          "benefits": ["List of benefits offered"],
          "application_instructions": "How to apply",
          "application_deadline": "Deadline for application if mentioned",
          "about_company": "Brief description about the company"
        }
        
        If any field is not available, use an empty string, empty array, or null as appropriate.
        Do not include any explanations or notes outside the JSON object.
        """
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # or any other Groq model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=2048
        )
        
        # Extract the JSON from the response
        response_text = response.choices[0].message.content
        
        # Look for JSON in the response
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Clean response text to ensure it's valid JSON
        response_text = response_text.strip()
        if response_text.startswith('```') and response_text.endswith('```'):
            response_text = response_text[3:-3].strip()
        
        # Parse JSON
        parsed_data = json.loads(response_text)
        return parsed_data, None
    
    except Exception as e:
        return None, f"Error: {str(e)}"

# App title and description
st.title("Resume & Job Description Parser")
st.markdown("Upload a resume or job description to extract structured information in JSON format.")

# Document type selection
doc_type = st.radio("Document Type", ["Resume", "Job Description"])

# Upload option
st.subheader("Upload Document")
uploaded_file = st.file_uploader(f"Upload {doc_type}", type=["pdf", "docx", "txt"])

# Text input option
st.subheader("Or Paste Text")
text_input = st.text_area(f"Paste {doc_type} text here", height=300)

# Process button
if st.button("Extract Information"):
    with st.spinner("Processing..."):
        if uploaded_file is not None:
            # Handle file upload
            # For simplicity, we're just reading text files
            # In a full implementation, you'd need to handle PDF and DOCX files
            if uploaded_file.type == "text/plain":
                text = uploaded_file.read().decode("utf-8")
            else:
                st.error("PDF and DOCX processing requires additional libraries. Please paste the text for now.")
                st.stop()
        elif text_input:
            text = text_input
        else:
            st.error("Please upload a file or paste text to proceed.")
            st.stop()
        
        # Extract information
        result, error = extract_information(text, doc_type)
        
        if error:
            st.error(error)
        else:
            # Display the JSON
            st.subheader("Extracted Information (JSON)")
            st.json(result)
            
            # Download button for JSON
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{doc_type.lower().replace(' ', '_')}_data.json",
                mime="application/json"
            )
            
            # Display data in a more readable format
            st.subheader("Formatted View")
            
            if doc_type == "Resume":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Personal Information")
                    st.write(f"**Name:** {result.get('name', '')}")
                    st.write(f"**Email:** {result.get('email', '')}")
                    st.write(f"**Phone:** {result.get('phone', '')}")
                    
                    if result.get('links'):
                        st.markdown("### Professional Links")
                        for link_type, url in result.get('links', {}).items():
                            if url:
                                st.write(f"**{link_type.capitalize()}:** {url}")
                
                with col2:
                    if result.get('summary'):
                        st.markdown("### Summary")
                        st.write(result.get('summary', ''))
                
                st.markdown("### Experience")
                experience = result.get('experience', {})
                st.write(f"**Total Experience:** {experience.get('years', 'Not specified')}")
                
                for position in experience.get('positions', []):
                    st.markdown(f"**{position.get('title', '')} at {position.get('company', '')}**")
                    st.write(f"*{position.get('duration', '')}*")
                    st.markdown("Key Responsibilities:")
                    for resp in position.get('responsibilities', []):
                        st.markdown(f"- {resp}")
                    st.markdown("---")
                
                st.markdown("### Education")
                for edu in result.get('education', []):
                    st.write(f"**{edu.get('degree', '')}** - {edu.get('institution', '')}, {edu.get('year', '')}")
                
                st.markdown("### Skills")
                skills = result.get('skills', {})
                
                if skills.get('technical'):
                    st.markdown("**Technical Skills:**")
                    st.write(", ".join(skills.get('technical', [])))
                
                if skills.get('soft'):
                    st.markdown("**Soft Skills:**")
                    st.write(", ".join(skills.get('soft', [])))
                
                if result.get('projects'):
                    st.markdown("### Projects")
                    for project in result.get('projects', []):
                        st.markdown(f"**{project.get('title', '')}**")
                        st.write(project.get('description', ''))
                        if project.get('technologies'):
                            st.write(f"*Technologies:* {', '.join(project.get('technologies', []))}")
                        st.markdown("---")
                
                if result.get('certifications'):
                    st.markdown("### Certifications")
                    for cert in result.get('certifications', []):
                        st.markdown(f"- {cert}")
            
            else:  # Job Description
                st.markdown(f"### {result.get('job_title', '')} at {result.get('company', '')}")
                st.write(f"**Location:** {result.get('location', '')}")
                st.write(f"**Employment Type:** {result.get('employment_type', '')}")
                
                if result.get('salary_range'):
                    st.write(f"**Salary Range:** {result.get('salary_range', '')}")
                
                if result.get('about_company'):
                    st.markdown("### About the Company")
                    st.write(result.get('about_company', ''))
                
                st.markdown("### Requirements")
                st.write(f"**Experience:** {result.get('required_experience', '')}")
                st.write(f"**Education:** {result.get('required_education', '')}")
                
                if result.get('required_skills'):
                    st.markdown("**Required Skills:**")
                    for skill in result.get('required_skills', []):
                        st.markdown(f"- {skill}")
                
                if result.get('preferred_skills'):
                    st.markdown("**Preferred Skills:**")
                    for skill in result.get('preferred_skills', []):
                        st.markdown(f"- {skill}")
                
                if result.get('responsibilities'):
                    st.markdown("### Responsibilities")
                    for resp in result.get('responsibilities', []):
                        st.markdown(f"- {resp}")
                
                if result.get('benefits'):
                    st.markdown("### Benefits")
                    for benefit in result.get('benefits', []):
                        st.markdown(f"- {benefit}")
                
                if result.get('application_instructions') or result.get('application_deadline'):
                    st.markdown("### Application Details")
                    if result.get('application_instructions'):
                        st.write(f"**How to Apply:** {result.get('application_instructions', '')}")
                    if result.get('application_deadline'):
                        st.write(f"**Deadline:** {result.get('application_deadline', '')}")

# Footer
st.markdown("---")
st.markdown("**Note:** This application extracts structured information from your documents. No data is stored.")