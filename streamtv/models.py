from django.db import models
from django.db.models import Q
from datetime import datetime, date, timedelta
from django.db.models.functions import Now
from django.db.models.functions import Length
from  django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
models.CharField.register_lookup(Length)
# Create your models here.

# Id for each django model is created by default 
class Artist(models.Model):
    name = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)
    def __str__(self):
        return f"{self.name} {self.surname}"

class Studio(models.Model):
    name = models.CharField(max_length=25, unique=True)
    hq_location = models.CharField(max_length=50, null=True)
    studio_head = models.ForeignKey(Artist, related_name="current_studio", on_delete=models.CASCADE, unique=True) 
    def __str__(self):
        return f"{self.name}"

class Franchise(models.Model):
    name = models.CharField(max_length=50, unique=True)
    rights_owner = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"


class Serie(models.Model):
    class GenreType(models.TextChoices):
        MUSICAL = 'MUS', 'Musical'
        THRILLER = 'THR', 'Thriller'
        COMEDY = 'COM', 'Comedy'
        ACTION = 'ACT', 'Action'
        DRAMA = 'DRM' , 'Drama'
        HORROR = 'HOR', 'Horror'
        DOCUMENTARY = 'DOC', 'Documentary'
        NOT_SPECIFIED = '-', 'Not_specified'
    
    class Classification(models.TextChoices):
        EVERYONE  = 'T', 'For_Everyone'
        NOT_UNDER_14 = '14+', 'Not_for_under_14' 
        NOT_UNDER_18 = '18+', 'Mature_content'
    
    name = models.CharField(max_length=50, unique=True)
    franchise = models.ForeignKey(Franchise, related_name="series", on_delete=models.CASCADE)
    genre = models.CharField(
            max_length=3,
            choices=GenreType.choices,
            default= GenreType.NOT_SPECIFIED
            )
    classification = models.CharField(
            max_length=3,
            choices=Classification.choices,
            default=Classification.EVERYONE
            )
    def __str__(self):
        return f"{self.name}"


class Episode(models.Model):
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=50)
    season_num = models.PositiveIntegerField()
    serie = models.ForeignKey(Serie, related_name="episodes", on_delete=models.CASCADE) 
    studio = models.ForeignKey(Studio, related_name="ep_produced", on_delete=models.SET_NULL, null=True) 
    director = models.ForeignKey(Artist, related_name="ep_directed", on_delete=models.SET_NULL, null=True)
    minutes_length = models.PositiveIntegerField()
    airing_date = models.DateField()
    finale = models.BooleanField()
    ratings = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True,  default='NULL') 

    def __str__(self):
        return f"E{self.number} S{self.season_num} {self.serie.name}"
    def clean(self):
        # check if the episode is already present and some datefield has been changed
        if self.id != None:
            prev_data = Episode.objects.get(pk=self.id)
            if self.airing_date != prev_data.airing_date:
                raise ValidationError({"airing_date":("Cannot change the airing date of an already saved Episode model instance")})

        if self.finale != None:
            if (self.finale == 1) and (Episode.objects.filter(serie = self.serie, season_num = self.season_num, finale=1).exclude(id=self.id)):
                raise ValidationError({"finale":("There is already a finale for this season")})
    
    def save(self, **kwargs):
        
        # ratings field calculation is done at db level, the model shouldn't write a value
        self.ratings = None
        super().save(**kwargs) 

    class Meta:
        ordering = ["serie", "season_num", "number"]
        constraints =[
                models.UniqueConstraint(
                    fields=["serie", "season_num", "number"],
                    name="unique_episode_per_season_per_serie"
                    )
                ]

