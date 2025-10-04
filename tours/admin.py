from django.contrib import admin
from .models import Tour, Hotel, FlightInfo, Service, ItineraryItem, Image , Chunk , ChunkEmbedding , ChatMessage , ChatSession , FAQ , FAQChunk , FAQChunkEmbedding
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
    
    
    
    
    
    
    
    
    
    
# tours/admin.py
from django.contrib import admin
from .models import FAQ, FAQChunk, FAQChunkEmbedding

# ----------------------------
# Inline برای نمایش چانک‌های FAQ در خود FAQ
# ----------------------------
class FAQChunkInline(admin.TabularInline):
    model = FAQChunk
    extra = 0  # بدون چانک خالی اضافی
    readonly_fields = ("chunk_type", "text")  # فقط خواندنی، چون معمولاً خودکار ساخته می‌شوند
    can_delete = True

# ----------------------------
# Inline برای نمایش embedding هر چانک (خواندنی)
# ----------------------------
class FAQChunkEmbeddingInline(admin.TabularInline):
    model = FAQChunkEmbedding
    readonly_fields = ("vector",)
    can_delete = False
    extra = 0

# ----------------------------
# Admin FAQChunk
# ----------------------------
@admin.register(FAQChunk)
class FAQChunkAdmin(admin.ModelAdmin):
    list_display = ("faq", "chunk_type", "text_short")
    list_filter = ("chunk_type",)
    search_fields = ("text", "faq__question")

    inlines = [FAQChunkEmbeddingInline]

    def text_short(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_short.short_description = "متن چانک"

# ----------------------------
# Admin FAQ
# ----------------------------
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "answer_short", "created_at", "updated_at")
    search_fields = ("question", "answer")
    inlines = [FAQChunkInline]

    def answer_short(self, obj):
        return obj.answer[:50] + "..." if len(obj.answer) > 50 else obj.answer
    answer_short.short_description = "جواب کوتاه"

# ----------------------------
# Admin FAQChunkEmbedding (خواندنی)
# ----------------------------
@admin.register(FAQChunkEmbedding)
class FAQChunkEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("chunk", "vector_size")
    readonly_fields = ("vector",)

    def vector_size(self, obj):
        import numpy as np
        if obj.vector:
            arr = np.frombuffer(obj.vector, dtype=np.float32)
            return arr.shape[0]
        return 0
    vector_size.short_description = "ابعاد وکتور"    