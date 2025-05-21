from django.test import TransactionTestCase, TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError
from .models import *
from datetime import datetime, date
# Create your tests here.

class RegUserModelTest(TransactionTestCase):
    
    def setUp(self):
        self.user = Registered_User(email="ale95@gmail.com", password="asdfghjkl", username="ale95", registration_date=date(1995, 3, 19), birth_date=date(1985,3,1))

    def test_clean_method(self):
        self.user.clean() # the date is acceptable 
        self.user.registration_date = date(2080, 3, 19)
        self.assertEquals(self.user.registration_date, date(2080, 3, 19))
        with self.assertRaises(ValidationError):
            self.user.clean() # the date is a future date (not acceptable) 

    def test_str_method(self):
        self.assertEqual(str(self.user), f"utente {self.user.id}: ale95")

    def test_last_watched_ep_method(self):
        self.artist = Artist.objects.create(name= "David", surname= "Chase")
        self.studio = Studio.objects.create(name="HBO studios", hq_location="London, UK", studio_head = self.artist)
        self.franchise = Franchise.objects.create(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie.objects.create(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.episode = Episode.objects.create(number=1, title="pilot", season_num=1, serie=self.serie, studio=self.studio, director=self.artist, minutes_length=50, airing_date=date.today(), finale=0, ratings=None)
        self.user.save()
        # adding a new episode to the user watch history
        UserWatchHistory.objects.create(user = self.user, episode = self.episode, watch_date= date(2012,3,7))

        self.assertEqual(self.user.last_watched_ep, self.episode)
    
    def test_password_constraint(self):
        user = Registered_User(email="giorgio95@gmail.com", password="asd", username="gio95", registration_date=date(1995, 8, 2), birth_date=date(1985,3,1))
        with self.assertRaises(IntegrityError):
            user.save() # the password must be 8 characters long
        user.password="asdfghjklop"
        user.save()

    
class ArtistModelTest(TestCase):
    def setUp(self):
        self.artist = Artist(name= "George", surname= "Lucas")
    
    def test_str_method(self):
        self.assertEqual(str(self.artist), "George Lucas")
    
    def test_ep_directed(self):
        self.artist.save()
        self.studio = Studio.objects.create(name="HBO studios", hq_location="London, UK", studio_head = self.artist)
        self.franchise = Franchise.objects.create(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie.objects.create(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.episode = Episode.objects.create(number=1, title="pilot", season_num=1, serie=self.serie, studio=self.studio, director=self.artist, minutes_length=50, airing_date=date.today(), finale=0, ratings=None)

        self.assertEqual(self.artist.ep_directed.first(), self.episode)
    

class StudioModelTest(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="David", surname="Chase") # a studio needs an artist as studio_head
        self.studio = Studio.objects.create(name="Cinecittà", hq_location="Rome, Italy", studio_head= self.artist)
    
    def test_str_method(self):
        self.assertEqual(str(self.studio), "Cinecittà")

    def  test_ep_produced(self):
        self.franchise = Franchise.objects.create(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie.objects.create(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.episode = Episode.objects.create(number=1, title="pilot", season_num=1, serie=self.serie, studio=self.studio, director=self.artist, minutes_length=50, airing_date=date.today(), finale=0, ratings=None)

        self.assertEqual(self.studio.ep_produced.first(), self.episode)
    
    def test_on_delete(self):
        self.assertEqual(self.artist, self.studio.studio_head)
        self.artist.delete()
        # deleting the artist will cause the studio to be deleted because of ON DELETE CASCADE clause
        with self.assertRaises(Studio.DoesNotExist):
            Studio.objects.get(pk=self.studio.id)


class FranchiseModelTest(TransactionTestCase):
    def setUp(self):
        self.franchise = Franchise(name="Marvel's Avengers", rights_owner="Disney")

    def test_str_method(self):
        self.assertEqual(str(self.franchise), "Marvel's Avengers")

    def test_unique_constraint(self):
        self.franchise.save()
        franchise = Franchise(name="Marvel's Avengers", rights_owner="Warner Bros")
        with self.assertRaises(IntegrityError):
            franchise.save() # the name field must be unique
        franchise.name="Batman"
        franchise.save()


    def test_franchise_series(self):
        self.franchise.save()
        self.serie = Serie.objects.create(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.assertEqual(self.franchise.series.first(), self.serie)


class SerieModelTest(TransactionTestCase):
    def setUp(self):
        self.franchise = Franchise(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")

    def test_genre_field(self):
        self.assertEqual(self.serie.genre, Serie.GenreType.DRAMA)

    def test_classification_field(self):
        self.assertEqual(self.serie.classification, Serie.Classification.NOT_UNDER_14)

    def test_default_genre_field(self):
        serie = Serie(name="The Sopranos", franchise=self.franchise, classification="14+")
        self.assertEqual(serie.genre, Serie.GenreType.NOT_SPECIFIED)

    def test_default_classification_field(self):
        serie = Serie(name="The Sopranos", franchise= self.franchise, genre="DRM")
        self.assertEqual(serie.classification, Serie.Classification.EVERYONE)

    def test_unique_constraint(self):
        self.franchise.save()
        self.serie.save()
        serie = Serie(name="The Sopranos", franchise= self.franchise,genre="DRM", classification="14+")
        with self.assertRaises(IntegrityError):
            serie.save() # the name field must be unique
        serie.name = "Breaking Bad"
        serie.save()

    def test_str_method(self):
        self.assertEqual(str(self.serie), "The Sopranos")


class EpisodeModelTest(TransactionTestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name= "David", surname= "Chase")
        self.studio = Studio.objects.create(name="HBO studios", hq_location="London, UK", studio_head= self.artist)
        self.franchise = Franchise.objects.create(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie.objects.create(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.franchise.save()
        self.serie.save()
        self.episode= Episode(number=1, title="pilot", season_num=1, serie=self.serie, studio=self.studio, director=self.artist, minutes_length=50, airing_date=date.today(), finale=0, ratings=None)

    def test_unique_constraint(self):
        self.episode.save()
        self.assertTrue(self.episode, Episode.objects.get(pk=self.episode.id))
        episode = Episode(number=1, title="pilot2", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=None)
        with self.assertRaises(IntegrityError):
            episode.save()
        episode = Episode(number=2, title="pilot2", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=None)
        episode.save()
        self.assertTrue(episode, Episode.objects.get(pk=episode.id))

    def test_str_method(self):
        self.assertEqual(str(self.episode), "E1 S1 The Sopranos")

    def test_clean_method(self):
        self.episode.clean()
        #test date validation
        episode = Episode(number=1, title="pilot", season_num=1, serie=self.serie, studio=self.studio, director=self.artist, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=None)
        # the date can be changed as long as that model instance is not in the database
        episode.save()
        # the airing date cannot be changed once the episode is saved
        episode.airing_date = date(1999,1,2)
        with self.assertRaises(ValidationError):
            episode.clean()
        episode.delete()

        #test finale field validation
        self.episode.finale = 1
        self.episode.save() #update the episode
        episode = Episode(number=1, title="pilot2", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=1, ratings=None)
        with self.assertRaises(ValidationError):
            episode.clean()

    def test_save_method(self):
        self.episode.ratings = 9.99 #this value will be set to None when the model is saved
        self.episode.save()
        self.assertEqual(self.episode.ratings, None)

class UserFavSerieModelTest(TestCase):
    def setUp(self):
        self.user = Registered_User(email="ale95@gmail.com", password="asdfghjkl", username="ale95", registration_date=date(1995, 3, 19), birth_date=date(1985,3,1))
        self.franchise = Franchise(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.userfavorites = UserFavoriteSerie(user=self.user, serie=self.serie, added_date=date.today())

    def test_str_method(self):
        self.assertEquals(str(self.userfavorites), f"favorite of ale95: The Sopranos")
    
    def test_clean_method(self):
        self.userfavorites.clean()
        userfavorites = UserFavoriteSerie(user=self.user, serie=self.serie, added_date=date(1980,1,1))                
        with self.assertRaises(ValidationError):
            userfavorites.clean()


class UserWatchHistoryModelTest(TestCase):
    def setUp(self):
        self.user = Registered_User(email="ale95@gmail.com", password="asdfghjkl", username="ale95", registration_date=date(1995, 3, 19), birth_date=date(1985,3,1))
        self.franchise = Franchise(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.episode = episode = Episode(number=1, title="pilot", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=None)
        self.userwatchhistory = UserWatchHistory(user=self.user, episode=self.episode, watch_date=date.today())

    def test_clean_method(self):
        self.userwatchhistory.clean()

        user = Registered_User(email="ale95@gmail.com", password="asdfghjkl", username="ale95", registration_date=date(1997, 3, 19), birth_date=date(1985,3,1))
        userwatchhistory = UserWatchHistory(user=user, episode=self.episode, watch_date=date(2000,1,1))
        with self.assertRaises(ValidationError):
            userwatchhistory.clean()
        userwatchhistory.user = self.user
        userwatchhistory.watch_date = date(1978,1,1)
        with self.assertRaises(ValidationError):
            userwatchhistory.clean()
        userwatchhistory.watch_date = date(1998,1,1)
        with self.assertRaises(ValidationError):
            userwatchhistory.clean()

    def test_str_method(self):
        self.assertEqual(str(self.userwatchhistory), f"utente {self.user.id}: ale95 watched E1 S1 The Sopranos")
    

class UserReviewModelTest(TransactionTestCase):
    def setUp(self):
        self.user = Registered_User(email="ale95@gmail.com", password="asdfghjkl", username="ale95", registration_date=date(1995, 3, 19), birth_date=date(1985,3,1))
        self.franchise = Franchise(name="The Sopranos", rights_owner="HBO")
        self.serie = Serie(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.episode = episode = Episode(number=1, title="pilot", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=None)
        self.userreview = UserReview(user = self.user, episode= self.episode, vote="Positive")
        self.userwatchhistory = UserWatchHistory(user=self.user, episode=self.episode, watch_date=date.today())
        self.user.save()
        self.franchise.save()
        self.serie.save()
    
    def test_unique_constraint(self):
        self.episode.save()
        self.userwatchhistory.save()
        self.userreview.save()
        userreview = UserReview(user = self.user, episode= self.episode, vote="Positive")
        with self.assertRaises(IntegrityError):# the field couple (user, episode) must be unique
            userreview.save()
        user =Registered_User(email="al@gmail.com", password="iaasdfghjkl", username="al95", registration_date=date(1992, 5, 9), birth_date=date(1985,3,1))
        # for a different user or episode the review will be saved
        user.save() 
        userreview = UserReview(user = user, episode= self.episode, vote="Positive")
        userreview.save() 
        self.assertTrue(userreview, UserReview.objects.get(pk=userreview.id))
        episode = Episode(number=6, title="some_other_episode", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=None)
        episode.save()
        userreview = UserReview(user = self.user, episode= episode, vote="Positive")
        userreview.save()
        self.assertTrue(userreview, UserReview.objects.get(pk=userreview.id))

    def test_clean_method(self):
        self.episode.save()
        userreview = UserReview(user = self.user, episode= self.episode, vote="Positive")
        with self.assertRaises(ValidationError):
            self.userreview.clean()  
        self.userwatchhistory.save()
        self.userreview.clean()

    def test_str_method(self):
        self.assertEquals(str(self.userreview),"E1 S1 The Sopranos : Positive vote by ale95")

class PlaylistModelTest(TestCase):
    def setUp(self):
        self.user =Registered_User(email="ale95@gmail.com", password="asdfghjkl", username="ale95", registration_date=date(1995, 3, 19), birth_date=date(1985,3,1))
        self.playlist = Playlist(name="best episodes ever", user= self.user, creation_date=date.today())

    def test_str_method(self):
        self.assertEqual(str(self.playlist), "Playlist best episodes ever by ale95")

    def test_clean_method(self):
        self.playlist.creation_date = date(1975,3, 18)
        with self.assertRaises(ValidationError):
            self.playlist.clean() 

