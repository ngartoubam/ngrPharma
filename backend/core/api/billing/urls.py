from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CreateBillingPortalView,
    MeSubscriptionView,
)

urlpatterns = [
    path("checkout/", CreateCheckoutSessionView.as_view()),
    path("portal/", CreateBillingPortalView.as_view()),
    path("me/", MeSubscriptionView.as_view()),
]