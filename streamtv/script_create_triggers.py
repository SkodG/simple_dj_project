import MySQLdb
import mysql.connector

mydb = mysql.connector.connect( user='django_project',
                                host='localhost',
                                password='password123',
                                database='stream_tv')
crt_procedures = []
crt_triggers = []
### Implementazione Procedure ###
verifyAcceptableDate = """CREATE PROCEDURE `verifyAcceptableDate`(
                                IN dateToVerify DATE,
                                IN maxAcceptableDate DATE
                            )
                            BEGIN
                                IF dateToVerify > maxAcceptableDate  
                                    THEN SIGNAL SQLSTATE '45000'
                                    SET MESSAGE_TEXT = 'specified date is not acceptable';
                                 END IF;
                            END"""
crt_procedures.append(verifyAcceptableDate)

verifyUserWatchedEpisode = """CREATE PROCEDURE `verifyUserWatchedEpisode`(
                                        IN new_user_id INT,
                                        IN new_episode_id INT
                                )
                                 BEGIN
                                     DECLARE watchedEpisode INT;
                                     SELECT COUNT(episode_id)
                                     INTO watchedEpisode
                                     FROM streamtv_userwatchhistory 
                                     WHERE user_id = new_user_id 
                                        AND episode_id = new_episode_id;
                                     IF watchedEpisode < 1 
                                        THEN SIGNAL SQLSTATE '45000' 
                                        SET MESSAGE_TEXT = 'Users can review only watched episodes';
                                     END IF;
                                END"""
crt_procedures.append(verifyUserWatchedEpisode)

deleteUserReview = """CREATE PROCEDURE `deleteUserReview`(
                                 IN old_user_id INT,
                                 IN old_episode_id INT
                            )
                            BEGIN
                                DECLARE watchedEpisode INT;
                                SELECT COUNT(episode_id)
                                INTO watchedEpisode
                                FROM streamtv_userwatchhistory
                                WHERE user_id = old_user_id 
                                    AND episode_id = old_episode_id;
                                IF watchedEpisode < 1 
                                    THEN DELETE FROM streamtv_userreview 
                                    WHERE user_id = old_user_id 
                                    AND episode_id = old_episode_id;
                                END IF;
                            END"""
crt_procedures.append(deleteUserReview)

enforceContentRestriction = """CREATE PROCEDURE `enforceContentRestriction`(
                                        IN user_id INT,
                                        IN watch_date DATE, 
                                        IN episode_id INT
                                    )
                                    BEGIN 
                                        DECLARE user_age INT;
                                        DECLARE classification VARCHAR(3); 
                                        SELECT DATEDIFF(watch_date, birth_date) / 365.25 
                                        INTO user_age 
                                        FROM streamtv_registered_user 
                                        WHERE id = user_id;
                                        SELECT se.classification 
                                        INTO classification 
                                        FROM streamtv_episode AS ep 
                                        LEFT JOIN streamtv_serie AS se ON ep.serie_id = se.id 
                                        WHERE ep.id = episode_id; 
                                        IF (classification = '14+' AND user_age < 14) 
                                          OR (classification = '18+' AND user_age < 18)
                                            THEN SIGNAL SQLSTATE '45000' 
                                            SET MESSAGE_TEXT = 'User not old enough to see episode'; 
                                    END IF;
                                END"""
crt_procedures.append(enforceContentRestriction)


### Implementazione Trigger ###
# Comandi SQL utilizzati su più trigger
sql_trg_episode_ratings = """BEGIN
                                DECLARE tot_ratings, positive_ratings INT; 
                                SELECT COUNT(vote) 
                                INTO tot_ratings 
                                FROM streamtv_userreview 
                                WHERE (vote = 'Positive' OR vote = 'Negative') 
                                    AND episode_id = new.id; 
                                SELECT COUNT(vote) 
                                INTO positive_ratings 
                                FROM streamtv_userreview 
                                WHERE vote = 'Positive' 
                                    AND episode_id = new.id; 
                                IF tot_ratings >= 10 
                                    THEN SET new.ratings = (positive_ratings / tot_ratings)*10; 
                                ELSE 
                                    SET new.ratings = NULL; 
                                END IF; 
                            END"""

sql_trg_favorite_date = """BEGIN 
                               DECLARE userRegDate DATE;
                               DECLARE firstEpSerieDate DATE;
                               CALL verifyAcceptableDate(new.added_date, CURDATE()); 
                               SELECT registration_date 
                               INTO userRegDate 
                               FROM streamtv_registered_user
                               WHERE id = new.user_id; 
                               CALL verifyAcceptableDate(userRegDate, new.added_date);
                               SELECT MIN(airing_date)
                               INTO firstEpSerieDate
                               FROM streamtv_episode
                               WHERE serie_id = new.serie_id;
                               CALL verifyAcceptableDate(firstEpSerieDate, new.added_date);
                            END"""

