# Generated by Django 4.2.16 on 2024-12-24 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('surname', models.CharField(max_length=25)),
                ('birth_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=50)),
                ('season_num', models.PositiveIntegerField()),
                ('minutes_length', models.PositiveIntegerField()),
                ('airing_date', models.DateField()),
                ('finale', models.BooleanField()),
                ('ratings', models.DecimalField(decimal_places=1, default='NULL', max_digits=3, null=True)),
                ('director', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='streamtv.artist')),
            ],
        ),
        migrations.CreateModel(
            name='Franchise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('rights_owner', models.CharField(max_length=50)),
                ('creation_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Registered_User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=128, unique=True)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('birth_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Serie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('genre', models.CharField(choices=[('MUS', 'Musical'), ('THR', 'Thriller'), ('COM', 'Comedy'), ('ACT', 'Action'), ('DRM', 'Drama'), ('HOR', 'Horror'), ('DOC', 'Documentary'), ('-', 'Not_specified')], default='-', max_length=3)),
                ('classification', models.CharField(choices=[('T', 'For_Everyone'), ('14+', 'Not_for_under_14'), ('18+', 'Mature_content')], default='T', max_length=3)),
                ('franchise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.franchise')),
            ],
        ),
        migrations.CreateModel(
            name='UserWatchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watch_date', models.DateField()),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.episode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.registered_user')),
            ],
        ),
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.CharField(choices=[('Positive', 'Positive vote'), ('Negative', 'Negative vote'), ('Unknown', 'Unknown')], default='Unknown', max_length=8)),
                ('comment', models.TextField(blank=True, max_length=250, null=True)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.episode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.registered_user')),
            ],
        ),
        migrations.CreateModel(
            name='UserFavoriteSerie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateField()),
                ('serie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.serie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.registered_user')),
            ],
        ),
        migrations.CreateModel(
            name='Studio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True)),
                ('hq_location', models.CharField(max_length=50, null=True)),
                ('founding_date', models.DateField()),
                ('studio_head', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='streamtv.artist', unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='registered_user',
            name='fav_series',
            field=models.ManyToManyField(through='streamtv.UserFavoriteSerie', to='streamtv.serie'),
        ),
        migrations.AddField(
            model_name='registered_user',
            name='followed_artists',
            field=models.ManyToManyField(blank=True, to='streamtv.artist'),
        ),
        migrations.AddField(
            model_name='registered_user',
            name='followed_studios',
            field=models.ManyToManyField(blank=True, to='streamtv.studio'),
        ),
        migrations.AddField(
            model_name='registered_user',
            name='reviews',
            field=models.ManyToManyField(related_name='user_review', through='streamtv.UserReview', to='streamtv.episode'),
        ),
        migrations.AddField(
            model_name='registered_user',
            name='watch_history',
            field=models.ManyToManyField(through='streamtv.UserWatchHistory', to='streamtv.episode'),
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('creation_date', models.DateField()),
                ('saved_episodes', models.ManyToManyField(to='streamtv.episode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.registered_user')),
            ],
        ),
        migrations.AddField(
            model_name='episode',
            name='serie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamtv.serie'),
        ),
        migrations.AddField(
            model_name='episode',
            name='studio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='streamtv.studio'),
        ),
        migrations.AddConstraint(
            model_name='userreview',
            constraint=models.UniqueConstraint(fields=('user', 'episode'), name='unique_episode_review_per_user'),
        ),
        migrations.AddConstraint(
            model_name='registered_user',
            constraint=models.CheckConstraint(check=models.Q(('password__length__gte', 8)), name='password_min_length'),
        ),
        migrations.AddConstraint(
            model_name='episode',
            constraint=models.UniqueConstraint(fields=('serie', 'season_num', 'number'), name='unique_episode_per_season_per_serie'),
        ),
    ]
