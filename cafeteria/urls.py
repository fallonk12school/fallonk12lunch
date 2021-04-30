from django.urls import include, path

from cafeteria import views
from transactions.views import HomeroomOrdersArchiveView, UsersTodayArchiveView, UsersTransactionsArchiveView

urlpatterns = [
     # Student/Staff pages
    path('', views.home, name='home'),
    path('delete-order/', views.delete_order, name='delete'),
    path('homeroom-orders/', HomeroomOrdersArchiveView.as_view(), name='homeroom-orders'),
    path('submit-order/', views.submit_order, name='submit'),
    path('todays-order/', UsersTodayArchiveView.as_view(), name='todays-order'),
    path('transactions/', UsersTransactionsArchiveView.as_view(),name='user-transactions'),

    # Guardian specific pages
    path('guardian/', views.guardian_home, name='guardian'),
    path('guardian-submit-order/', views.guardian_submit_order, name='guardian-submit'),

     # Admin dashboard pages
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/homeroom-orders-report/', views.homeroom_orders_report, name='homerooms-report'),
    path('admin/profiles/', include('profiles.urls')),
    path('admin/settings/', views.admin_settings, name='settings'),
    path('admin/transactions/', include('transactions.urls')),
]
