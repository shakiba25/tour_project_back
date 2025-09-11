from rest_framework import serializers
from .models import ChatSession, ChatMessage , Tour, FlightInfo, Hotel, Service, ItineraryItem, Image


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ["id", "user", "created_at", "messages"]
        
        


class FlightInfoSerializer(serializers.ModelSerializer):
    date_jalali = serializers.SerializerMethodField()
    datetime_jalali = serializers.SerializerMethodField()

    class Meta:
        model = FlightInfo
        fields = ['date', 'time', 'airline', 'date_jalali', 'datetime_jalali']

    def get_date_jalali(self, obj):
        return obj.date_jalali.strftime('%Y/%m/%d') if obj.date_jalali else None

    def get_datetime_jalali(self, obj):
        return obj.datetime_jalali.strftime('%Y/%m/%d - %H:%M') if obj.datetime_jalali else None
    
class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'star']  

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name']  
        
class ItineraryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryItem
        fields = ['description']  # یا هر فیلدی که داری

class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['url']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            else:
                return obj.file.url
        return None


class TourSerializer(serializers.ModelSerializer):
    departure = FlightInfoSerializer()
    return_info = FlightInfoSerializer()
    hotel = HotelSerializer()
    services = ServiceSerializer(many=True)
    itinerary = ItineraryItemSerializer(many=True)
    images = ImageSerializer(many=True)
    price = serializers.IntegerField()  
    class Meta:
        model = Tour
        fields = [
            'tour_id',
            'name',
            'destination',
            'destination_type',
            'duration_days',
            'price',
            'departure',
            'return_info',
            'hotel',
            'services',
            'itinerary',
            'images',
            'insurance_included',
            'rich_text',
        ]    