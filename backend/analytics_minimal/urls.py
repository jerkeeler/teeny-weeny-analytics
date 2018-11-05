from django.urls import path

from analytics_minimal.views import V1Collect, Sandbox

urlpatterns = [
    path('v1/collect', V1Collect.as_view()),
    path('sandbox/v1/collect', Sandbox.as_view()),
]
