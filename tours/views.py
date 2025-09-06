from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, MessageSerializer
from tours.utils.chat_logic import generate_assistant_response


# ساخت و لیست چت‌ها
class ChatListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        chat = ChatSession.objects.create(user=user)
        return Response(ChatSessionSerializer(chat).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        chats = ChatSession.objects.all()
        return Response(ChatSessionSerializer(chats, many=True).data, status=status.HTTP_200_OK)


# جزییات یک چت (با ID)
class ChatDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, chat_id):
        chat = ChatSession.objects.filter(id=chat_id).first()
        if not chat:
            return Response({"error": "چت پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ChatSessionSerializer(chat).data, status=status.HTTP_200_OK)


# پیام جدید توی یک چت
# class ChatMessageAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, chat_id):
#         chat = ChatSession.objects.filter(id=chat_id).first()
#         if not chat:
#             return Response({"error": "چت پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)

#         content = request.data.get("content")
#         if not content:
#             return Response({"error": "متن پیام لازم است"}, status=status.HTTP_400_BAD_REQUEST)

#         # پیام کاربر
#         user_msg = ChatMessage.objects.create(session=chat, role="user", content=content)

#         # تاریخچه گفتگو
#         history = list(chat.messages.values("role", "content"))

#         # --- اینجا LLM رو صدا میزنی ---
#         bot_text = f"پیام شما: {content}"  # موقت برای تست
#         bot_msg = ChatMessage.objects.create(session=chat, role="assistant", content=bot_text)

#         return Response({
#             "user_msg": MessageSerializer(user_msg).data,
#             "bot_msg": MessageSerializer(bot_msg).data,
#         }, status=status.HTTP_200_OK)



class ChatMessageAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, chat_id):
        chat = ChatSession.objects.filter(id=chat_id).first()
        if not chat:
            return Response({"error": "چت پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get("content")
        if not content:
            return Response({"error": "متن پیام لازم است"}, status=status.HTTP_400_BAD_REQUEST)

        # پیام کاربر
        user_msg = ChatMessage.objects.create(session=chat, role="user", content=content)

        # پاسخ دستیار
        bot_text = generate_assistant_response(chat, content)
        bot_msg = ChatMessage.objects.create(session=chat, role="assistant", content=bot_text)

        return Response({
            "user_msg": MessageSerializer(user_msg).data,
            "bot_msg": MessageSerializer(bot_msg).data,
        }, status=status.HTTP_200_OK)
        
        
        
        