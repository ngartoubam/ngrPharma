import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# =====================================================
# PHARMACY
# =====================================================
class Pharmacy(models.Model):
    PHARMACY_TYPES = (
        ("pharmacie", "Pharmacie"),
        ("depot", "Dépôt"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=PHARMACY_TYPES)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# =====================================================
# USER MANAGER
# =====================================================
class UserManager(BaseUserManager):
    def create_user(self, name, pharmacy, pin, role="vendeur"):
        if not name:
            raise ValueError("User must have a name")
        if not pharmacy:
            raise ValueError("User must belong to a pharmacy")

        user = self.model(
            id=uuid.uuid4(),
            name=name,
            pharmacy=pharmacy,
            role=role,
            is_active=True,
        )
        user.set_pin(pin)
        user.save(using=self._db)
        return user


# =====================================================
# CUSTOM USER
# =====================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("gerant", "Gérant"),
        ("vendeur", "Vendeur"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="users")

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ["name"]

    def set_pin(self, raw_pin):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_pin)

    def check_pin(self, raw_pin):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_pin, self.password)

    def __str__(self):
        return f"{self.name} ({self.role})"


# =====================================================
# PRODUCT
# =====================================================
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
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="products")

    name = models.CharField(max_length=150)
    generic_name = models.CharField(max_length=150, blank=True, null=True)
    dosage = models.CharField(max_length=50)
    form = models.CharField(max_length=50, choices=FORM_CHOICES)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    min_stock_level = models.PositiveIntegerField(default=10)

    manufacturer = models.CharField(max_length=150, blank=True, null=True)
    requires_prescription = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} {self.dosage}"


# =====================================================
# PRODUCT BATCH (LOT)
# =====================================================
class ProductBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")

    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["expiry_date", "created_at"]

    def __str__(self):
        return f"{self.product.name} | {self.quantity} | exp {self.expiry_date}"


# =====================================================
# SALE
# =====================================================
class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(default=timezone.now)


# =====================================================
# SALE AUDIT LOG
# =====================================================
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

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="sale_audit_logs")
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    requested_quantity = models.PositiveIntegerField()

    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


# =====================================================
# SUPPLIER
# =====================================================
class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="suppliers")

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# =====================================================
# STOCK ENTRY (BON D’ENTRÉE)
# =====================================================
class StockEntry(models.Model):
    STATUS_CHOICES = (
        ("draft", "Brouillon"),
        ("validated", "Validé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name="stock_entries")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name="stock_entries")

    invoice_number = models.CharField(max_length=100, blank=True, null=True)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


# =====================================================
# STOCK ENTRY ITEM
# =====================================================
class StockEntryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()

    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.purchase_price
        super().save(*args, **kwargs)


# =====================================================
# STOCK ENTRY AUDIT
# =====================================================
class StockEntryAudit(models.Model):
    ACTION_CHOICES = (
        ("CREATED", "Créée"),
        ("VALIDATED", "Validée"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE)

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    message = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

# -------------------------
# STOCK ENTRY AUDIT LOG
# -------------------------
class StockEntryAuditLog(models.Model):
    ACTION_CHOICES = (
        ("CREATED", "Entrée créée"),
        ("VALIDATED", "Entrée validée"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="stock_entry_audits"
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    stock_entry = models.ForeignKey(
        StockEntry,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} | {self.created_at:%Y-%m-%d %H:%M}"
