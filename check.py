from huggingface_hub import login
from sentence_transformers import SentenceTransformer, util
import torch

# 🔹 Replace with your Hugging Face API Token
HUGGINGFACE_TOKEN = "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"

# 🔹 Authenticate with Hugging Face
login(HUGGINGFACE_TOKEN)

# 🔹 Load the SentenceTransformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 🔹 Define two lists
resume_keywords = [
    "Machine Learning", 
    "Data Science", 
    "Python Developer", 
    "NLP", 
    "Deep Learning"
]

job_keywords = [
    "Machine Learning Engineer", 
    "Artificial Intelligence", 
    "Python", 
    "Neural Networks", 
    "Computer Vision"
]

# 🔹 Convert keywords to embeddings
resume_embeddings = model.encode(resume_keywords, convert_to_tensor=True)
job_embeddings = model.encode(job_keywords, convert_to_tensor=True)

# 🔹 Compute cosine similarity between two lists
similarity_matrix = util.cos_sim(resume_embeddings, job_embeddings)

# 🔹 Print similarity scores
print("🔹 Cosine Similarity Matrix:")
print(similarity_matrix)

# 🔹 Find the best match for each resume keyword
for i, resume_kw in enumerate(resume_keywords):
    best_match_idx = torch.argmax(similarity_matrix[i]).item()
    best_match_job_kw = job_keywords[best_match_idx]
    best_score = similarity_matrix[i][best_match_idx].item()

    print(f"🔹 Resume Keyword: {resume_kw}")
    print(f"   ✅ Best Match: {best_match_job_kw} (Score: {best_score:.4f})\n")