sql_trg_playlist_date =   """BEGIN 
                                DECLARE userRegDate DATE; 
                                CALL verifyAcceptableDate(new.creation_date, CURDATE()); 
                                SELECT registration_date 
                                INTO userRegDate 
                                FROM streamtv_registered_user
                                WHERE id= new.user_id; 
                                CALL verifyAcceptableDate(userRegDate, new.creation_date);
                            END"""
 
sql_trg_userwatchhistory_user_id = """BEGIN
                                        CALL enforceContentRestriction(new.user_id, new.watch_date, new.episode_id);
                                      END"""

sql_trg_userwatchhistory_date = """BEGIN
                                       DECLARE userRegDate DATE;
                                       DECLARE episodeDate DATE;
                                       CALL verifyAcceptableDate(new.watch_date, CURDATE());
                                       SELECT registration_date
                                       INTO userRegDate
                                       FROM streamtv_registered_user
                                       WHERE id = new.user_id;
                                       CALL verifyAcceptableDate(userRegDate, new.watch_date); 
                                       SELECT airing_date
                                       INTO episodeDate
                                       FROM streamtv_episode
                                       WHERE id = new.episode_id;
                                       CALL verifyAcceptableDate(episodeDate, new.watch_date);
                                   END"""

sql_trg_episode_finale = """BEGIN 
                                DECLARE countFinale BOOL; 
                                SELECT COUNT(finale) 
                                INTO countFinale 
                                FROM streamtv_episode 
                                WHERE finale = TRUE 
                                AND serie_id = new.serie_id 
                                AND season_num = new.season_num;
                                IF (countFinale > 0 
                                  AND new.finale = TRUE) 
                                    THEN SIGNAL SQLSTATE '45000' 
                                    SET MESSAGE_TEXT = 'Only one finale per season is allowed'; 
                                END IF; 
                            END"""
sql_trg_userwatchhistory_userreview = """BEGIN 
                                            CALL deleteUserReview(old.user_id, old.episode_id); 
                                         END"""


crt_triggers = []
before_episode_ratings_insert = """CREATE TRIGGER before_episode_ratings_insert 
                                        BEFORE INSERT 
                                        ON streamtv_episode 
                                        FOR EACH ROW """+ sql_trg_episode_ratings
crt_triggers.append(before_episode_ratings_insert)
#
before_episode_finale_insert = """CREATE TRIGGER before_episode_finale_insert 
                                        BEFORE INSERT 
                                        ON streamtv_episode 
                                        FOR EACH ROW """ + sql_trg_episode_finale 

crt_triggers.append(before_episode_finale_insert)
#

before_episode_ratings_update = """CREATE TRIGGER before_episode_ratings_update 
                                        BEFORE UPDATE 
                                        ON streamtv_episode 
                                        FOR EACH ROW """+ sql_trg_episode_ratings
crt_triggers.append(before_episode_ratings_update)
#
before_episode_finale_update = """CREATE TRIGGER before_episode_finale_update 
                                        BEFORE UPDATE 
                                        ON streamtv_episode 
                                        FOR EACH ROW 
                                        BEGIN 
                                            DECLARE countFinale BOOL; 
                                            SELECT COUNT(finale) 
                                            INTO countFinale 
                                            FROM streamtv_episode 
                                            WHERE finale = TRUE 
                                                AND serie_id = new.serie_id 
                                                AND season_num = new.season_num; 
                                            IF (countFinale > 0 
                                              AND old.finale < new.finale) 
                                                THEN SIGNAL SQLSTATE '45000' 
                                                SET MESSAGE_TEXT = 'Only one finale per season is allowed'; 
                                            END IF; 
                                        END"""
crt_triggers.append(before_episode_finale_update)
#
before_episode_date_update = """CREATE TRIGGER before_episode_date_update
                                 BEFORE UPDATE
                                 ON streamtv_episode
                                 FOR EACH ROW
                                 BEGIN
                                    IF old.airing_date <> new.airing_date
                                        THEN SIGNAL SQLSTATE '45000'
                                        SET MESSAGE_TEXT = 'The airing date of an episode is not changeable';
                                    END IF;
                                 END"""
crt_triggers.append(before_episode_date_update)

before_playlist_date_insert = """CREATE TRIGGER before_playlist_date_insert 
                                    BEFORE INSERT
                                    ON streamtv_playlist
                                    FOR EACH ROW """ + sql_trg_playlist_date

