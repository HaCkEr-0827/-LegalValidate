import docx
from PyPDF2 import PdfReader
from rest_framework import status, permissions, parsers, serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ContractAnalysis
from .serializers import ContractAnalysisSerializer
from .tasks import analyze_contract_ai
from shared.utils import success_response, error_response


class FileUploadSerializer(serializers.Serializer):
    """Swagger uchun fayl yuklash serializer"""
    file = serializers.FileField(required=True, help_text="Yuklanadigan fayl (.pdf, .docx, .txt)")


class ContractUploadView(APIView):
    """Faylni yuklash va AI tahlil jarayonini boshlash"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @swagger_auto_schema(
        operation_description="PDF, DOCX yoki TXT fayl yuklash, matnni ajratib olish va AI tahlilni boshlash.",
        request_body=FileUploadSerializer,
        responses={
            200: openapi.Response(description="Fayl yuklandi va AI tahlil boshlandi"),
            400: openapi.Response(description="Fayl yuborilmagan yoki noto‘g‘ri format")
        }
    )
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']

        # Contract yaratish
        contract = ContractAnalysis.objects.create(user=request.user, file=file)

        # Fayldan matn olish
        extracted_text = ""
        try:
            filename = file.name.lower()
            if filename.endswith(".pdf"):
                reader = PdfReader(file)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
            elif filename.endswith(".docx"):
                doc = docx.Document(file)
                extracted_text = "\n".join([p.text for p in doc.paragraphs])
            elif filename.endswith(".txt"):
                extracted_text = file.read().decode('utf-8')
            else:
                return error_response("Unsupported file type", status=400)
        except Exception:
            extracted_text = "Failed to extract text."

        contract.extracted_text = extracted_text
        contract.save()

        # Celery task ishga tushadi
        analyze_contract_ai.delay(contract.id)

        return success_response({
            "contract_id": contract.id,
            "message": "Fayl saqlandi va AI tahlil jarayoniga yuborildi."
        })
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contract_result(request, pk):
    """Muayyan shartnoma tahlil natijasini olish"""
    try:
        contract = ContractAnalysis.objects.get(id=pk, user=request.user)
    except ContractAnalysis.DoesNotExist:
        return error_response("Bunday contract topilmadi.", status=404)

    if contract.analysis_result:
        return success_response({
            "id": contract.id,
            "status": "Tahlil yakunlangan ✅",
            "result": contract.analysis_result,
            "created_at": contract.created_at,
        })

    return success_response({
        "id": contract.id,
        "status": "AI tahlil jarayonida ⏳",
        "result": {
            "summary": "Tahlil hali tugallanmagan.",
            "risks": ["Ba’zi bandlar hali tekshirilmagan."],
            "recommendations": ["Tahlil tugagach, natijani qayta tekshirib chiqing."]
        },
        "created_at": contract.created_at,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_contracts(request):
    """Foydalanuvchining barcha shartnomalari ro‘yxati"""
    contracts = ContractAnalysis.objects.filter(user=request.user).order_by('-created_at')
    serializer = ContractAnalysisSerializer(contracts, many=True)
    return success_response(serializer.data)
