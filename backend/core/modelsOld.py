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

    # 🔹 Nouveau champ SaaS
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


# =====================================================
# USER MANAGER
# =====================================================

# =====================================================
# USER MANAGER
# =====================================================
class UserManager(BaseUserManager):

    def create_user(self, email, name, pharmacy=None, pin=None, role="admin", is_saas_admin=False):
        if not email:
            raise ValueError("Users must have an email")

        email = self.normalize_email(email)

        # 🔹 Si pas SaaS admin → pharmacie obligatoire
        if not is_saas_admin and not pharmacy:
            raise ValueError("User must belong to a pharmacy")

        user = self.model(
            email=email,
            name=name,
            pharmacy=pharmacy,
            role=role,
            is_saas_admin=is_saas_admin
        )

        if pin:
            user.set_pin(pin)

        user.save(using=self._db)
        return user


    def create_superuser(self, email, name, password):
        user = self.create_user(
            email=email,
            name=name,
            pharmacy=None,
            pin=password,
            is_saas_admin=True
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# =====================================================
# CUSTOM USER
# =====================================================

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

    # 🔹 SaaS Admin support
    email = models.EmailField(unique=True, null=True, blank=True)
    is_saas_admin = models.BooleanField(default=False)

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="admin")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def set_pin(self, raw_pin):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_pin)

    def check_pin(self, raw_pin):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_pin, self.password)

    def __str__(self):
        if self.is_saas_admin:
            return f"{self.name} (SaaS Admin)"
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
    min_stock_level = models.PositiveIntegerField(default=10)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} {self.dosage}"


# =====================================================
# PRODUCT BATCH (LOT) – AVEC COÛT
# =====================================================
class ProductBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")

    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)  # ✅ coût par lot

    expiry_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["expiry_date", "created_at"]

    def __str__(self):
        return f"{self.product.name} | {self.quantity} | exp {self.expiry_date}"


# =====================================================
# SALE (VENTE)
# =====================================================
class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    cost_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # ✅ COGS réel

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Sale {self.id}"


# =====================================================
# FIFO CONSUMPTION TRACKING
# =====================================================
class SaleBatchConsumption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="batch_consumptions")
    batch = models.ForeignKey(ProductBatch, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


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
# STOCK ENTRY
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

    def __str__(self):
        return f"StockEntry {self.id} - {self.status}"


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
