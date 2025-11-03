import os
import docx # type: ignore
from PyPDF2 import PdfReader # type: ignore
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from drf_yasg.utils import swagger_auto_schema # type: ignore
from drf_yasg import openapi# type: ignore
from rest_framework import serializers
from .models import ContractAnalysis
from .tasks import analyze_contract_ai
from rest_framework import generics
from .serializers import ContractAnalysisSerializer
from .models import ContractAnalysis
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated 


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, help_text="Yuklanadigan fayl (.pdf, .docx, .txt)")

class ContractUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser] 

    @swagger_auto_schema(
        operation_description="PDF, DOCX yoki TXT fayl yuklash, matnni ajratib olish va AI bilan tahlil qilish.",
        request_body=FileUploadSerializer,
        responses={
            200: openapi.Response(description="Fayl saqlandi va AI tahlil boshlandi"),
            400: openapi.Response(description="Fayl yuborilmagan yoki noto‘g‘ri format")
        }
    )
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']

        contract = ContractAnalysis.objects.create(user=request.user, file=file)

        text = ""
        filename = file.name.lower()
        if filename.endswith(".pdf"):
            try:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception:
                text = "Failed to extract text from PDF."
        elif filename.endswith(".docx"):
            try:
                doc = docx.Document(file)
                text = "\n".join([p.text for p in doc.paragraphs])
            except Exception:
                text = "Failed to extract text from DOCX."
        elif filename.endswith(".txt"):
            try:
                text = file.read().decode('utf-8')
            except Exception:
                text = "Failed to read TXT file."
        else:
            return Response({"detail": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

        contract.extracted_text = text
        contract.save()
        analyze_contract_ai.delay(contract.id)

        return Response({
                "detail": "Fayl saqlandi va AI tahlil boshlandi.",
                "contract_id": contract.id
            }, status=status.HTTP_200_OK)

    
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contract_result(request, pk):
    try:
        contract = ContractAnalysis.objects.get(id=pk, user=request.user)
    except ContractAnalysis.DoesNotExist:
        return Response({"error": "Bunday contract topilmadi."}, status=404)

    if contract.analysis_result:
        return Response({
            "id": contract.id,
            "status": "Tahlil yakunlangan ",
            "result": contract.analysis_result,
            "created_at": contract.created_at,
        })

    default_result = {
        "summary": "AI tahlil hali tugallanmagan. Hozircha shartnoma umumiy ko‘rinishda to‘g‘ri tuzilgan.",
        "risks": ["Hujjatda ayrim bandlar hali tekshirilmagan."],
        "recommendations": ["Tahlil tugagach, natijani qayta tekshirib chiqing."]
    }

    return Response({
        "id": contract.id,
        "status": "AI tahlil jarayonida ⏳",
        "result": default_result,
        "created_at": contract.created_at,
    })
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_contracts(request):
   
    contracts = ContractAnalysis.objects.filter(user=request.user).order_by('-created_at')
    serializer = ContractAnalysisSerializer(contracts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

