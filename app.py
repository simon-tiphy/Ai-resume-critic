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

# api.add_resource(ResumeAnalyzer, "/analyze")

# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import pdfminer.high_level
import io
import re

app = Flask(__name__)
api = Api(app)
CORS(app)  # Enable CORS for frontend requests

def clean_text(text):
    """Cleans extracted text by removing extra spaces and fixing line breaks."""
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = text.strip()  # Remove leading/trailing spaces
    return text

class ResumeAnalyzer(Resource):
    def post(self):
        if 'resume' not in request.files:
            return {"error": "No file uploaded"}, 400

        resume_file = request.files['resume']

        if resume_file.filename == '':
            return {"error": "No selected file"}, 400

        try:
            # Read file bytes
            pdf_bytes = resume_file.read()

            # Convert bytes to a file-like object
            pdf_file = io.BytesIO(pdf_bytes)

            # Extract text from PDF
            raw_text = pdfminer.high_level.extract_text(pdf_file)

            # Clean up extracted text
            cleaned_text = clean_text(raw_text)

            return {"analysis": cleaned_text}, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

# Register the API route
api.add_resource(ResumeAnalyzer, "/analyze")

if __name__ == "__main__":
    app.run(debug=True)
