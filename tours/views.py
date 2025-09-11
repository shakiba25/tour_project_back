from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import ChatSession, ChatMessage , Tour
from .serializers import ChatSessionSerializer, MessageSerializer , TourSerializer
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
        
        
        
        
class DestinationListAPIView(APIView):
    def get(self, request):
        destinations = Tour.objects.values("destination", "destination_type").distinct()
        return Response(destinations, status=status.HTTP_200_OK)        
    
    
    

class FilteredTourListAPIView(APIView):
    def get(self, request):
        destination_type = request.GET.get("destination_type")
        destination = request.GET.get("destination")
        departure_date = request.GET.get("departure_date")
        return_date = request.GET.get("return_date")
        nights = request.GET.get("nights")

        tours = Tour.objects.all()

        if destination_type:
            tours = tours.filter(destination_type=destination_type)

        if destination:
            tours = tours.filter(destination__icontains=destination)

        if departure_date:
            tours = tours.filter(departure__date=departure_date)

        if return_date:
            tours = tours.filter(return_info__date=return_date)

        if nights:
            try:
                nights_int = int(nights)
                tours = tours.filter(duration_days=nights_int)
            except ValueError:
                pass  # نادیده بگیر اگه عدد نبود

        serializer = TourSerializer(tours, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)    
    
    
class TourDetailAPIView(APIView):
    def get(self, request, id):
        # print("\n \n {id} \n \n")
        
        # tour = Tour.objects.filter(tour_id='tour_001').first()
        # print(TourSerializer(tour).data)
        # return Response(status=status.HTTP_200_OK) 

        
        
        tour = Tour.objects.filter(tour_id=id).first()
        if not tour:
            return Response({"error": "تور پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TourSerializer(tour)
        return Response(serializer.data, status=status.HTTP_200_OK)  