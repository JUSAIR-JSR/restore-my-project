from django.urls import path
from .views import job_posting_list, job_posting_detail, job_posting_create, job_posting_update, job_posting_delete, job_application_create, job_application_success, user_job_applications

urlpatterns = [
    path('postings/', job_posting_list, name='job_posting_list'),
    path('postings/create/', job_posting_create, name='job_posting_create'),
    path('postings/update/<int:pk>/', job_posting_update, name='job_posting_update'),
    path('postings/delete/<int:pk>/', job_posting_delete, name='job_posting_delete'),
    path('postings/detail/<int:pk>/', job_posting_detail, name='job_posting_detail'),
    path('postings/apply/<int:pk>/', job_application_create, name='job_application_create'),
    path('application/success/', job_application_success, name='job_application_success'),
    path('applications/', user_job_applications, name='user_job_applications'),
]
