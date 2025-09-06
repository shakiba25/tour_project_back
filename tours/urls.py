from django.urls import path
from .views import ChatListCreateAPIView, ChatDetailAPIView, ChatMessageAPIView

urlpatterns = [
    path("chat/", ChatListCreateAPIView.as_view(), name="chat-list-create"),
    path("chat/<int:chat_id>/", ChatDetailAPIView.as_view(), name="chat-detail"),
    path("chat/<int:chat_id>/messages/", ChatMessageAPIView.as_view(), name="chat-message"),
]
