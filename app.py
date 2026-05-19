from flask import Flask, render_template, request, jsonify
import os
import joblib
from model import extract_text
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

# username = os.getenv("DB_USER")
# password = os.getenv("DB_PASSWORD")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

model = joblib.load("model/resume_model.pkl")

print("Model loaded. Classes:", model.classes_)



DATABASE_URL = "sqlite:///resume.db"

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_text TEXT,
            predicted_role TEXT,
            score REAL
        )
    """))
    connection.commit()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chat_history = []

skills_list = [
    "Python",
    "Java",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "JavaScript",
    "React",
    "HTML",
    "CSS",
    "NLP"
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():

    file = request.files["resume"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    resume_text = extract_text(filepath)

    prediction = model.predict([resume_text])[0]

    found_skills = []

    for skill in skills_list:

        if skill.lower() in resume_text.lower():
            found_skills.append(skill)

    proba = model.predict_proba([resume_text])[0]
    confidence = round(float(proba.max()) * 100, 2)
    score = confidence

    with engine.connect() as connection:

        query = text("""
            INSERT INTO resumes
            (resume_text, predicted_role, score)
            VALUES (:resume_text, :predicted_role, :score)
        """)

        connection.execute(query, {
            "resume_text": resume_text,
            "predicted_role": prediction,
            "score": score
        })

        connection.commit()

    return jsonify({
    "predicted_role": prediction,
    "skills": found_skills,
    "score": score,
    "confidence": f"{confidence}%",
    "model_classes": list(model.classes_)
})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    chat_history.append({
        "role": "user",
        "content": user_message
    })

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert AI career coach and resume advisor. 
                Help users improve their resumes, suggest skills to learn, 
                recommend jobs based on their profile, and answer career questions. 
                Be concise and practical."""
            }
        ] + chat_history,
        temperature=0.7,
        max_tokens=500
    )

    reply = response.choices[0].message.content

    chat_history.append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)