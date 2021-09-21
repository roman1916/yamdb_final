from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriesViewSet,
    CommentViewSet,
    GenresViewSet,
    GetToken,
    ReviewViewSet,
    SendEmail,
    TitlesViewset,
    UserViewSet
)

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'titles', TitlesViewset, basename='titles')
router_v1.register(
    r'categories',
    CategoriesViewSet,
    basename='categories'
)
router_v1.register(
    r'genres',
    GenresViewSet,
    basename='genres'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

token_authorization_by_email = [
    path('auth/email/', SendEmail.as_view(), name='send_email'),
    path('auth/token/', GetToken.as_view(), name='get_token'),
]

urlpatterns = [
    path('v1/', include(token_authorization_by_email)),
    path('v1/', include(router_v1.urls)),
]
