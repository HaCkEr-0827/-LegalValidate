from rest_framework import serializers
from .models import ContractAnalysis
from PyPDF2 import PdfReader # type: ignore
import docx # type: ignore

class ContractAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAnalysis
        fields = ['id', 'file', 'extracted_text', 'created_at']
        read_only_fields = ['extracted_text', 'created_at']

    def create(self, validated_data):
        file = validated_data.get('file')
        extracted_text = ""

        if file.name.endswith('.pdf'):
            try:
                reader = PdfReader(file)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
            except Exception:
                extracted_text = "Failed to extract text from PDF."

        elif file.name.endswith('.docx'):
            try:
                doc = docx.Document(file)
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"
            except Exception:
                extracted_text = "Failed to extract text from DOCX."

        elif file.name.endswith('.txt'):
            try:
                extracted_text = file.read().decode('utf-8')
            except Exception:
                extracted_text = "Failed to read TXT file."

        else:
            extracted_text = "Unsupported file type."

        validated_data['extracted_text'] = extracted_text
        return super().create(validated_data)
