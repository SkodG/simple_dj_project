from django.contrib import admin
from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from .models import Registered_User, Artist, Studio, Franchise, Playlist, Serie, Episode, UserFavoriteSerie, UserWatchHistory, UserReview
# Register your models here.
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "password", "registration_date")
    
class UserWatchHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "episode","watch_date")

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "creation_date", "user_id")
    filter_horizontal = ("saved_episodes",)

class ArtistAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "surname")

class StudioAdmin(admin.ModelAdmin):
    list_display = ("id","name", "hq_location", "studio_head")

class FranchiseAdmin(admin.ModelAdmin):
    list_display = ("id","name","rights_owner")

class SerieAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "franchise", "genre", "classification")

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("id", "number", "title", "season_num", "serie", "studio", "director", "minutes_length", "airing_date", "finale", "ratings")
    readonly_fields = ["ratings"]

class UserReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "vote", "user", "episode", "comment")

class UserFavoriteSerieAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "serie", "added_date")

admin.site.register(Registered_User, RegisteredUserAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Studio, StudioAdmin)
admin.site.register(Franchise, FranchiseAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Serie, SerieAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(UserFavoriteSerie, UserFavoriteSerieAdmin)
admin.site.register(UserWatchHistory, UserWatchHistoryAdmin)
admin.site.register(UserReview, UserReviewAdmin)