crt_triggers.append(before_playlist_date_insert)
#
before_playlist_date_update = """CREATE TRIGGER before_playlist_date_update 
                                    BEFORE UPDATE 
                                    ON streamtv_playlist
                                    FOR EACH ROW """+ sql_trg_playlist_date
crt_triggers.append(before_playlist_date_update)
#
before_playlist_episode_date_insert = """CREATE TRIGGER before_playlist_episode_date_insert
                                         BEFORE INSERT
                                         ON streamtv_playlist_saved_episodes
                                         FOR EACH ROW
                                         BEGIN
                                            DECLARE episodeDate DATE;
                                            SELECT airing_date
                                            INTO episodeDate
                                            FROM streamtv_episode
                                            WHERE id = new.episode_id;
                                            CALL verifyAcceptableDate(episodeDate, CURDATE());
                                         END"""
crt_triggers.append(before_playlist_episode_date_insert)

before_registered_user_date_insert = """CREATE TRIGGER before_registered_user_date_insert 
                                            BEFORE INSERT 
                                            ON streamtv_registered_user 
                                            FOR EACH ROW 
                                            BEGIN 
                                                CALL verifyAcceptableDate(new.birth_date, CURDATE());
                                                CALL verifyAcceptableDate(new.registration_date, CURDATE());
                                                CALL verifyAcceptableDate(new.birth_date, new.registration_date);
                                            END"""
crt_triggers.append(before_registered_user_date_insert)
#
before_registered_user_date_update = """CREATE TRIGGER before_registered_user_date_update 
                                            BEFORE UPDATE 
                                            ON streamtv_registered_user 
                                            FOR EACH ROW 
                                            BEGIN 
                                                IF (old.birth_date <> new.birth_date 
                                                  OR old.registration_date <> new.registration_date)
                                                    THEN SIGNAL SQLSTATE '45000'
                                                    SET MESSAGE_TEXT = 'user birth date and registration date cannot be changed';
                                                END IF;
                                            END """
crt_triggers.append(before_registered_user_date_update)
#
before_userfavoriteserie_date_insert = """CREATE TRIGGER before_userfavoriteserie_date_insert 
                                                BEFORE INSERT
                                                ON streamtv_userfavoriteserie
                                                FOR EACH ROW """+ sql_trg_favorite_date 
                                                
crt_triggers.append(before_userfavoriteserie_date_insert)
#
before_userfavoriteserie_date_update = """CREATE TRIGGER before_userfavoriteserie_date_update 
                                                BEFORE UPDATE
                                                ON streamtv_userfavoriteserie
                                                FOR EACH ROW """ + sql_trg_favorite_date 
crt_triggers.append(before_userfavoriteserie_date_update)
#
before_userreview_insert = """CREATE TRIGGER before_userreview_insert 
                                    BEFORE INSERT 
                                    ON streamtv_userreview 
                                    FOR EACH ROW 
                                    BEGIN 
                                        CALL verifyUserWatchedEpisode(new.user_id, new.episode_id); 
                                    END """
crt_triggers.append(before_userreview_insert)
#
after_userreview_vote_insert = """CREATE TRIGGER after_userreview_vote_insert 
                                        AFTER INSERT 
                                        ON streamtv_userreview 
                                        FOR EACH ROW 
                                        BEGIN 
                                            DECLARE tot_ratings, positive_ratings VARCHAR(8); 
                                            SELECT COUNT(vote)
                                            INTO tot_ratings 
                                            FROM streamtv_userreview 
                                            WHERE (vote = 'Positive' OR vote = 'Negative') 
                                              AND episode_id = new.episode_id; 
                                            SELECT COUNT(vote) 
                                            INTO positive_ratings 
                                            FROM streamtv_userreview 
                                            WHERE vote = 'Positive' 
                                              AND episode_id = new.episode_id; 
                                            IF tot_ratings >= 10 
                                                THEN UPDATE streamtv_episode 
                                                SET ratings = (positive_ratings / tot_ratings)*10 
                                                WHERE id = new.episode_id; 
                                            ELSE 
                                                UPDATE streamtv_episode SET ratings = NULL 
                                                WHERE id = new.episode_id; 
                                            END IF;
                                        END """
crt_triggers.append(after_userreview_vote_insert)
#
before_userreview_update = """CREATE TRIGGER before_userreview_update 
                                    BEFORE UPDATE 
                                    ON streamtv_userreview 
                                    FOR EACH ROW 
                                    BEGIN 
                                        CALL verifyUserWatchedEpisode(new.user_id, new.episode_id); 
                                    END """
