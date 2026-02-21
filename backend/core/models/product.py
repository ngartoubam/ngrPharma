import uuid
from django.db import models
from django.utils import timezone


class Product(models.Model):

    FORM_CHOICES = (
        ("comprime", "Comprimé"),
        ("gelule", "Gélule"),
        ("sirop", "Sirop"),
        ("injectable", "Injectable"),
        ("pommade", "Pommade"),
        ("suspension", "Suspension"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(
        "Pharmacy",
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=150)
    generic_name = models.CharField(max_length=150, blank=True, null=True)
    dosage = models.CharField(max_length=50)
    form = models.CharField(max_length=50, choices=FORM_CHOICES)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_stock_level = models.PositiveIntegerField(default=10)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} {self.dosage}"