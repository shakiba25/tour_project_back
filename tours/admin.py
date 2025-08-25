from django.contrib import admin
from .models import Tour, Hotel, FlightInfo, Service, ItineraryItem, Image


# class ImageInline(admin.TabularInline):  # یا StackedInline برای ظاهر ستونی
#     model = Tour.images.through          # چون ManyToMany هست
#     extra = 1


class ServiceInline(admin.TabularInline):
    model = Tour.services.through
    extra = 1


class ItineraryInline(admin.TabularInline):
    model = Tour.itinerary.through
    extra = 1


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("tour_id", "name", "destination", "price", "insurance_included")
    inlines = [ ServiceInline, ItineraryInline] #ImageInline,
    search_fields = ("name", "destination")
    list_filter = ("destination", "insurance_included")


# @admin.register(Image)
# class ImageAdmin(admin.ModelAdmin):
#     list_display = ("id", "file")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "star")


@admin.register(FlightInfo)
class FlightInfoAdmin(admin.ModelAdmin):
    list_display = ("airline", "date", "time")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ("description",)