crt_triggers.append(before_userreview_update)
#
after_userreview_vote_update = """CREATE TRIGGER after_userreview_vote_update 
                                        AFTER UPDATE 
                                        ON streamtv_userreview 
                                        FOR EACH ROW 
                                        BEGIN 
                                            DECLARE tot_ratings, positive_ratings VARCHAR(8); 
                                            SELECT COUNT(vote) 
                                            INTO tot_ratings 
                                            FROM streamtv_userreview 
                                            WHERE (vote = 'Positive' OR vote = 'Negative') 
                                              AND episode_id = new.episode_id; 
                                            SELECT COUNT(vote) 
                                            INTO positive_ratings 
                                            FROM streamtv_userreview 
                                            WHERE vote = 'Positive' AND episode_id = new.episode_id; 
                                            IF tot_ratings >= 10 
                                                THEN UPDATE streamtv_episode 
                                                SET ratings = (positive_ratings / tot_ratings)*10 
                                                WHERE id = new.episode_id; 
                                            ELSE 
                                                UPDATE streamtv_episode SET ratings = NULL 
                                                WHERE id = new.episode_id; 
                                            END IF; 
                                        END """
crt_triggers.append(after_userreview_vote_update)
#
after_userreview_vote_delete = """CREATE TRIGGER after_userreview_vote_delete 
                                        AFTER DELETE 
                                        ON streamtv_userreview 
                                        FOR EACH ROW 
                                        BEGIN 
                                            DECLARE tot_ratings, positive_ratings VARCHAR(8); 
                                            SELECT COUNT(vote) 
                                            INTO tot_ratings 
                                            FROM streamtv_userreview 
                                            WHERE (vote = 'Positive' OR vote = 'Negative') 
                                              AND episode_id = old.episode_id; 
                                            SELECT COUNT(vote) 
                                            INTO positive_ratings 
                                            FROM streamtv_userreview 
                                            WHERE vote = 'Positive' 
                                              AND episode_id = old.episode_id; 
                                            IF tot_ratings >= 10 
                                                THEN UPDATE streamtv_episode 
                                                SET ratings = (positive_ratings / tot_ratings)*10 
                                                WHERE id = old.episode_id; 
                                            ELSE 
                                                UPDATE streamtv_episode 
                                                SET ratings = NULL 
                                                WHERE id = old.episode_id; 
                                            END IF; 
                                         END"""
crt_triggers.append(after_userreview_vote_delete)
#
before_userwatchhistory_user_id_insert = """CREATE TRIGGER before_userwatchhistory_user_id_insert 
                                                BEFORE INSERT 
                                                ON streamtv_userwatchhistory 
                                                FOR EACH ROW """ + sql_trg_userwatchhistory_user_id 
crt_triggers.append(before_userwatchhistory_user_id_insert)
#
before_userwatchhistory_date_insert = """CREATE TRIGGER before_userwatchhistory_date_insert 
                                             BEFORE INSERT 
                                             ON streamtv_userwatchhistory 
                                             FOR EACH ROW """ + sql_trg_userwatchhistory_date 

crt_triggers.append(before_userwatchhistory_date_insert)
#
before_userwatchhistory_user_id_update = """CREATE TRIGGER before_userwatchhistory_user_id_update 
                                                BEFORE UPDATE 
                                                ON streamtv_userwatchhistory 
                                                FOR EACH ROW """ + sql_trg_userwatchhistory_user_id 
crt_triggers.append(before_userwatchhistory_user_id_update)
#
before_userwatchhistory_date_update = """CREATE TRIGGER before_userwatchhistory_date_update 
                                             BEFORE UPDATE 
                                             ON streamtv_userwatchhistory 
                                             FOR EACH ROW """+ sql_trg_userwatchhistory_date 

crt_triggers.append(before_userwatchhistory_date_update)
#
after_userwatchhistory_user_id_update = """CREATE TRIGGER after_userwatchhistory_user_id_update 
                                                AFTER UPDATE 
                                                ON streamtv_userwatchhistory 
                                                FOR EACH ROW """ + sql_trg_userwatchhistory_userreview 
crt_triggers.append(after_userwatchhistory_user_id_update)
#
after_userwatchhistory_userreview_delete = """CREATE TRIGGER after_userwatchhistory_userreview_delete 
                                                    AFTER DELETE 
                                                    ON streamtv_userwatchhistory 
                                                    FOR EACH ROW """ + sql_trg_userwatchhistory_userreview 
crt_triggers.append(after_userwatchhistory_userreview_delete)
#

### Creazione di Procedure e Trigger nel DB
def call_script():
    mycursor = mydb.cursor()
    for procedure in crt_procedures:
        try:
            mycursor.execute(procedure)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    for trigger in crt_triggers:
        try:
            mycursor.execute(trigger)
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    mycursor.close()

if __name__ == '__main__':
    call_script()

