import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


class UserManager(BaseUserManager):

    def create_user(self, email, name, pharmacy=None, pin=None, role="admin", is_saas_admin=False):
        if not email:
            raise ValueError("Users must have an email")

        email = self.normalize_email(email)

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


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("gerant", "Gérant"),
        ("vendeur", "Vendeur"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True, null=True, blank=True)
    is_saas_admin = models.BooleanField(default=False)

    pharmacy = models.ForeignKey(
        "Pharmacy",
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
        self.password = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.password)

    def __str__(self):
        if self.is_saas_admin:
            return f"{self.name} (SaaS Admin)"
        return f"{self.name} ({self.role})"