import uuid
from django.db import models
from django.utils import timezone


class Pharmacy(models.Model):

    PHARMACY_TYPES = (
        ("pharmacie", "Pharmacie"),
        ("depot", "Dépôt"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )

    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=PHARMACY_TYPES)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        import random
        return f"PH{random.randint(1000,9999)}"

    def __str__(self):
        return f"{self.name} ({self.code})"