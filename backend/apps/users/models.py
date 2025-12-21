"""
User and NotificationPreferences models for TIME BLOCK
Based on database_erd.md specifications
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for TIME BLOCK
    Uses email for authentication instead of username
    Supports OAuth 2.0 (Google, Kakao)
    """

    # OAuth provider choices
    class OAuthProvider(models.TextChoices):
        GOOGLE = 'google', 'Google'
        KAKAO = 'kakao', 'Kakao'

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, verbose_name='Email')
    username = models.CharField(max_length=100, verbose_name='Username')
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name='Password Hash')

    # OAuth fields
    oauth_provider = models.CharField(
        max_length=20,
        choices=OAuthProvider.choices,
        null=True,
        blank=True,
        verbose_name='OAuth Provider'
    )
    oauth_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='OAuth ID')
    profile_image = models.URLField(max_length=500, null=True, blank=True, verbose_name='Profile Image URL')

    # User preferences
    timezone = models.CharField(max_length=50, default='Asia/Seoul', verbose_name='Timezone')

    # Premium subscription
    is_premium = models.BooleanField(default=False, verbose_name='Premium Member')
    premium_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Premium Expiration Date')

    # Django required fields
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_staff = models.BooleanField(default=False, verbose_name='Staff Status')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    # Manager
    objects = UserManager()

    # Authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['oauth_provider', 'oauth_id'], name='idx_user_oauth'),
            models.Index(fields=['is_premium', 'premium_expires_at'], name='idx_user_premium'),
        ]
        constraints = [
            # Ensure oauth_id is unique per provider
            models.UniqueConstraint(
                fields=['oauth_provider', 'oauth_id'],
                condition=models.Q(oauth_provider__isnull=False),
                name='unique_oauth_provider_id'
            )
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @property
    def is_oauth_user(self):
        """Check if user registered via OAuth"""
        return self.oauth_provider is not None

    @property
    def is_premium_active(self):
        """Check if premium subscription is active"""
        if not self.is_premium:
            return False
        if self.premium_expires_at is None:
            return True  # Lifetime premium
        return timezone.now() < self.premium_expires_at


class NotificationPreferences(models.Model):
    """
    Silent notification preferences for each user
    JSON flash_pattern: {duration, count, interval, color}
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='User'
    )

    # Notification toggles
    sound_enabled = models.BooleanField(default=False, verbose_name='Sound Enabled')
    screen_flash_enabled = models.BooleanField(default=True, verbose_name='Screen Flash Enabled')
    vibration_enabled = models.BooleanField(default=True, verbose_name='Vibration Enabled')
    device_flash_enabled = models.BooleanField(default=False, verbose_name='Device Flash Enabled (Premium)')

    # Flash pattern customization (JSON)
    flash_pattern = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Flash Pattern',
        help_text='JSON: {duration: 500, count: 3, interval: 200, color: "#10b981"}'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
        indexes = [
            models.Index(fields=['user'], name='idx_notification_user'),
        ]

    def __str__(self):
        return f'Notification Preferences for {self.user.email}'

    def get_default_flash_pattern(self):
        """Return default flash pattern if not set"""
        return self.flash_pattern or {
            'duration': 500,
            'count': 3,
            'interval': 200,
            'color': '#10b981'
        }
