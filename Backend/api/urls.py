from django.urls import path
from . import views

urlpatterns = [
    path('match/', views.match),
    path('supabase/select/', views.supabase_select),
    path('supabase/insert/', views.supabase_insert),
    path('supabase/update/', views.supabase_update),
    path('supabase/delete/', views.supabase_delete),
    path('offers/scan-save/', views.scan_and_save_offers),
]
