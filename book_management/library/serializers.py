from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Author, Book, Review


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_email(self, email):
        user = User.objects.filter(email=email)
        if user.exists():
            raise serializers.ValidationError("Email already exists")
        return email
    

class LoginSerliazer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class AuthorSerializer(serializers.ModelSerializer):
    total_books = serializers.SerializerMethodField()

    def get_total_books(self, obj):
        return obj.book_set.count()
    
    class Meta:
        model = Author
        fields = '__all__'
    
class CreateAuthorSerializer(serializers.Serializer):

    class Meta:
        model = Author
        fields = ['name']


class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.name')

    class Meta:
        model = Book
        fields = '__all__'

class BookUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['author', 'book', 'rating', 'comment']
    



    