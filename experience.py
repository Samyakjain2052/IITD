def experience_match(job_experience, resume_experience):
    """
    Calculates experience match score based on job requirements.

    Args:
    - job_experience (tuple or str): Experience range (e.g., (0,5)) or "5+" format.
    - resume_experience (int): Candidate's experience in years.

    Returns:
    - int: Matching value or penalty.
    """
    
    if isinstance(job_experience, tuple):  # Case: (min, max) range
        min_exp, max_exp = job_experience
        if resume_experience < min_exp:
            return resume_experience - min_exp  # Negative penalty
        elif resume_experience > max_exp:
            return resume_experience - max_exp  # Positive penalty
        else:
            return resume_experience  # Within range, return as it is

    elif isinstance(job_experience, str) and job_experience.endswith("+"):  # Case: "5+"
        required_exp = int(job_experience[:-1])  # Extract number (e.g., "5+" → 5)
        return resume_experience - required_exp  # Return difference

    else:
        raise ValueError("Invalid job experience format")

# 🔹 Test Cases
print(experience_match((0, 5), 3))  # Output: 3 (within range)
print(experience_match((0, 5), 6))  # Output: 1 (exceeds max, penalty)
print(experience_match((0, 5), 0))  # Output: 0 (within range)
print(experience_match((0, 5), -1)) # Output: -1 (below min, penalty)
print(experience_match("5+", 3))    # Output: -2 (3 years but 5+ required)
print(experience_match("5+", 6))    # Output: 1 (extra experience)

