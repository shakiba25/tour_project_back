from django.urls import path
from .views import ChatListCreateAPIView, ChatDetailAPIView, ChatMessageAPIView, DestinationListAPIView , FilteredTourListAPIView ,TourDetailAPIView

urlpatterns = [
    path("chat/", ChatListCreateAPIView.as_view(), name="chat-list-create"),
    path("chat/<int:chat_id>/", ChatDetailAPIView.as_view(), name="chat-detail"),
    path("chat/<int:chat_id>/messages/", ChatMessageAPIView.as_view(), name="chat-message"),
    
    path('destinations/', DestinationListAPIView.as_view(), name='destination-list'),
    path('tours/', FilteredTourListAPIView.as_view(), name='filtered-tours'),
    path('tours/<str:id>/', TourDetailAPIView.as_view(), name='tour-detail'),

]
