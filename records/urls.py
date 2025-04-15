from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.student_profiles, name='student_profiles'),
    path('academic-results/', views.academic_results, name='academic_results'),
    path('student/<str:student_id>/', views.student_report, name='student_report'),
    path('promotions/', views.manage_promotions, name='manage_promotions'),
]