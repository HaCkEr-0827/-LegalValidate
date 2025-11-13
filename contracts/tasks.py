import openai
from celery import shared_task
from django.conf import settings
from .models import ContractAnalysis

openai.api_key = getattr(settings, "OPENAI_API_KEY", None)

@shared_task
def analyze_contract_ai(contract_id):
    """
    Contract matnini AI orqali tahlil qiladi.
    Natija ContractAnalysis jadvaliga yoziladi.
    """
    contract = ContractAnalysis.objects.get(id=contract_id)
    text = contract.extracted_text or "No text available."

    try:
        if openai.api_key:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional legal assistant."},
                    {"role": "user", "content": f"Analyze this contract text:\n{text}"}
                ],
                max_tokens=500
            )
            ai_text = response.choices[0].message.content
        else:
            raise Exception("API key not found")

    except Exception as e:
        print(f"[Mock Mode] AI error: {e}")
        ai_text = (
            "⚠️ [Mock AI Response]\n"
            "This is a simulated AI analysis (no OpenAI key found).\n\n"
            "**Summary:** The contract seems standard.\n"
            "**Risks:** Confidentiality clause missing.\n"
            "**Recommendations:** Add termination and compliance clauses."
        )

    contract.analysis_result = ai_text
    contract.save(update_fields=["analysis_result"])
    return ai_text
