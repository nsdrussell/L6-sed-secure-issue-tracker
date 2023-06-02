# L6-sed-secure-issue-tracker

## Installation Prerequisites
- Python 3.10.5
- Django 4.10

## Setup and running
1. Download the source code.
2. Open the directory /issuetracker/ within your IDE. If asked to install any packages, do so.
3. Within a terminal window, from the /issuetracker/ directory, run the following commands to create a database and run the app.
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
## Help
To erase the database and create some example items in the database, on the homepage, click **Create Example Database Rows**.
This will create two user accounts, with which you can log in. The user account details are presented in the Create Example Database Rows page.
To view the help file, on the homepage, click **View Help**.
