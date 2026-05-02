from django.urls import path
from accounts import views as auth_views
from operations import views as ops_views
from main import views as main_views

urlpatterns = [
    path('auth/login', auth_views.login_view),
    path('auth/logout', auth_views.logout_view),
    path('auth/me', auth_views.me_view),

    path('villages', ops_views.village_list),
    path('villages/<int:pk>', ops_views.village_detail),
    path('villages/<int:pk>/units', ops_views.village_units),

    path('units', ops_views.unit_list),
    path('units/<int:pk>', ops_views.unit_detail),

    path('production', main_views.production_list),
    path('production/<int:pk>', main_views.production_detail),

    path('inventory', main_views.inventory_list),
    path('inventory/stock-in', main_views.stock_in),
    path('inventory/stock-out', main_views.stock_out),
    path('inventory/<int:pk>', main_views.inventory_detail),
    path('inventory/<int:pk>/history', main_views.stock_history),

    path('trainings', main_views.training_list),
    path('trainings/enroll', main_views.enroll_trainee),
    path('trainings/<int:pk>', main_views.training_detail),

    path('trainees', main_views.trainee_list),
    path('trainees/<int:pk>', main_views.trainee_detail),

    path('dashboard/summary', main_views.dashboard_summary),
    path('dashboard/charts', main_views.dashboard_charts),
]
