import pprint
from django.http import HttpResponse
from django.http import JsonResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from bson import ObjectId
import pymongo

client = MongoClient('mongodb+srv://dharaneesh0745:Dhoni_007@cluster0.evk57.mongodb.net/sih')
db = client["sih"]
printer = pprint.PrettyPrinter(indent=4)

def home(request):
    return HttpResponse("WELCOME TO GIGA-MEGA RECOMMENDER use /recommender/userid to get recommendations")

printer = pprint.PrettyPrinter(indent=4)

def preprocess_text(text):

    return text.lower().strip()


def job_recommendations(request, user_id):
    if request.method == 'GET':
        
        user_id = ObjectId(user_id)
        user = db.users.find_one({"_id": user_id})
        
        user_skills = (preprocess_text("".join(user["nonTechnicalSkills"] +" " + user["technicalSkills"] + " " + user["city"])))
        if not user_skills:
            return JsonResponse({"error": "User has no skills listed"}, status=400)

        jobs = list(db.jobs.find({}))
        job_descriptions = [preprocess_text("".join(job["category"]+ " " + job['location'] + " " + job["skills"] + " " + job["jobType"])) for job in jobs]


        if not any(job_descriptions):
            return JsonResponse({"error": "No job descriptions available"}, status=404)

        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        job_vectors = tfidf_vectorizer.fit_transform(job_descriptions)
        user_vector = tfidf_vectorizer.transform([user_skills])
        print(job_vectors)
        print("User Vector Shape:", user_vector.shape)
        print("Job Vectors Shape:", job_vectors.shape)
        # Compute cosine similarity
        similarity_scores = cosine_similarity(user_vector, job_vectors).flatten()

        recommended_jobs = sorted(zip(jobs, similarity_scores), key=lambda x: x[1], reverse=True)

        response_data = {
            "user_details": {
                "id": str(user["_id"]),
                "name": f"{user['firstName']} {user['lastName']}",
                "skills": f"{user["technicalSkills"]} {user['nonTechnicalSkills']}",
            },
            "recommended_jobs": [
                {
                    "_id": str(job["_id"]),
                    "title": job["title"],
                    "category": job["category"],
                    "salary": job["salary"],
                    "companyId": str(job["companyId"]),
                    "employer": {"_id":str(job["employer"]["_id"]),
                                 "companyName": job["employer"]["companyName"],
                                 "employerName": job["employer"]["employerName"],
                                 "employerEmail": job["employer"]["employerEmail"],
                                 "employerPhone": job["employer"]["employerPhone"],
                                 "avatar": job["employer"]["avatar"],
                                 "companyVerification": job["employer"]["companyVerification"],
                                 "createdAt": job["employer"]["createdAt"],
                                 },
                    "images": job["images"],
                    "location": job["location"],
                    "experience": job["experience"],
                    "skills": job["skills"],
                    "jobType": job["jobType"],
                    "locationType": job["locationType"],
                    "education": job["education"],
                    "deadline": job["deadline"],
                    "vacancy": job["vacancy"],
                    "date": job["date"],
                    "createdAt": job["createdAt"],
                    "similarity_score": round(score, 2)
                } for job, score in recommended_jobs if score > 0
            ]
        }
        
        # Print and return the response
        printer.pprint(response_data)
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "Unsupported HTTP method"}, status=405)
