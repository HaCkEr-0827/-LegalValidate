from rest_framework import serializers
from .models import ContractAnalysis
from PyPDF2 import PdfReader
import docx

class ContractAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractAnalysis
        fields = ['id', 'file', 'extracted_text', 'analysis_result', 'created_at']
        read_only_fields = ['extracted_text', 'analysis_result', 'created_at']

    def create(self, validated_data):
        """Fayldan matn ajratib olish"""
        file = validated_data.get('file')
        extracted_text = ""

        try:
            if file.name.endswith('.pdf'):
                reader = PdfReader(file)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""

            elif file.name.endswith('.docx'):
                doc = docx.Document(file)
                extracted_text = "\n".join([p.text for p in doc.paragraphs])

            elif file.name.endswith('.txt'):
                extracted_text = file.read().decode('utf-8')

            else:
                extracted_text = "Unsupported file type."
        except Exception:
            extracted_text = "Failed to extract text from file."

        validated_data['extracted_text'] = extracted_text
        return super().create(validated_data)