class Registered_User(models.Model):
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128, unique=True)
    username = models.CharField(max_length=50, unique=True)
    registration_date = models.DateField()
    birth_date = models.DateField()
    fav_series = models.ManyToManyField(Serie, related_name="favorite_of", through='UserFavoriteSerie')
    watch_history = models.ManyToManyField(Episode, related_name="watched_by", through='UserWatchHistory')
    reviews = models.ManyToManyField(Episode, related_name="reviewed_by", through='UserReview')
    followed_artists = models.ManyToManyField(Artist, related_name="followers", blank=True) 
    followed_studios = models.ManyToManyField(Studio, related_name="followers", blank=True) 
    def __str__(self):
        return f"utente {self.id}: {self.username}"

    @property
    def last_watched_ep(self):
        last_ep = UserWatchHistory.objects.filter(user = self.id).order_by("-watch_date").first().episode
        return last_ep



    def clean(self):
        # check if the user is already present and some datefield has been changed
        if self.id != None:
            prev_data = Registered_User.objects.get(pk=self.id)
            if self.birth_date != prev_data.birth_date:
                raise ValidationError({"birth_date":("Cannot change the birth date of an already saved Registered User model instance")})
            if self.registration_date != prev_data.registration_date:
                raise ValidationError({"registration_date":("Cannot change the registration date of an already saved Registered User model instance ")})
        # check if the dates are valid
        if self.birth_date !=None and self.registration_date !=None:
            if self.birth_date > self.registration_date:
                raise ValidationError({"birth_date": (f"Invalid date: max boundary for acceptable registration date is {date.today()}")})
            if self.registration_date > date.today():
                raise ValidationError({"registration_date": (f"Invalid date: max boundary for acceptable registration date is {date.today()}")})
    class Meta:
        constraints = [
                models.CheckConstraint(
                    check=Q(password__length__gte=8),
                    name="password_min_length")
            ]

class UserFavoriteSerie(models.Model):
    user = models.ForeignKey(Registered_User, on_delete=models.CASCADE)
    serie = models.ForeignKey(Serie, related_name="marked_favorite", on_delete=models.CASCADE)
    added_date = models.DateField()
    def __str__(self):
        return f"favorite of {self.user.username}: {self.serie.name}"
    def clean(self):
        if self.added_date != None:
            if self.added_date < self.user.registration_date:
                raise ValidationError({"added_date": ("Invalid date: added date cannot precede user registration date")})
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['user','serie'],
                    name="unique_serie_per_user")
                ]


class UserWatchHistory(models.Model):

    user = models.ForeignKey(Registered_User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, related_name="watch_list", on_delete=models.CASCADE)
    watch_date = models.DateField()
    def __str__(self):
        return f"{self.user} watched {self.episode}"

    def clean(self):
        if self.watch_date !=None and hasattr(self, "episode"):
            if self.watch_date < self.episode.airing_date:
                raise ValidationError({"watch_date": ("Invalid date: watch date cannot precede airing date of episode")})
            if self.watch_date < self.user.registration_date:
                raise ValidationError({"watch_date": ("Invalid date: watch date cannot precede birth date of user")})
            if (self.episode.serie.classification =='14+'and self.watch_date - self.user.registration_date < timedelta(days=365*14)) or (self.episode.serie.classification == '18+' and self.watch_date - self.user.registration_date < timedelta(days=365*18)) :
                raise ValidationError({"user":("Invalid user: user not old enough to see episodes of this serie")})

class UserReview(models.Model):
    
    class Rating(models.TextChoices):
        POSITIVE = 'Positive', 'Positive vote'
        NEGATIVE = 'Negative', 'Negative vote'

    vote = models.CharField(
            max_length=8,
            choices=Rating.choices)
    user = models.ForeignKey(Registered_User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, related_name="reviews", on_delete=models.CASCADE)
    comment = models.TextField(max_length=250, null=True, blank=True)

    class Meta:
        constraints = [ 
                models.UniqueConstraint(
                    fields=['user','episode'],
                    name="unique_episode_review_per_user")                
                ]
    def __str__(self):
        return f"E{self.episode.number} S{self.episode.season_num} {self.episode.serie} : {self.vote} vote by {self.user.username}"
    
    def clean(self):
        if hasattr(self, "user") and hasattr(self, "episode"):
            if not UserWatchHistory.objects.filter(user = self.user, episode = self.episode):
                raise ValidationError({"user":("Only users that watched an episode can review it")})


class Playlist(models.Model):
    name = models.CharField(max_length=50)
    creation_date = models.DateField()
    user = models.ForeignKey(Registered_User,related_name="saved_playlists", on_delete=models.CASCADE)
    saved_episodes = models.ManyToManyField(Episode, related_name="in_playlists")
    def __str__(self):
        return f"Playlist {self.name} by {self.user.username}"
    def clean(self):
        if self.creation_date != None and hasattr(self, "user"):
            if self.creation_date < self.user.registration_date:
                raise ValidationError({"creation_date":("Invalid date: creation date cannot precede birth date of user")})

