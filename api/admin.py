from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('id', 'username', 'email', 'role')
    list_filter = ('username', 'email', 'role')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'first_name',
                           'last_name', 'bio', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email',
                       'first_name', 'last_name', 'bio', 'role')
        }),
    )
    empty_value = '<пусто>'


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('title', 'text', 'author',)
    search_fields = ('title', 'author',)
    empty_value_display = '<empty>'


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('review', 'text', 'author',)


@admin.register(Title)
class TitleAdmin(ModelAdmin):
    list_display = ('name', 'year', 'description', 'category',)
    search_fields = ('name',)
    list_filter = ('category',)
    empty_value_display = '<empty>'


@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ('name', 'slug',)
    empty_value_display = '<empty>'


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug',)
    empty_value_display = '<empty>'
