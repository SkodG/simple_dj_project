from datetime import date
from django.test import TransactionTestCase, TestCase
from django.db.utils import IntegrityError, OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from streamtv.models import *
from streamtv.script_create_triggers import *
from decimal import Decimal

class triggerTest(TransactionTestCase):
    
    def setUp(self):
        #execute sql code with the cursor object
        with connection.cursor() as cursor:
            for procedure in crt_procedures:
                try:
                    cursor.execute(procedure)
                except OperationalError as Err:
                    print(Err)
            for trigger in crt_triggers:
                try:
                    cursor.execute(trigger)
                except OperationalError as Err:
                    print(Err) 
        # TODO Si potrebbe eseguire ciascun trigger nel test in cui si testa
        # Populate the database
        # Create and save users
        self.user1= Registered_User.objects.create(email="ale95@gmail.com", password="asdfghjkl", username="ale95", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user2= Registered_User.objects.create( email="a@gmail.com", password="43asdfghjkl", username="ale46", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user3= Registered_User.objects.create( email="ie5@gmail.com", password="a5g5sdfghjkl", username="legend", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user4= Registered_User.objects.create( email="alty@gmail.com", password="asdf78ghj3kl", username="awqdw", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user5= Registered_User.objects.create(email="pome95@gmail.com", password="asdfghh82jkl", username="alrfh4", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user6= Registered_User.objects.create(email="kjyt@gmail.com", password="asdfgtr5hjkl", username="arj", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user7= Registered_User.objects.create(email="rgtr@gmail.com", password="asdfghjkl34", username="aer5", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user8= Registered_User.objects.create(email="art9@gmail.com", password="asdfghxcrt4jkl", username="alefe", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user9= Registered_User.objects.create(email="pew95@gmail.com", password="ast65dfghjkl", username="alfr", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))
        self.user10= Registered_User.objects.create(email="nbv@gmail.com", password="argsdfghjkl", username="al", registration_date=date(1995, 3, 19), birth_date=date(1995,3,18))

        # Create and save an Episode, Serie and Franchise model instance
        self.franchise= Franchise.objects.create(name="The Sopranos", rights_owner="HBO")
        self.serie= Serie.objects.create(name="The Sopranos", franchise= self.franchise, genre="DRM", classification="14+")
        self.episode= Episode.objects.create(number=1, title="pilot", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=None)
        # Create and save a UserWatchHistory model instance for every user 
        UserWatchHistory.objects.create(user=self.user1, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user2, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user3, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user4, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user5, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user6, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user7, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user8, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user9, episode=self.episode, watch_date=date.today())
        UserWatchHistory.objects.create(user=self.user10, episode=self.episode, watch_date=date.today())


        # Create and save a UserReview model instance for every user and the same episode 
        self.review1= UserReview.objects.create(user=self.user1, episode=self.episode, vote="Negative")
        self.review2= UserReview.objects.create(user=self.user2, episode=self.episode, vote="Positive")
        self.review3= UserReview.objects.create(user=self.user3, episode=self.episode, vote="Positive")
        self.review4= UserReview.objects.create(user=self.user4, episode=self.episode, vote="Positive")
        self.review5= UserReview.objects.create(user=self.user5, episode=self.episode, vote="Positive")
        self.review6= UserReview.objects.create(user=self.user6, episode=self.episode, vote="Positive")
        self.review7= UserReview.objects.create(user=self.user7, episode=self.episode, vote="Positive")
        self.review8= UserReview.objects.create(user=self.user8, episode=self.episode, vote="Positive")
        self.review9= UserReview.objects.create(user=self.user9, episode=self.episode, vote="Positive")
        self.review10= UserReview.objects.create(user=self.user10, episode=self.episode, vote="Positive")
        # Create and save a UserFavorite instance
        self.fav_serie= UserFavoriteSerie.objects.create(user=self.user1, serie=self.serie, added_date=date.today())
        # Create and save a Playlist instance
        self.playlist = Playlist.objects.create(name="best episodes ever", creation_date=date.today(), user=self.user3)
        self.playlist.saved_episodes.add(self.episode)


    def test_db_triggers_reg_user(self):
        # Insert test
        new_user = Registered_User(email="giorgia99@gmail.com", password="i65hhjkl", username="gio99", registration_date=date(2080, 3, 19), birth_date=date(1995,3,18))
        # registration date < birth date
        with self.assertRaises(OperationalError):
            new_user.save()

        new_user.registration_date = date(2001,1,1)
        new_user.birth_date = date(2040,1,1) # birth date > today
        with self.assertRaises(OperationalError):
            new_user.save()
        
        # Update test
        new_user.birth_date = date(1999,1,1)
        new_user.save()
        new_user.username = "asdf" # fields other than date are updateable
        new_user.save()

        # updating the birth or registration date will result in an Error
        new_user.birth_date = date(1999,1,2)
        with self.assertRaises(OperationalError):
            new_user.save()

        new_user.birth_date = date(2999,1,1)
        with self.assertRaises(OperationalError):
            new_user.save()

        new_user.registration_date = date(2001,1,1)
        new_user.birth_date = date(2040,1,1)
        with self.assertRaises(OperationalError):
            new_user.save()

        new_user.delete() # to change a user birth date or registration date it needs to be deleted first
        new_user.birth_date = date(2000,12,4)
        new_user.save()

    def test_db_triggers_episode(self):
        # Testing ratings reset for episode with less than 10 reviews
        # Insert test
        episode = Episode.objects.create(number=2, title="pilot2", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=0, ratings=10)
        self.assertEqual(episode.ratings, None) # the ratings field is reset before insertion
        # Update test
        episode.ratings = 10
        episode.save()
        self.assertEqual(episode.ratings, None) # the ratings field is reset before update
        # Testing finale constraint
        # Insert test
        self.episode.finale=1
        self.episode.save() # a finale is already present in the database
        new_episode =Episode(number=3, title="not an episode", season_num=1, serie=self.serie, minutes_length=50, airing_date=date(1999,1,1), finale=1, ratings=None)
        with self.assertRaises(OperationalError):
            new_episode.save()

        # Update test
        # finale
        new_episode.finale=0
        new_episode.save()
        new_episode.finale=1
        with self.assertRaises(OperationalError):
            new_episode.save()

        # date
        # the airing date is not changeable
        new_episode.airing_date = date(2000,1,1)
        with self.assertRaises(OperationalError):
            new_episode.save()

    def test_db_triggers_review(self):
        reviewed_episode = Episode.objects.get(pk=self.episode.id)
        self.assertEqual(reviewed_episode.ratings, 9) # this episode has a rating of 9
        # Insert test
        # user
        new_user = Registered_User.objects.create(email="@mail", password="123456789", username="a", registration_date=date(1999,1,1), birth_date=date(1980,1,1))
        new_review = UserReview(user=new_user, episode= reviewed_episode, vote="Negative")
        with self.assertRaises(OperationalError): 
            new_review.save() # the user has not watched the episode

        new_watch_history= UserWatchHistory.objects.create(user=new_user, episode=reviewed_episode, watch_date=date.today()) 
        new_review.save() # now the review can be inserted in the database

        #Update test
        # user
        new_user_2 = Registered_User.objects.create(email="j@mail.com", password="0987654321", username="J", registration_date=date(1999,1,1), birth_date=date(1980,1,1))
        new_review.user =  new_user_2
        with self.assertRaises(OperationalError):
            new_review.save() 

        # Insert test
        # vote
        reviewed_episode = Episode.objects.get(pk=self.episode.id)
        r =  Decimal.from_float(round(9/11,2)*10)
        r = r.quantize(Decimal('1.0'))
        self.assertEqual(reviewed_episode.ratings, r) # the rating is calculated on 11 reviews now

        # Delete test
        # vote
        new_review.delete()
        self.review1.delete() # With < 10 votes the episode rating is set to Null
        reviewed_episode = Episode.objects.get(pk=self.episode.id)
        self.assertEqual(reviewed_episode.ratings, None)
        self.review1.save()
        reviewed_episode = Episode.objects.get(pk=self.episode.id) 
        self.assertEqual(reviewed_episode.ratings, 9) # the ratings is now the same as before

        # Update test
        # vote
        self.review1.vote= "Positive"
        self.review1.save()
        reviewed_episode = Episode.objects.get(pk=self.episode.id)
        self.assertEqual(reviewed_episode.ratings, 10)
    
    def test_db_triggers_fav_serie(self):
        # Insert test
        # date
        new_fav_serie = UserFavoriteSerie(user=self.user1, serie=self.serie, added_date=date(1994,1,1))
        with self.assertRaises(OperationalError):
            new_fav_serie.save() # the serie is added in a date that is < to the registration date of the user
        new_fav_serie.added_date = date(1996,1,1) 
        with self.assertRaises(OperationalError):
            new_fav_serie.save()
        
        # Update Test
        self.fav_serie.added_date = date(1994,1,1)
        with self.assertRaises(OperationalError):
            self.fav_serie.save()
        self.fav_serie.added_date = date(2080,1,1)
        with self.assertRaises(OperationalError):
            self.fav_serie.save()
 

    def test_db_triggers_watch_history(self):
        # Insert test
        # user
        new_user = Registered_User.objects.create(email="j@mail.it", username="JJ", password="ushdubfe", birth_date=date(2012,1,1), registration_date=date.today())
        new_user_watch_history = UserWatchHistory(user= new_user, watch_date=date.today(), episode= self.episode)
        with self.assertRaises(OperationalError):
            new_user_watch_history.save() # the episode classification is '14+' and the user is 13
        new_user.delete()
        new_user.birth_date=date(2009,1,1)
        new_user.save() # now the user is 16
        new_user_watch_history.user = new_user
        new_user_watch_history.save()
        # Update test
        # user
        new_user.delete() # the user's date are not updateable
        new_user.birth_date= date(2012,1,1)
        new_user.save()
        new_user_watch_history.user = new_user
        with self.assertRaises(OperationalError):
            new_user_watch_history.save()

        new_user.delete() 
        new_user.birth_date= date(2009,12,12)
        new_user.save() # now the user is 15
        new_user_watch_history.user = new_user
        new_user_watch_history.save()
        new_review = UserReview.objects.create(user=new_user, episode= self.episode, vote="Positive")
        self.assertEqual(new_review, UserReview.objects.get(pk=new_review.id))
        # update the watch history by changing the user
        new_user_watch_history.user = self.user1
        new_user_watch_history.save()
        # since new_user watched the episode only once changing the user that watched the episode
        # will cause the deletion of new_review by new_user for that episode
        with self.assertRaises(ObjectDoesNotExist):
            UserReview.objects.get(pk=new_review.id)

        new_user_watch_history.delete() #  setup for next test
        new_user_watch_history.user = new_user

        # Insert test
        # date
        new_user_watch_history.watch_date= date(2080,1,1)
        with self.assertRaises(OperationalError):
            new_user_watch_history.save()
            
        new_user_watch_history.watch_date = date(2024,12,31)
        with self.assertRaises(OperationalError):
            new_user_watch_history.save()

        new_user.delete()
        new_user.birth_date = date(1980,1,1)
        new_user.registration_date = date(1998,1,1)
        new_user.save()

        new_user_watch_history.user = new_user
        new_user_watch_history.watch_date = date(1998,1,1) 
        # the watch date can't precede the airing date of the episode
        with self.assertRaises(OperationalError):
            new_user_watch_history.save()
        new_user_watch_history.watch_date = date(2024,12,31)
        new_user_watch_history.save() # the user is old enough and the watch date is acceptable

        # Update test
        # date
        new_user_watch_history.watch_date= date(2080,1,1)
        with self.assertRaises(OperationalError):
            new_user_watch_history.save()

        new_user.delete()
        new_user.registration_date = date(2024,12,31)
        new_user.save()
        new_user_watch_history.user = new_user
        new_user_watch_history.watch_date = date(2024,12,31)

        # saving the instance with an acceptable date
        # then changing the date with a date that precedes the registration date 
        new_user_watch_history.watch_date = date(2022,12,31)
        with self.assertRaises(OperationalError):
            new_user_watch_history.save()

        new_user.delete()
        new_user.registration_date = date(1998,1,1)
        new_user.save()
        new_user_watch_history.user = new_user
        new_user_watch_history.watch_date = date(2024,12,31)
        new_user_watch_history.save()
        
        # the watch date canpt precede the airing date of the episode
        new_user_watch_history.watch_date = date(1998,1,1) 
        with self.assertRaises(OperationalError):
            new_user_watch_history.save()
        new_user_watch_history.watch_date = date(2000,12,1)
        new_user_watch_history.save()
        
        # Delete test
        # review
        review_to_delete = UserReview(user= new_user, episode= self.episode, vote="Positive")
        review_to_delete.save()
        self.assertEqual(review_to_delete, UserReview.objects.get(pk=review_to_delete.id))
        new_user_watch_history.delete() 
        # deleting the only record that the user watched the episode                          
        # will cause the review of that user for that episode to be deleted
        with self.assertRaises(ObjectDoesNotExist):
            review_to_delete = UserReview.objects.get(pk=review_to_delete.id)


    def test_db_triggers_playlist(self):
        # Insert Test
        # date
        new_playlist = Playlist(name="another playlist", creation_date=date(2080,1,1), user=self.user5)
        with self.assertRaises(OperationalError):
            new_playlist.save()
        new_playlist.creation_date = date(1950,6,21)
        with self.assertRaises(OperationalError):
            new_playlist.save()
        new_playlist.creation_date = date(1996,1,1)
        new_playlist.save()

        # Update Test
        # date
        self.playlist.creation_date = date(2080,1,1)
        with self.assertRaises(OperationalError):
            self.playlist.save()
        new_playlist.creation_date = date(1950,6,21)
        with self.assertRaises(OperationalError):
            self.playlist.save()

        self.playlist.creation_date = date(1996,1,1)
        self.playlist.save()
        # changing the user
        new_user = Registered_User.objects.create(email="g@mail.com", username="Gg", password="wsd45tg564g", birth_date= date(1990,1,1), registration_date=date(2000,1,1))
        self.playlist.user = new_user
        # the creation date precedes the registration date
        with self.assertRaises(OperationalError):
            self.playlist.save()
        #TODO trigger per impedire di aggiungere episodi futuri alla playlist?
