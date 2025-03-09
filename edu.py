from huggingface_hub import login
from sentence_transformers import SentenceTransformer, util
import torch

# 🔹 Replace with your Hugging Face API Token
HUGGINGFACE_TOKEN = "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"

# 🔹 Authenticate with Hugging Face
login(HUGGINGFACE_TOKEN)

# 🔹 Load the SentenceTransformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 🔹 Define education details
job_education_requirements = [
    "Graduate from Tier 1 college", 
    "Master's degree in Computer Science", 
    "PhD in AI/ML"
]

candidate_education = [
    "B.Tech from IIT Delhi", 
    "M.Tech from NIT Trichy", 
    "PhD in Deep Learning from MIT"
]

# 🔹 Convert education details to embeddings
job_embeddings = model.encode(job_education_requirements, convert_to_tensor=True)
resume_embeddings = model.encode(candidate_education, convert_to_tensor=True)

# 🔹 Compute cosine similarity
similarity_matrix = util.cos_sim(resume_embeddings, job_embeddings)

# 🔹 Print similarity scores
print("🔹 Cosine Similarity Matrix:")
print(similarity_matrix)

# 🔹 Find the best match for each resume education
for i, resume_edu in enumerate(candidate_education):
    best_match_idx = torch.argmax(similarity_matrix[i]).item()
    best_match_job_edu = job_education_requirements[best_match_idx]
    best_score = similarity_matrix[i][best_match_idx].item()

    print(f"🔹 Candidate Education: {resume_edu}")
    print(f"   ✅ Best Match: {best_match_job_edu} (Score: {best_score:.4f})\n")
