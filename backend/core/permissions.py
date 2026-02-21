from datetime import date
from rest_framework.permissions import BasePermission, SAFE_METHODS


# =========================================================
# 🔒 SUBSCRIPTION ACTIVE (SAAS PAYWALL)
# =========================================================
class IsSubscriptionActive(BasePermission):
    """
    Bloque l'accès si :
    - pharmacie désactivée
    - abonnement expiré
    - statut Stripe invalide
    """

    message = "Votre abonnement est inactif ou expiré."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # SaaS Admin toujours autorisé
        if getattr(user, "is_saas_admin", False):
            return True

        pharmacy = getattr(user, "pharmacy", None)

        if not pharmacy:
            return False

        # Pharmacie suspendue par admin
        if not pharmacy.is_active:
            return False

        # Stripe status valide
        if pharmacy.subscription_status in ("active", "trialing"):
            # Vérifie date fin Stripe
            if pharmacy.current_period_end and pharmacy.current_period_end.date() < date.today():
                return False
            return True

        # Vérifie grace period interne
        if pharmacy.grace_until and pharmacy.grace_until.date() >= date.today():
            return True

        return False


# =========================================================
# 🏢 ADMIN / GERANT (PHARMACY LEVEL)
# =========================================================
class IsAdminOrGerant(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and not getattr(user, "is_saas_admin", False)
            and user.role in ("admin", "gerant")
        )


# =========================================================
# 🏢 ADMIN ONLY (PHARMACY LEVEL)
# =========================================================
class IsAdminOnly(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and not getattr(user, "is_saas_admin", False)
            and user.role == "admin"
        )


# =========================================================
# 👁 READ FOR ALL / WRITE FOR ADMIN OR GERANT
# =========================================================
class ReadOnlyOrAdminOrGerant(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Lecture autorisée pour tous les users pharmacie
        if request.method in SAFE_METHODS:
            return not getattr(user, "is_saas_admin", False)

        # Écriture réservée admin / gerant
        return (
            not getattr(user, "is_saas_admin", False)
            and user.role in ("admin", "gerant")
        )


# =========================================================
# 🌍 SaaS ADMIN (GLOBAL PLATFORM LEVEL)
# =========================================================
class IsSaaSAdmin(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_saas_admin", False)
        )