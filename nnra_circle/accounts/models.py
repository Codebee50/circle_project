from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Department(models.Model):
    dept_name = models.CharField(null=False, blank=False, max_length=255)

class Office(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='offices')
    office_name = models.CharField(null=False, blank=False, max_length=255)

    def __str__(self) -> str:
        return self.office_name

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False, related_name='profile')
    office = models.ForeignKey(Office, null=True, on_delete= models.SET_NULL, related_name='profile' )
    profileImg= models.ImageField(upload_to='users/%Y/%M/%d', default='def-user-img.png')
    phone = models.CharField(max_length=11, null=True, blank=True)
    is_online = models.BooleanField(default=False)
    joined = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)
    is_email_verified = models.BooleanField(default=False)
    about = models.TextField(blank=True, null=True)
    fullname = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-joined']
        indexes = [
            models.Index(fields=['-joined'])
        ]


    def __str__(self) -> str:
        return self.user.username
    
    def save(self, *args, **kwargs):
        self.fullname = self.user.get_full_name()
        super().save(*args, **kwargs)
        

class Otpcode(models.Model):
    class Type(models.TextChoices):
        AUTHENTICATION = 'LC', 'Authentication',
        PASSWORD_RESET = 'PC', 'Password reset'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, related_name='otpcode')
    code = models.CharField(max_length=6, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    type = models.CharField(max_length=2, choices=Type.choices, default=Type.AUTHENTICATION)

    #returns true or false indicating if the otp is expired or not.
    @property
    def expired(self):
        # time delta can be used to perform date and time arithmetic
        expiration_duration = timedelta(minutes=10)#returns a date time object
        expiration_time = self.created + expiration_duration
        return timezone.now() > expiration_time
    
    def get_tte(self):#returns the time to expiry 
        expiration_duration = timedelta(minutes=10)
        expiration_time = self.created + expiration_duration
        now = timezone.now()
     
        # Calculate remaining time (if not expired)
        remaining_time = expiration_time - now
        remaining_minutes = int(remaining_time.total_seconds() / 60)
        return remaining_minutes
