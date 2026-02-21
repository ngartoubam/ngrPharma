from django.db import models

class SaaSPlan(models.Model):
    name = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="usd")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name