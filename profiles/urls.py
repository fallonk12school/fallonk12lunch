from django.urls import include, path

from profiles import views

urlpatterns = [
    path('', views.ProfileListView.as_view(), name='profile-list'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/make-inactive', views.make_inactive, name='profile-make-inactive'),
    path('<int:pk>/new-card', views.new_individual_card, name='profile-new-card'),
    path('debtors/', views.ProfileListView.as_view(filter='debt'),
         name='profile-debt-list'),
    path('pending-inactive/', views.pending_inactive_students, name='pending-inactive'),
    path('search/', views.ProfileSearchResultsView.as_view(filter='search'), name='profile-search'),
]
