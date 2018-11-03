from django.urls import path

from analytics_minimal.views import Collect, Sandbox

urlpatterns = [
    path('v1/collect', Collect.as_view()),
    path('sandbox/v1/collect', Sandbox.as_view()),
]
