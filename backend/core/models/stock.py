import uuid
from django.db import models
from django.utils import timezone


class ProductBatch(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="batches"
    )

    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    expiry_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["expiry_date", "created_at"]

    def __str__(self):
        return f"{self.product.name} | {self.quantity} | exp {self.expiry_date}"


class StockEntry(models.Model):

    STATUS_CHOICES = (
        ("draft", "Brouillon"),
        ("validated", "Validé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(
        "Pharmacy",
        on_delete=models.CASCADE,
        related_name="stock_entries"
    )

    supplier = models.ForeignKey(
        "Supplier",
        on_delete=models.SET_NULL,
        null=True,
        related_name="stock_entries"
    )

    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


class StockEntryItem(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stock_entry = models.ForeignKey(
        "StockEntry",
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey("Product", on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()

    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.purchase_price
        super().save(*args, **kwargs)