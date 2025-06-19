from django.db import models
from django.conf import settings

class County(models.Model):
    """Shared reference data for counties"""
    county_id = models.AutoField(primary_key=True)
    county_name = models.CharField(max_length=100, unique=True)
    county_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Counties'
        verbose_name_plural = 'Counties'
    
    def __str__(self):
        return self.county_name

class SubCounty(models.Model):
    """Shared reference data for sub-counties"""
    sub_county_id = models.AutoField(primary_key=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='sub_counties')
    sub_county_name = models.CharField(max_length=100)
    sub_county_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'SubCounties'
        verbose_name_plural = 'Sub Counties'
        unique_together = [['county', 'sub_county_name'], ['county', 'sub_county_code']]
    
    def __str__(self):
        return f"{self.sub_county_name}, {self.county.county_name}"

class UserAddress(models.Model):
    """User's saved delivery addresses"""
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=100, help_text="e.g., Westlands, Karen, etc.")
    detailed_address = models.TextField(help_text="Building, floor, apartment number, landmarks, etc.")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'UserAddresses'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['county']),
            models.Index(fields=['sub_county']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.location_name}, {self.sub_county.sub_county_name}"
    
    def save(self, *args, **kwargs):
        # If this address is being set as default, unset any other default for this user
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

# Keep the old Location model for backward compatibility (we'll migrate data later)
class Location(models.Model):
    """DEPRECATED: Use UserAddress instead"""
    location_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    location_name = models.CharField(max_length=100)
    sub_location = models.CharField(max_length=100, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Locations'  # Keep existing table name
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.location_name} - {self.user.get_full_name()}"
