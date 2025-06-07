from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'first_name', 'last_name', 'email', 'gender', 'birth_date']
    
    def validate_email(self, value):
        """
        Validate that email is unique across all UserProfiles
        """
        # Convert empty string to None for consistency
        if value == '':
            value = None
            
        if value:  # Only validate if email is provided
            # Check if this email is already used by another user
            existing_profile = UserProfile.objects.filter(email=value).first()
            
            # If updating existing profile, exclude current instance
            if self.instance and existing_profile and existing_profile.user != self.instance.user:
                raise serializers.ValidationError("Email này đã được sử dụng bởi người dùng khác.")
            elif not self.instance and existing_profile:
                raise serializers.ValidationError("Email này đã được sử dụng bởi người dùng khác.")
                
        return value

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def validate_email(self, value):
        """
        Validate that email is unique across all UserProfiles during registration
        """
        # Convert empty string to None for consistency
        if value == '':
            value = None
            
        if value:  # Only validate if email is provided
            # Check if this email is already used by another user
            existing_profile = UserProfile.objects.filter(email=value).first()
            if existing_profile:
                raise serializers.ValidationError("Email này đã được sử dụng bởi người dùng khác.")
                
        return value

    def create(self, validated_data):
        # Extract profile-related data with default values
        email = validated_data.pop('email', '')
        first_name = validated_data.pop('first_name', '') or 'Jane'  # Default to 'Jane'
        last_name = validated_data.pop('last_name', '') or 'Doe'     # Default to 'Doe'
        
        # Convert empty email to None
        if email == '':
            email = None
        
        # Create user with just username and password
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        
        # Create UserProfile with the personal information and defaults
        UserProfile.objects.create(
            user=user,
            email=email,
            first_name=first_name,
            last_name=last_name,
            gender='O',  # Default to 'Khác'
            birth_date='2000-01-01',  # Default birth date
            profile_picture=None  # Default to empty avatar
        )
        return user

class UserProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
    
    def update(self, instance, validated_data):
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.save()
        return instance