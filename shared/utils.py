from rest_framework.response import Response
import docx
from PyPDF2 import PdfReader

def success_response(data=None, message="Success", status=200):
    """Muvaffaqiyatli javob"""
    return Response({
        "status": "success",
        "message": message,
        "data": data
    }, status=status)


def error_response(message="Error", errors=None, status=400):
    """Xato holat uchun javob"""
    return Response({
        "status": "error",
        "message": message,
        "errors": errors
    }, status=status)

def generate_otp_code():
    """6 xonali OTP kodini generatsiya qilish"""
    import random
    return f"{random.randint(0, 999999):06d}"

def extract_text_from_file(file):
    """PDF, DOCX yoki TXT fayldan matnni ajratib olish"""
    filename = file.name.lower()
    text = ""

    try:
        if filename.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif filename.endswith(".docx"):
            doc = docx.Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith(".txt"):
            text = file.read().decode('utf-8')
        else:
            return None, "Unsupported file type"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

    return text, None