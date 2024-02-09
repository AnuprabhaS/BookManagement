from rest_framework import generics
from .serializers import (RegisterSerializer, LoginSerliazer, AuthorSerializer,
                          CreateAuthorSerializer, BookSerializer, BookUpdateSerializer,
                          ReviewSerializer)
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from .models import Author, Book, Review
from django.db.models import Sum

# Create your views here.
class Register(generics.CreateAPIView):
    permission_classes = []
    authentication_classes = ()
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            User.objects.create_user(email=data['email'].lower(), first_name=data['first_name'],
                                       last_name=data['last_name'], username=data['email'],
                                       password=data['password'])
            return Response(status=201)
        return Response({"errors": serializer.errors},
                        status=400)
    

class Login(generics.GenericAPIView):
    permission_classes = []
    authentication_classes = ()
    serializer_class = LoginSerliazer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return Response({"message": "Success"})
            else:
                return Response({"message": "Invalid credentials"}, status=401)
        return Response({"errors": serializer.errors}, status=400)


class AuthorView(generics.ListCreateAPIView):   #creating and listing authors
    serializer_class = AuthorSerializer
    
    def get_queryset(request, *args, **kwargs):
        return Author.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = CreateAuthorSerializer(data=request.data)
        if serializer.is_valid():
            Author.objects.create(name=request.data['name'])
        return Response(status=201)
    

class BooksView(generics.ListAPIView, generics.UpdateAPIView):  #list and update books
    serializer_class = BookSerializer

    def get_queryset(request, *args, **kwargs):
        return Book.objects.all()
    
    def update(self, request, *args, **kwargs):
        book = Book.objects.get(id=kwargs.get('id'))
        serializer = BookUpdateSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Success"})
        return Response({"errors": serializer.errors}, status=400)
    
    
class AddReview(generics.GenericAPIView):   #review book or author

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            review_type = request.data.get('review_type')
            if review_type == "author":
                review, _ = Review.objects.update_or_create(
                    author=data.get('author'),
                    added_by = self.request.user
                )
                review.rating = data.get('rating')
                review.comment = data.get('comment')
                review.save()
                author_obj = Author.objects.get(id=data.get('author').id)
                total_reviews = author_obj.review_set.count()
                total_rating = author_obj.review_set.aggregate(Sum('rating'))['rating__sum']
                average_rating = total_rating / total_reviews
                author_obj.total_rating = average_rating
                author_obj.save()
            else:
                review, _ = Review.objects.update_or_create(book=data.get('book'),
                                                            added_by = self.request.user)
                review.rating = data.get('rating')
                review.comment = data.get('comment')
                review.save()
                book_obj = Book.objects.get(id=data.get('book').id)
                total_reviews = book_obj.review_set.count()
                total_rating = book_obj.review_set.aggregate(Sum('rating'))['rating__sum']
                average_rating = total_rating / total_reviews if total_rating > 0 else 0
                book_obj.total_rating = average_rating
                book_obj.save()
            return Response({"message": "Success"}, status=201)
        return Response({"message": serializer.errors}, status=400)

    
class AuthorReview(generics.GenericAPIView):    #list reviews of author

    def get(self, request, *args, **kwargs):
        reviews = Review.objects.filter(author__id=kwargs['author_id'])
        serializer = ReviewSerializer(reviews, many=True)
        return Response({"reviews": serializer.data})
    
