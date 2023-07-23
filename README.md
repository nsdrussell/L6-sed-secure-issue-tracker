# L6-sed-secure-issue-tracker

## deploy branch info
This branch is intended only for deploying to Heroku. As such, it has some minor differences from the main branch, including:
- The text of this readme file
- settings.py contains Heroku specific dependencies
- settings.py contains Heroku specific settings, such as using PostgreSQL instead of SQLite
- settings.py has Debug set to False
- .github\workflows contains djangodeploy.yml, which enables a GitHub action for deploying this branch directly to Heroku
- requirements.txt contains Heroku requirements

It is not intended that this branch should be run or hosted on a local machine, but only on Heroku.

It is hosted here:
https://nrussell-l6-sed-secure-webapp-13d5cac8c288.herokuapp.com/

## Help
To erase the database and create some example items in the database, on the homepage, click **Create Example Database Rows**.
This will seed the database with sample rows, including two user accounts, with which you can log in. The user account details are presented in Appendix B of the assignment text.
To view the help file, on the homepage, click **View Help**.
