from rest_framework import serializers
from .models import CustomUser, FriendReq
from django.contrib.auth import authenticate
from .helpers import is_valid_email

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        # Normalize email by converting to lowercase
        value = value.lower()

        if not is_valid_email(value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def create(self, validated_data):
        validated_data['email'] = validated_data['email'].lower()  # Ensure email is saved in lowercase
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        # Normalize email by converting to lowercase
        value = value.lower()

        if not is_valid_email(value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate(self, data):
        email = data.get('email').lower()  # Normalize email before authentication
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        data['user'] = user
        return data
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendReq
        fields = ['id', 'user_from', 'user_to', 'status', 'timestamp']
        read_only_fields = ['status', 'timestamp']