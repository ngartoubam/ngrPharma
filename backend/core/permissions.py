from rest_framework.permissions import BasePermission, SAFE_METHODS


# =========================================================
# ADMIN / GERANT (PHARMACY LEVEL)
# =========================================================
class IsAdminOrGerant(BasePermission):
    """
    Autorise uniquement les utilisateurs avec le rôle :
    - admin
    - gerant
    (niveau pharmacie)
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_saas_admin", False) is False
            and user.role in ("admin", "gerant")
        )


# =========================================================
# ADMIN ONLY (PHARMACY LEVEL)
# =========================================================
class IsAdminOnly(BasePermission):
    """
    Autorise uniquement les administrateurs de pharmacie
    (pas SaaS Admin)
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_saas_admin", False) is False
            and user.role == "admin"
        )


# =========================================================
# READ FOR ALL AUTHENTICATED / WRITE FOR ADMIN OR GERANT
# =========================================================
class ReadOnlyOrAdminOrGerant(BasePermission):
    """
    Lecture pour tous les utilisateurs authentifiés,
    écriture réservée aux admin / gérant (niveau pharmacie)
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Lecture autorisée à tous les users pharmacie
        if request.method in SAFE_METHODS:
            return not getattr(user, "is_saas_admin", False)

        # Écriture réservée aux admin / gérant pharmacie
        return (
            getattr(user, "is_saas_admin", False) is False
            and user.role in ("admin", "gerant")
        )


# =========================================================
# SaaS ADMIN (GLOBAL PLATFORM LEVEL)
# =========================================================
class IsSaaSAdmin(BasePermission):
    """
    Autorise uniquement les comptes SaaS Admin
    (niveau plateforme globale)
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_saas_admin", False) is True
        )
