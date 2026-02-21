import uuid
from django.db import models
from django.utils import timezone


class Sale(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey("Pharmacy", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    cost_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Sale {self.id}"


class SaleBatchConsumption(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sale = models.ForeignKey(
        "Sale",
        on_delete=models.CASCADE,
        related_name="batch_consumptions"
    )

    batch = models.ForeignKey("ProductBatch", on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class SaleAuditLog(models.Model):

    ACTION_CHOICES = (
        ("SUCCESS", "Vente réussie"),
        ("BLOCKED", "Vente bloquée"),
    )

    REASON_CHOICES = (
        ("expired_stock", "Stock expiré"),
        ("insufficient_stock", "Stock insuffisant"),
        ("unauthorized_product", "Produit non autorisé"),
        ("inactive_product", "Produit inactif"),
        ("other", "Autre"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(
        "Pharmacy",
        on_delete=models.CASCADE,
        related_name="sale_audit_logs"
    )

    user = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    requested_quantity = models.PositiveIntegerField()

    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]