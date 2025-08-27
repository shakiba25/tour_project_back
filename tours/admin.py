from django.contrib import admin
from .models import Tour, Hotel, FlightInfo, Service, ItineraryItem, Image , Chunk , ChunkEmbedding
import jdatetime


# ✅ ثبت مدل‌های Chunk و ChunkEmbedding به صورت امن
for model in [Chunk, ChunkEmbedding]:
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