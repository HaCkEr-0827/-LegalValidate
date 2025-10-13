import openai
from celery import shared_task
from django.conf import settings
from .models import ContractAnalysis

openai.api_key = getattr(settings, "OPENAI_API_KEY", None)

@shared_task
def analyze_contract_ai(contract_id):
    """
    Contract matnini AI orqali tahlil qilish.
    Natija ContractAnalysis jadvaliga yoziladi.
    """
    contract = ContractAnalysis.objects.get(id=contract_id)
    text = contract.extracted_text or "No text available."

    try:
        if openai.api_key:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a legal assistant."},
                    {"role": "user", "content": f"Analyze this contract:\n{text}"}
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
            "This is a simulated analysis since OpenAI API is not available.\n\n"
            "**Summary:** Contract appears to be a standard agreement.\n"
            "**Risks:** Confidentiality clause may be missing.\n"
            "**Recommendations:** Add termination terms and review legal compliance."
        )

    contract.analysis_result = ai_text
    contract.save(update_fields=["analysis_result"])
    return ai_text
