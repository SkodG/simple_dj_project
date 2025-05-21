Hello there! 
This is a project I made for a University Course on Databases, it is a simple django backend web application that connects to mysql server, creates
an implementation of a Relational Database schema I designed for the Exam and performs CRUD operations with it using the Django ORM.

I also tried to implement a lot of Triggers but Django has limitations on thtat side, so I used a python script to set them in the db ('streamtv/script_create_triggers.py').

To run it you nedd to have installed MySQL server, python3, django and django-extensions on your system.

Once you cloned the repo, you need to create a MySQL database called 'stream_tv' (or any other name of your choice, make sure to modify it in the db_project/settings.py file of the app!) in MySQL, set a username, and a password for the django client and do the same in the settings.py file of the 'db_project/' directory, so that the django client can connect and perform operations on it.
Then use the command:  
`python3 manage.py makemigrations`
and 
`python3 manage.py migrate`
then you can perform CRUD operations with the django admin application, after you've logged in as an admin:
first create a super-user so you can login as admin:
`python3 manage.py createsuperuser`
Then run the local development server with:
`python3 manage.py runserver`
Then you can test the app and the triggers on the DB by running
`python3 manage.py test` this will run each python file that has "test" in the name. 
