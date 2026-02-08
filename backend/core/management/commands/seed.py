import random
import uuid
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    Pharmacy,
    CustomUser,
    Product,
    ProductBatch,
)

# -------------------------
# DATA DE TEST
# -------------------------

PRODUCT_CATALOG = [
    ("Paracétamol", "Paracetamol", "500 mg", "comprime"),
    ("Ibuprofène", "Ibuprofen", "400 mg", "comprime"),
    ("Amoxicilline", "Amoxicillin", "500 mg", "gelule"),
    ("Vitamine C", "Ascorbic Acid", "1000 mg", "comprime"),
    ("Aspirine", "Acetylsalicylic Acid", "500 mg", "comprime"),
    ("Diclofénac", "Diclofenac", "50 mg", "comprime"),
    ("Metformine", "Metformin", "850 mg", "comprime"),
    ("Ciprofloxacine", "Ciprofloxacin", "500 mg", "comprime"),
    ("Sirop toux", None, "125 ml", "sirop"),
    ("Pommade antibiotique", None, "15 g", "pommade"),
]

MANUFACTURERS = [
    "Sanofi",
    "Pfizer",
    "Novartis",
    "Bayer",
    "Roche",
    "GSK",
]

PHARMACIES = [
    ("Pharmacie Centrale", "pharmacie"),
    ("Pharmacie du Marché", "pharmacie"),
    ("Pharmacie Espoir", "pharmacie"),
]

# -------------------------
# COMMAND
# -------------------------

class Command(BaseCommand):
    help = "Seed database with pharmacies, admins, products and batches"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding database...\n")

        for pharmacy_name, pharmacy_type in PHARMACIES:
            pharmacy = Pharmacy.objects.create(
                id=uuid.uuid4(),
                name=pharmacy_name,
                type=pharmacy_type,
                city="N'Djamena",
            )

            self.stdout.write(f"🏪 Pharmacy created: {pharmacy.name}")

            # -------------------------
            # ADMIN
            # -------------------------
            admin = CustomUser.objects.create_user(
                name=f"Admin {pharmacy.name}",
                pharmacy=pharmacy,
                role="admin",
                pin="1234",
            )

            self.stdout.write(f"👤 Admin created: {admin.name}")

            # -------------------------
            # PRODUITS
            # -------------------------
            for i in range(100):
                base_product = random.choice(PRODUCT_CATALOG)

                product = Product.objects.create(
                    id=uuid.uuid4(),
                    pharmacy=pharmacy,
                    name=base_product[0],
                    generic_name=base_product[1],
                    dosage=base_product[2],
                    form=base_product[3],
                    unit_price=random.randint(500, 5000),
                    purchase_price=random.randint(300, 4000),
                    min_stock_level=random.randint(5, 20),
                    manufacturer=random.choice(MANUFACTURERS),
                    requires_prescription=random.choice([True, False]),
                    is_active=True,
                )

                # -------------------------
                # LOTS (1 à 3 par produit)
                # -------------------------
                for _ in range(random.randint(1, 3)):
                    ProductBatch.objects.create(
                        id=uuid.uuid4(),
                        product=product,
                        quantity=random.randint(20, 150),
                        expiry_date=date.today()
                        + timedelta(days=random.randint(90, 720)),
                    )

            self.stdout.write(
                f"💊 100 produits + lots créés pour {pharmacy.name}\n"
            )

        self.stdout.write(
            self.style.SUCCESS("✅ Seeding terminé avec succès 🎉")
        )
