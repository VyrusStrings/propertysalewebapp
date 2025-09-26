from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Property(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    city = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    size_sqm = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField()
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="properties/covers/", blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cover = models.ImageField(upload_to="properties/covers/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.city}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("properties:detail", args=[self.slug])

    def __str__(self):
        return self.title
    
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="properties/gallery/")
    alt = models.CharField(max_length=120, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.property} — {self.id}"
    

