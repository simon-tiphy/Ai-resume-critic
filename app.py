from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from transformers import pipeline
import pdfminer.high_level

app = Flask(__name__)
CORS(app)
api = Api(app)  # Use Flask-RESTful API

# Load NLP model
resume_analyzer = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")

class ResumeAnalysis(Resource):
    def post(self):
        if 'resume' not in request.files:
            return {"error": "No resume file uploaded"}, 400

        resume_file = request.files['resume']
        text = pdfminer.high_level.extract_text(resume_file)

        if not text.strip():
            return {"error": "Could not extract text"}, 400

        # Analyze the text with NLP model
        analysis = resume_analyzer(text[:512])  # Limiting input length

        return {"analysis": analysis}, 200

# Add resource to API
api.add_resource(ResumeAnalysis, '/analyze')

if __name__ == '__main__':
    app.run(debug=True)
