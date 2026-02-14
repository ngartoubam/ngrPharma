from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrGerant(BasePermission):
    """
    Autorise uniquement les utilisateurs avec le rôle :
    - admin
    - gerant
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.role in ("admin", "gerant")
        )


class IsAdminOnly(BasePermission):
    """
    Autorise uniquement les administrateurs
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user
            and user.is_authenticated
            and user.role == "admin"
        )


class ReadOnlyOrAdminOrGerant(BasePermission):
    """
    Lecture pour tous les utilisateurs authentifiés,
    écriture réservée aux admin / gérant
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Lecture autorisée à tous
        if request.method in SAFE_METHODS:
            return True

        # Écriture réservée
        return user.role in ("admin", "gerant")
