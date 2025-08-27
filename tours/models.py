from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    star = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.name} ⭐{self.star}"


class FlightInfo(models.Model):
    date = models.DateField()
    time = models.TimeField()
    airline = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.airline} - {self.date} {self.time}"


class Service(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ItineraryItem(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description


class Image(models.Model):
    # به جای URLField از ImageField استفاده می‌کنیم
    file = models.ImageField(upload_to="tours/images/")

    def __str__(self):
        return self.file.url if self.file else "No Image"


class Tour(models.Model):
    tour_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    destination = models.CharField(max_length=100)
    destination_type = models.CharField(  
        max_length=50,
        null=True,
        blank=True,
        choices=[("داخلی", "داخلی"), ("خارجی", "خارجی")]
    )
    duration_days = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()

    # روابط
    departure = models.OneToOneField(
        FlightInfo, on_delete=models.CASCADE, related_name="departure_tour"
    )
    return_info = models.OneToOneField(
        FlightInfo, on_delete=models.CASCADE, related_name="return_tour"
    )
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    services = models.ManyToManyField(Service, blank=True)
    itinerary = models.ManyToManyField(ItineraryItem, blank=True)
    images = models.ManyToManyField(Image, blank=True)

    insurance_included = models.BooleanField(default=False)
    rich_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.tour_id})"



# model 2

from django.db import models
from django.core.exceptions import ValidationError

# ======== Validators ======== #
def validate_departure(value):
    required_keys = {"date", "time", "airline"}
    if not isinstance(value, dict):
        raise ValidationError("departure باید دیکشنری باشه.")
    if set(value.keys()) != required_keys:
        raise ValidationError(f"departure باید شامل فیلدهای {required_keys} باشه.")

def validate_return(value):
    required_keys = {"date", "time", "airline"}
    if not isinstance(value, dict):
        raise ValidationError("return_info باید دیکشنری باشه.")
    if set(value.keys()) != required_keys:
        raise ValidationError(f"return_info باید شامل فیلدهای {required_keys} باشه.")

def validate_hotel(value):
    required_keys = {"name", "star"}
    if not isinstance(value, dict):
        raise ValidationError("hotel باید دیکشنری باشه.")
    if set(value.keys()) != required_keys:
        raise ValidationError(f"hotel باید شامل فیلدهای {required_keys} باشه.")

def validate_services(value):
    if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
        raise ValidationError("services باید لیستی از رشته‌ها باشه.")

def validate_itinerary(value):
    if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
        raise ValidationError("itinerary باید لیستی از رشته‌ها باشه.")

def validate_images(value):
    if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
        raise ValidationError("images باید لیستی از URLها باشه.")


class Chunk(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="chunks")
    chunk_type = models.CharField(max_length=50)
    text = models.TextField()
    
    
class ChunkEmbedding(models.Model):
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE, related_name="embedding")
    vector = models.BinaryField()  # ذخیره‌سازی باینری numpy (faiss-compatible)



# class TourChunk(models.Model):
#     tour = models.ForeignKey("Tour", on_delete=models.CASCADE, related_name="chunks")
#     chunk_type = models.CharField(max_length=50)
#     text = models.TextField()

#     def __str__(self):
#         return f"{self.tour.name} - {self.chunk_type}"
    
    

# # ======== مدل Tour ======== #
# class Tour2(models.Model):
#     tour_id = models.CharField(max_length=50, unique=True)
#     name = models.CharField(max_length=200)
#     destination = models.CharField(max_length=100)
#     destination_type = models.CharField(
#         max_length=50,
#         null=True,
#         blank=True,
#         choices=[("داخلی", "داخلی"), ("خارجی", "خارجی")]
#     )
#     duration_days = models.PositiveSmallIntegerField()
#     price = models.PositiveIntegerField()

#     # JSON fields
#     departure = models.JSONField(validators=[validate_departure])
#     return_info = models.JSONField(validators=[validate_return])
#     hotel = models.JSONField(validators=[validate_hotel])
#     services = models.JSONField(validators=[validate_services], default=list)
#     itinerary = models.JSONField(validators=[validate_itinerary], default=list)
#     images = models.JSONField(validators=[validate_images], default=list)

#     insurance_included = models.BooleanField(default=False)
#     rich_text = models.TextField(blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.name} ({self.tour_id})"
