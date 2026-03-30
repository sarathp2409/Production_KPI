from django.urls import path
from . import views

app_name = 'pagination_dash'

urlpatterns = [
    # Home page - Plant selection
    path('', views.PlantSelectionView.as_view(), name='pagination_home'),

    # Plant-specific URLs
    path('<str:plant_id>/create/', views.PaginationCreateView.as_view(), name='pagination_create'),
    path('<str:plant_id>/list/', views.PaginationListView.as_view(), name='pagination_list'),
    path('<str:plant_id>/view/<int:pk>/', views.PaginationDetailView.as_view(), name='pagination_detail'),
    path('<str:plant_id>/edit/<int:pk>/', views.PaginationUpdateView.as_view(), name='pagination_update'),
    path('<str:plant_id>/delete/<int:pk>/', views.PaginationDeleteView.as_view(), name='pagination_delete'),
]
