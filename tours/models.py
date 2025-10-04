from django.db import models
from django.contrib.auth.models import User
import jdatetime


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
    
    @property
    def date_jalali(self):
        """تاریخ شمسی"""
        return jdatetime.date.fromgregorian(date=self.date)

    @property
    def datetime_jalali(self):
        """تاریخ و زمان شمسی"""
        from datetime import datetime
        dt = datetime.combine(self.date, self.time)
        return jdatetime.datetime.fromgregorian(datetime=dt)

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

# --------------------------------

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question

# --------------------------------

class Chunk(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="chunks")
    chunk_type = models.CharField(max_length=50)
    text = models.TextField()
    
    
class ChunkEmbedding(models.Model):
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE, related_name="embedding")
    vector = models.BinaryField()  # ذخیره‌سازی باینری numpy (faiss-compatible)


class FAQChunk(models.Model):
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name="chunks")
    chunk_type = models.CharField(max_length=50, default="faq")
    text = models.TextField()


class FAQChunkEmbedding(models.Model):
    chunk = models.OneToOneField(FAQChunk, on_delete=models.CASCADE, related_name="embedding")
    vector = models.BinaryField()
    
    
#--------------------------- ChatBot
class ChatSession(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # برای تشخیص چت باز فعلی

    def __str__(self):
        return f"Chat {self.id} - {self.user or 'Guest'}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]
    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.content[:30]}"


