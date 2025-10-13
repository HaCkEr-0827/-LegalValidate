from django.db import models
from django.conf import settings

class ContractAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="contracts"
    )
    file = models.FileField(upload_to="contracts/")
    analysis_result = models.TextField(blank=True, null=True)
    extracted_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract by {self.user.email or self.user.phone_number}"

