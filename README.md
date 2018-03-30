# Robit the slack bot #   
![Robit](robit.gif)
   
## Robit (the OBI bot) was created to do simple but useful everyday tasks ##   
Such as...   
**Quickly lookup a user role**   
**Server alerts**   
**Application load info**   
**Play a chat team game**   
   

## How to Use ##
![robit](robit.png)
   
**Uses Python 2.7**  

* Register on Slack for a BOT ID  
* Register on OWM (http://openweathermap.org/appid) for a free API ID  
* Add Slack BOT ID, BOT TOKEN, OWM API ID, and OBISITE as OS environment variables
* Install Oracle sqlplus, and setup TNSNAMES.ora file
* Create a .sql file with connection information

**Install third-party modules:**  
 
 `pip install slackclient`  
 `pip install schedule`  
 `pip install pyowm`   
 `pip install dataset`
 
**Install local database (SQlite)**  
http://www.sqlite.org

Create DB: `sqlite3 robit.db`  

Create table: `CREATE TABLE longrun ( id INTEGER PRIMARY KEY AUTOINCREMENT, presname text, user text, start_tm text, dashboard text, total_min integer );`  

**Slack developer kit:**  
https://github.com/slackapi/python-slackclient  
https://slackapi.github.io/python-slackclient

**Scheduler:**  
https://github.com/dbader/schedule  
https://schedule.readthedocs.io/en/stable

**PYOWM:**  
https://github.com/csparpa/pyowm  
https://pyowm.readthedocs.io/en/latest

**Dataset (Python DB manager):**  
http://dataset.readthedocs.io/en/latest


Run robit from command line  
`> python robit.py`

## Changes ##
Any changes and additions are welcome  
Recommended Python IDE -[**PyCharm**](https://www.jetbrains.com/pycharm/)

### Who do I talk to? ###

hewills