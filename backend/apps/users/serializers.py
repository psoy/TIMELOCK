"""
Serializers for users app
"""

from rest_framework import serializers
from .models import User, NotificationPreferences


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreferences model"""

    class Meta:
        model = NotificationPreferences
        fields = [
            'id',
            'sound_enabled',
            'screen_flash_enabled',
            'vibration_enabled',
            'device_flash_enabled',
            'flash_pattern',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_flash_pattern(self, value):
        """Validate flash pattern structure"""
        if not isinstance(value, dict):
            return value

        # Expected keys
        expected_keys = {'duration', 'count', 'interval', 'color'}

        # Check if all expected keys are present
        if value and not expected_keys.issubset(value.keys()):
            raise serializers.ValidationError(
                'Flash pattern must contain: duration, count, interval, color'
            )

        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    notification_preferences = NotificationPreferencesSerializer(read_only=True)
    is_oauth_user = serializers.BooleanField(read_only=True)
    is_premium_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'oauth_provider',
            'oauth_id',
            'profile_image',
            'timezone',
            'is_premium',
            'premium_expires_at',
            'is_oauth_user',
            'is_premium_active',
            'notification_preferences',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'oauth_provider',
            'oauth_id',
            'is_premium',
            'premium_expires_at',
            'is_oauth_user',
            'is_premium_active',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        # Create default notification preferences
        NotificationPreferences.objects.create(user=user)

        return user

    def update(self, instance, validated_data):
        """Update user, handling password separately"""
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'timezone']

    def validate(self, data):
        """Validate password match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        return data

    def create(self, validated_data):
        """Create user with password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create default notification preferences
        NotificationPreferences.objects.create(user=user)

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates"""

    class Meta:
        model = User
        fields = ['username', 'profile_image', 'timezone']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """Validate passwords"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'Passwords must match'})
        return data

    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value

    def save(self):
        """Change password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
