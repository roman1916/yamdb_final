import string

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from rest_framework.permissions import (
    SAFE_METHODS,
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import SUPPORT_MAIL

from .filters import TitleFilter
from .models import Category, User, Genre, Title
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdminOrReadOnly
)
from .serializers import (
    CategoriesSerializer,
    CommentSerializer,
    GenresSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    SendEmailSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer
)

GET_TOKEN_INVALID_REQUEST = (
    'O-ops! The user with such data was not found, check the entered data!'
)
EMAIL_SUBJECT = 'YamDB - Confirmation Code'
EMAIL_TEXT = ('You secret code for getting the token: {confirmation_code}\n'
              'Don\'t sent it on to anyone!')
CONFIRMATION_CODE_LENGTH = 16
ALLOWED_METHODS = ('get', 'post', 'patch', 'delete')


class BaseCategoriesViewSet(
    CreateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet
):
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    queryset = User.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ALLOWED_METHODS

    @action(
        methods=('GET', 'PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


class SendEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email').lower()
        username = email.split('@')[0]
        alphabet = string.ascii_letters + string.digits
        confirmation_code = get_random_string(
            CONFIRMATION_CODE_LENGTH, alphabet
        )
        send_mail(
            EMAIL_SUBJECT,
            EMAIL_TEXT.format(confirmation_code=confirmation_code),
            SUPPORT_MAIL,
            (email,)
        )
        usernames = [user.username for user in User.objects.all()]
        while username in usernames:
            username += '2'
        user = User.objects.filter(email=email)
        if not user.exists():
            User.objects.create(
                email=email,
                username=username,
                confirmation_code=confirmation_code,
            )
        else:
            user.update(confirmation_code=confirmation_code)
        return Response(serializer.validated_data)


class GetToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email').lower()
        confirmation_code = request.data.get('confirmation_code')
        user = User.objects.filter(
            email=email, confirmation_code=confirmation_code
        )
        if not user.exists():
            return Response({'error': GET_TOKEN_INVALID_REQUEST})
        token = str(AccessToken.for_user(user.first()))
        return Response({'token': token})


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdminOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ALLOWED_METHODS

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdminOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ALLOWED_METHODS

    def get_review(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return get_object_or_404(
            title.reviews, id=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class CategoriesViewSet(BaseCategoriesViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(BaseCategoriesViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class TitlesViewset(ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ALLOWED_METHODS

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer
