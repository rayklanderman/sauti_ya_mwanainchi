from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class County(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    description = models.TextField(blank=True)
    governor = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('county_detail', kwargs={'code': self.code})

class Bill(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('public_participation', 'Public Participation'),
        ('review', 'Under Review'),
        ('passed', 'Passed'),
        ('rejected', 'Rejected')
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='bills')
    description = models.TextField()
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    document = models.FileField(upload_to='bills/', blank=True)
    public_participation_deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('bill_detail', kwargs={'slug': self.slug})

class Comment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.bill.title}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='residents')
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    is_county_admin = models.BooleanField(default=False)
    notification_preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}\'s Profile'

    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'username': self.user.username})

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment', 'New Comment'),
        ('reply', 'Reply to Comment'),
        ('status_change', 'Bill Status Change'),
        ('deadline', 'Approaching Deadline'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.notification_type} for {self.user.username}'
