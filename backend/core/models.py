import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# -------------------------
# PHARMACY
# -------------------------
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


# -------------------------
# USER MANAGER
# -------------------------
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


# -------------------------
# CUSTOM USER
# -------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("gerant", "Gérant"),
        ("vendeur", "Vendeur"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="users"
    )
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


# -------------------------
# Produits
# -------------------------

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
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="products"
    )

    # Identification pharmaceutique
    name = models.CharField(max_length=150)                 # Nom commercial
    generic_name = models.CharField(max_length=150, null=True, blank=True)  # DCI
    dosage = models.CharField(max_length=50)                # ex: 500 mg
    form = models.CharField(max_length=50, choices=FORM_CHOICES)

    # Vente & logistique
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    min_stock_level = models.PositiveIntegerField(default=10)

    # Réglementaire
    manufacturer = models.CharField(max_length=150, null=True, blank=True)
    requires_prescription = models.BooleanField(default=False)

    # État
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} {self.dosage}"

# -------------------------
# ProductBatch (LOT)
# -------------------------

class ProductBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="batches"
    )
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["expiry_date", "created_at"]  # FIFO réel

    def __str__(self):
        return f"{self.product.name} | {self.quantity} | exp {self.expiry_date}"



# -------------------------
# Sale (Vente)
# -------------------------


class Sale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(default=timezone.now)
