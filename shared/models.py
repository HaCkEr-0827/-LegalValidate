from django.db import models

class BaseModel(models.Model):
    """Barcha modellarga umumiy maydonlar"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Bu model DBda jadval yaratmaydi

