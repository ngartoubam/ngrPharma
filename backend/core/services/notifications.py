from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now, timedelta

from core.models import (
    SaleAuditLog,
    Product,
    ProductBatch,
    CustomUser,
)


# ======================================================
# UTILITAIRES
# ======================================================

def get_admin_users(pharmacy):
    """
    Retourne les admins + gérants d’une pharmacie
    """
    return CustomUser.objects.filter(
        pharmacy=pharmacy,
        role__in=["admin", "gerant"],
        is_active=True,
    )


def send_email_to_admins(pharmacy, subject, message):
    """
    Envoie un email aux admins/gérants
    """
    admins = get_admin_users(pharmacy)
    recipients = [u.email for u in admins if u.email]

    if not recipients:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )


# ======================================================
# 🚫 VENTE BLOQUÉE
# ======================================================

def notify_blocked_sale(audit_log: SaleAuditLog):
    """
    Notification après une vente bloquée
    """
    pharmacy = audit_log.pharmacy

    subject = "🚫 Vente bloquée – ngrPharma"
    message = f"""
Une vente a été BLOQUÉE.

Pharmacie : {pharmacy.name}
Produit   : {audit_log.product}
Quantité  : {audit_log.requested_quantity}
Raison    : {audit_log.reason}

Message :
{audit_log.message}

Date : {audit_log.created_at.strftime('%Y-%m-%d %H:%M')}
"""

    send_email_to_admins(pharmacy, subject, message)


# ======================================================
# ⏰ PRODUITS EXPIRÉS
# ======================================================

def notify_expired_products(pharmacy):
    """
    Alerte produits expirés encore en stock
    """
    today = now().date()

    expired_batches = ProductBatch.objects.filter(
        product__pharmacy=pharmacy,
        expiry_date__lt=today,
        quantity__gt=0,
    ).select_related("product")

    if not expired_batches.exists():
        return

    lines = []
    for batch in expired_batches:
        lines.append(
            f"- {batch.product.name} ({batch.quantity} unités) expiré le {batch.expiry_date}"
        )

    subject = "⛔ Produits expirés détectés"
    message = f"""
Les produits suivants sont EXPIRES et encore en stock :

{chr(10).join(lines)}

Merci d’agir immédiatement (retrait / destruction).
"""

    send_email_to_admins(pharmacy, subject, message)


# ======================================================
# ⏳ PRODUITS PROCHES D’EXPIRATION
# ======================================================

def notify_expiring_soon_products(pharmacy, days=30):
    """
    Alerte produits expirant bientôt
    """
    today = now().date()
    limit_date = today + timedelta(days=days)

    batches = ProductBatch.objects.filter(
        product__pharmacy=pharmacy,
        expiry_date__range=(today, limit_date),
        quantity__gt=0,
    ).select_related("product")

    if not batches.exists():
        return

    lines = []
    for batch in batches:
        remaining_days = (batch.expiry_date - today).days
        lines.append(
            f"- {batch.product.name} ({batch.quantity}) – expire dans {remaining_days} jours"
        )

    subject = "⚠️ Produits proches d’expiration"
    message = f"""
Attention ⚠️

Les produits suivants expirent dans moins de {days} jours :

{chr(10).join(lines)}

Conseils :
• Prioriser la vente
• Éviter le surstock
• Informer l’équipe
"""

    send_email_to_admins(pharmacy, subject, message)


# ======================================================
# 📉 STOCK CRITIQUE
# ======================================================

def notify_low_stock(pharmacy):
    """
    Alerte stock critique
    """
    products = (
        Product.objects
        .filter(pharmacy=pharmacy, is_active=True)
        .annotate(stock=models.Sum("batches__quantity"))
    )

    low_stock = [
        p for p in products
        if (p.stock or 0) <= p.min_stock_level
    ]

    if not low_stock:
        return

    lines = []
    for p in low_stock:
        lines.append(
            f"- {p.name} : stock {p.stock or 0} (seuil {p.min_stock_level})"
        )

    subject = "📉 Stock critique détecté"
    message = f"""
Les produits suivants sont en STOCK CRITIQUE :

{chr(10).join(lines)}

Action recommandée :
• Réapprovisionnement
• Ajustement des seuils
"""

    send_email_to_admins(pharmacy, subject, message)
