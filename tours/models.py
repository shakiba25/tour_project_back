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
    url = models.URLField()

    def __str__(self):
        return self.url


class Tour(models.Model):
    tour_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    destination = models.CharField(max_length=100)
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
