from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_connection, name='test_connection'),
    path('upload-zip/', views.handle_zip_upload, name='upload_zip'),
    path('fetch-mapper/', views.fetch_mapper_json, name='fetch_mapper'),
    path('upload-mid/', views.handle_mid_upload, name='upload_mid'),
    path('upload-img/', views.handle_cover_upload, name='upload_img'),
    path('upload-json/', views.handle_json_upload, name='upload_json'),
    path('audio-search-result/', views.audio_search_result, name='audio_search_result'),
    path('download-audio-file/<str:filename>/', views.download_audio_file, name='download_audio_file'),
    path('cover-search-result/', views.cover_search_result, name='cover_search_result'),
    path('download-cover-file/<str:filename>/', views.download_cover_file, name='download_cover_file')
]
