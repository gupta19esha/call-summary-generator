from django.urls import path
from .views import GenerateSummaryView, SimpleUploadTestView

urlpatterns = [
    path('generate-summary/', GenerateSummaryView.as_view(), name='generate_summary'),
    path('test-upload/', SimpleUploadTestView.as_view(), name='test_upload'),
]