# IITD

IITD Resume Matcher
This project is a resume analysis and job title prediction system developed using Python and Natural Language Processing (NLP) techniques. It aims to assist in matching resumes to suitable job titles by analyzing the content of the resumes.

Features
Resume Parsing: Extracts and processes information from resumes.

Job Title Prediction: Utilizes a machine learning model to predict appropriate job titles based on resume content.

TF-IDF Vectorization: Applies Term Frequency-Inverse Document Frequency (TF-IDF) for text feature extraction.

Pre-trained Model: Includes a pre-trained model (model.pkl) for job title prediction.

Dataset: Employs a dataset of 5,000 job titles (job_titles_dataset_5000.csv) for training and evaluation.

Docker Support: Provides a Dockerfile for containerized deployment.

Getting Started
Prerequisites
Python 3.x

pip

Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/Samyakjain2052/IITD.git
cd IITD
Install the required packages:

bash
Copy
Edit
pip install -r requirements.txt
Usage
To run the main application:

bash
Copy
Edit
  python main.py
To test the job prediction functionality:

bash
Copy
Edit
  python job_pred.py
To perform a simple test:

bash
Copy
Edit
  python simple_test.py
Docker Deployment
Build the Docker image:

bash
Copy
Edit
docker build -t resume-matcher .
Run the Docker container:

bash
Copy
Edit
docker run -p 8000:8000 resume-matcher
File Structure
main.py: Main application script.

job_pred.py: Script for job title prediction.

simple_test.py: Script for simple testing.

model.pkl: Pre-trained machine learning model.

tfidf.pkl: TF-IDF vectorizer.

job_titles_dataset_5000.csv: Dataset of job titles.

requirements.txt: List of required Python packages.

Dockerfile: Docker configuration file.

Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

License
This project is licensed under the MIT License.
