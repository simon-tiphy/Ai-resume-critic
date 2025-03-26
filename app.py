
# from flask import Flask, request
# from flask_restful import Api, Resource
# from flask_cors import CORS
# import pdfminer.high_level
# import io
# import re

# app = Flask(__name__)
# api = Api(app)
# CORS(app)  # Enable CORS for frontend requests

# def clean_text(text):
#     """Cleans extracted text by removing extra spaces and fixing line breaks."""
#     text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
#     text = text.strip()  # Remove leading/trailing spaces
#     return text

# class ResumeAnalyzer(Resource):
#     def post(self):
#         if 'resume' not in request.files:
#             return {"error": "No file uploaded"}, 400

#         resume_file = request.files['resume']

#         if resume_file.filename == '':
#             return {"error": "No selected file"}, 400

#         try:
#             # Read file bytes
#             pdf_bytes = resume_file.read()

#             # Convert bytes to a file-like object
#             pdf_file = io.BytesIO(pdf_bytes)

#             # Extract text from PDF
#             raw_text = pdfminer.high_level.extract_text(pdf_file)

#             # Clean up extracted text
#             cleaned_text = clean_text(raw_text)

#             return {"analysis": cleaned_text}, 200

#         except Exception as e:
#             return {"error": str(e)}, 500

# # Register the API route
# api.add_resource(ResumeAnalyzer, "/analyze")

# if __name__ == "__main__":
#     app.run(debug=True)

import os
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pdfminer.high_level
import io
import re
import openai
from datetime import datetime

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
api = Api(app)
CORS(app)

# Database configuration: use DATABASE_URL environment variable or default
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    "DATABASE_URL",
    "postgresql://resume_db_i579_user:PDSwyFigILkmrFlvIpqfkatYtbrWjwta@dpg-cvi0rc2n91rc73ajoe0g-a.oregon-postgres.render.com/resume_db_i579"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the ResumeAnalysis model
class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256))
    resume_text = db.Column(db.Text)
    analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "resume_text": self.resume_text,
            "analysis": self.analysis,
            "created_at": self.created_at.isoformat()
        }

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

def clean_text(text):
    """Cleans extracted text by removing extra spaces and fixing line breaks."""
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    return text.strip()

class ResumeAnalyzerResource(Resource):
    def post(self):
        if 'resume' not in request.files:
            return {"error": "No file uploaded"}, 400

        resume_file = request.files['resume']
        if resume_file.filename == '':
            return {"error": "No selected file"}, 400

        try:
            # Read file bytes and convert to file-like object
            pdf_bytes = resume_file.read()
            pdf_file = io.BytesIO(pdf_bytes)

            # Extract and clean text from the PDF
            raw_text = pdfminer.high_level.extract_text(pdf_file)
            cleaned_text = clean_text(raw_text)

            # Prepare GPT-4 prompt for detailed analysis
            prompt = (
                "Please analyze the following resume and provide detailed feedback. "
                "Identify its strengths and weaknesses, highlight missing sections (such as education, skills, and experience), "
                "and suggest improvements where necessary.\n\n"
                f"Resume Text:\n{cleaned_text}"
            )

            # Call GPT-4 via the OpenAI API using the new interface
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional career advisor with expertise in resume evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            gpt_analysis = response["choices"][0]["message"]["content"].strip()

            # Save the resume and its analysis to the database
            new_record = ResumeAnalysis(
                filename=resume_file.filename,
                resume_text=cleaned_text,
                analysis=gpt_analysis
            )
            db.session.add(new_record)
            db.session.commit()

            return {"analysis": gpt_analysis, "id": new_record.id}, 200

        except Exception as e:
            return {"error": str(e)}, 500

class ResumeHistory(Resource):
    def get(self):
        # Retrieve all stored resume analyses, ordered by creation date (most recent first)
        records = ResumeAnalysis.query.order_by(ResumeAnalysis.created_at.desc()).all()
        return {"history": [record.as_dict() for record in records]}, 200

# Register API endpoints
api.add_resource(ResumeAnalyzerResource, "/analyze")
api.add_resource(ResumeHistory, "/history")

if __name__ == "__main__":
    app.run(debug=True)
