from django.contrib import admin
from .models import Tour, Hotel, FlightInfo, Service, ItineraryItem, Image , Chunk , ChunkEmbedding , ChatMessage , ChatSession
import jdatetime


# ✅ ثبت مدل‌های Chunk و ChunkEmbedding به صورت امن
for model in [Chunk]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass


class ImageInline(admin.TabularInline):  # یا StackedInline برای ظاهر ستونی
    model = Tour.images.through          # چون ManyToMany هست
    extra = 1


class ServiceInline(admin.TabularInline):
    model = Tour.services.through
    extra = 1


class ItineraryInline(admin.TabularInline):
    model = Tour.itinerary.through
    extra = 1


class TourAdmin(admin.ModelAdmin):
    list_display = ("tour_id", "name", "destination", "price", "insurance_included",
                    "departure_shamsi", "return_shamsi")
    
    def departure_shamsi(self, obj):
        if obj.departure and obj.departure.date:
            return jdatetime.date.fromgregorian(date=obj.departure.date).strftime("%Y-%m-%d")
        return "-"
    departure_shamsi.short_description = "تاریخ رفت (شمسی)"
    
    def return_shamsi(self, obj):
        if obj.return_info and obj.return_info.date:
            return jdatetime.date.fromgregorian(date=obj.return_info.date).strftime("%Y-%m-%d")
        return "-"
    return_shamsi.short_description = "تاریخ برگشت (شمسی)"
    
    list_filter = ("destination", "insurance_included")
    search_fields = ("name", "destination")
    
admin.site.register(Tour, TourAdmin)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "file")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "star")



# @admin.register(FlightInfo)
# class FlightInfoAdmin(admin.ModelAdmin):
#     list_display = ("airline", "date", "time")



@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ("description",)


class FlightInfoAdmin(admin.ModelAdmin):
    list_display = ("airline", "date", "time", "departure_shamsi")

    def departure_shamsi(self, obj):
        return jdatetime.date.fromgregorian(date=obj.date).strftime("%Y-%m-%d")
    departure_shamsi.short_description = "تاریخ شمسی"

admin.site.register(FlightInfo, FlightInfoAdmin)


import numpy as np
import io

@admin.register(ChunkEmbedding)
class ChunkEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'chunk', 'vector_preview')  # نمایش فیلد خلاصه وکتور

    def vector_preview(self, obj):
        import numpy as np

        try:
            # فرض می‌کنیم dtype و شکل آرایه مشخصه؛ مثلا float32 و طول 300
            vector = np.frombuffer(obj.vector, dtype=np.float32)
            return str(vector[:5]) + '...'
        except Exception as e:
            return f'خطا: {e}'


    vector_preview.short_description = 'پیش‌نمایش وکتور'
    
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0  # تعداد فرم‌های اضافه برای اضافه کردن پیام جدید، صفر یعنی نشون نمیده

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'is_active')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content', 'created_at')
    list_filter = ('role',)
    search_fields = ('content',)  