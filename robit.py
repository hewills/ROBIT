""""
Robit the OBI Slack bot
Created: 12/1/2017

slack bot designed for fun and small useful tasks.

"""
import os
import time
import logging
import schedule
import pyowm
import json
import random
import urllib
import datetime
import logit  # my custom logger
import dataset
from subprocess import Popen, PIPE
from slackclient import SlackClient

# Setup Logger (options: INFO, DEBUG, ERROR, WARNING, CRITICAL, LOGIT (Custom))
logging.basicConfig(level=logit.LOG_LEVEL_NUM)
logger = logging.getLogger(__name__)

logger.logit('Creating and initializing Bot')

# Robit's Slack BOT ID, BOT_TOKEN, and Weather API ID as environment variables
BOT_ID = os.environ.get("BOT_ID")
OWM_ID = os.environ.get("OWM_ID")
OBISITE = os.environ.get("OBISITE")

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# instantiate Open Weather Map object
# see http://openweathermap.org/appid to get free Weather API
owm = pyowm.OWM(OWM_ID)
logger.logit('Setting Weather API...')


# Load list of cities available in OWM (list downloaded from site)
# http://sustainablesources.com/resources/country-abbreviations/
# http://bulk.openweathermap.org/sample/city.list.json.gz
with open('city.list.json') as data_file:
    data = json.load(data_file)
    logger.debug('Number of cities available: %s', len(data))
    logger.debug('Data example= %s', data[0])

    # cities = {}
    # countryset = set()

    # for cities in data:
    # logger.logit('city=%s',cities)
    # for key, value in cities.items():
    # countryset.add(cities['country'])
    # logger.debug('List of countries= %s',countryset)
    # todo update countries in data with full name instead of abbreviations

# ---- End of Open Weather Map initialization

# Constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = ''
CHATROOM = <insert slack room ID>
ROBITSHOP =  <insert slack room ID>

logger.debug(slack_client.api_call("channels.list"))


# Functions to parse Slack output and handle commands  ------------------------
def handle_command(rb_command, rb_channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = ''
    rb_command = rb_command.lower()

    if rb_command.startswith(EXAMPLE_COMMAND):

        if 'pizza party' in rb_command:
            logger.logit('Running pizza party...')
            image_url = "https://s-media-cache-ak0.pinimg.com/originals/fd/41/e7/fd41e71fd21f6cd70dcab0c7d63666ef.gif"
            attachments = [{"title": "Pizza Party!", "image_url": image_url,"color": "#764FA5",
                            "text": "FUN FACT: National Pizza Party Day is the third Friday in May",
                            "color": "#e12301",
                            "footer": "Slices for all"
                            }]
            robitchat('', rb_channel, attachments)

        elif 'help' in rb_command:
            logger.logit('Running help...')
            response = "Send me commands with @robit. Here are the commands I know: \
            \n>  *pizza party* - I'll throw a pizza party! \
            \n>  *help* - You're looking at it \
            \n>  *user* _<username>_ - I'll show you OBI roles. Include _-all_ for BUS and DEPT \
            \n>  *stats* - See daily OBI report stats \
            \n>  *obi* - OBI status \
            \n>  *quiz* - Weather game (under construction)"

        # user command. Call function with parsed command list
        elif "user" in rb_command.split()[0]:
            logger.logit('Running user...')
            lookup_user(rb_command.split(), rb_channel)

        elif 'stats' in rb_command:
            logger.logit('Running stats...')
            runstats(rb_channel)

        elif 'quiz' in rb_command:
            logger.logit('Running quiz...')
            weatherquiz()

        elif 'obi' in rb_command:
            logger.logit('Running obi website_status...')
            website_status(rb_channel, OBISITE, 1)

        elif 'long' in rb_command:
            logger.logit('Running long running...')
            longrunning(rb_channel)

        # todo run usage tracking query to find long running queries
        # todo thread management !!!
        # todo Game using weather API or others
        # todo Balderdash type game (see http://phrontistery.info/ihlstart.html)

        else:
            # default response  todo: have random defaults available
            logger.logit('Running default...')
            response = "What? Does not compute. Try @robit help"

    # Send bot response to slack
    robitchat(response, rb_channel)


# ------------- End of HANDLE COMMANDS ---------------------------------------


# Lookup OBI roles for a user -------------------------------------------------
def lookup_user(f_commandlist, f_channel):
    """
       Command: user <username>  (-all [optional]) 
       Lookup an OBI role for a given username
       
       sysprod.sql contents:
          connect <user>/<password>@<host>
          SET NEWPAGE 0
          SET HEADING OFF  
    """
    # Check that command includes username
    if len(f_commandlist) > 1:
        # Parse command
        username = f_commandlist[1].strip().lower()
        option = ''
        sqlconnection = 'C:/Python27/sysprod.sql'

        robitchat('Looking up ' + username + '...', f_channel)
        logger.debug('f_commandlist = %s', f_commandlist)

        # if command includes an option
        if len(f_commandlist) > 2:
            option = f_commandlist[2].strip().lower()
            logger.debug('Option = %s', option)

        # -all option returns OBI roles, business units and department ids
        if '-all' in option:
            sqlcommand = 'SELECT DISTINCT DISPLAYNAME FROM schema.OBI_SEC WHERE USERNAME = \'' + username + '\';'
            # Connect (sqlConnection) and run command (sqlCommand). Return result into queryResults
            queryresult1, errormessage = runsqlquery(sqlcommand, sqlconnection)

            sqlcommand = 'SELECT OPRDEFNDESC FROM schema.OPRDEFN ' \
                         'WHERE OPRID = UPPER(\'' + username + '\');'
            queryresult2, errormessage = runsqlquery(sqlcommand, sqlconnection)

            queryresult = queryresult2 + queryresult1
            robitchat(queryresult, f_channel)

            sqlcommand = 'SELECT DISTINCT BUSINESS_UNIT FROM schema.SEC_BUNIT ' \
                         'WHERE lower(oprid) = \'' + username + '\';'
            queryresult, errormessage = runsqlquery(sqlcommand, sqlconnection)
            queryresult = 'Business units:\n' + queryresult

            sqlcommand = 'SELECT DISTINCT DEPTID FROM schema.SEC_DEPTID ' \
                         'WHERE lower(oprid) = \'' + username + '\';'
            queryresult2, errormessage = runsqlquery(sqlcommand, sqlconnection)
            queryresult2 = 'Dept IDs:\n' + queryresult2

            sqlcommand = 'SELECT FUND FROM schema.HUM_SPPI' \
                         'WHERE OPRID = UPPER(\'' + username + '\');'
            queryresult3, errormessage = runsqlquery(sqlcommand, sqlconnection)
            queryresult3 = 'PI Funds:\n' + queryresult3

            queryresult = queryresult + queryresult2 + queryresult3
            robitchat(queryresult, f_channel)

        # No option returns just OBI roles
        else:
            sqlcommand = 'SELECT DISTINCT DISPLAYNAME FROM schema.OBI_SEC ' \
                         'WHERE USERNAME = \'' + username + '\';'
            queryresult1, errormessage = runsqlquery(sqlcommand, sqlconnection)

            if errormessage:
                logger.info('Error running query - %s ', errormessage)
            logger.debug('queryResult = %s', queryresult1)

            sqlcommand = 'SELECT OPRDEFNDESC FROM schema.OPRDEFN ' \
                         'WHERE OPRID = UPPER(\'' + username + '\');'
            queryresult2, errormessage = runsqlquery(sqlcommand, sqlconnection)

            if queryresult2.strip() == 'no rows selected':
                queryresult2 = 'User not found. Possible test user.\n\n'

            queryresult = queryresult2 + queryresult1

            robitchat(queryresult, f_channel)
    else:
        robitchat('I need a username. Try @robit user <username>', f_channel)


# end of lookup_user ----------------------------------------------


def weatherquiz():
    """
           Play 'Guess the temperature' game in slack
           Robit uses weather API to challenge slackers
           
           data - dictionary of cities information
    """
    user = ''
    command = ''
    channel = ''

    if owm.is_API_online():
        logger.logit('Open Weather Map is online.')
    else:
        logger.logit('Open Weather Map is offline.')

    random.seed()  # uses current time to seed
    gameint = random.randint(0, len(data))  # get random index from city list

    logger.debug('Gameint = %s', gameint)
    city = data[gameint]  # get city's dictionary element

    # set observation object to selected game city
    obs = owm.weather_at_id(city['id'])
    w = obs.get_weather()

    logger.debug('MyDictEntry = %s', city)

    cityname = city['name']
    citycountry = city['country']
    citytemp = w.get_temperature('fahrenheit')['temp']

    text = "The Robit Weather Game! \n To play, just enter your guess in chat (ex. 50.5)\
            \n No need to type @robit. \
            \n Closest answer wins. You've got 60 seconds. Good luck! \
            \n\n What is the current temperature (" + unichr(176) + "F) in *" + cityname + "*, *" + citycountry + "*?"

    robitchat(text, ROBITSHOP)

    starttime = time.time()
    logger.logit('start=%s', starttime)

    while time.time() - starttime < 60:
        logger.debug('waiting...')

        user, command, channel = parse_user_output(slack_client.rtm_read())
        logger.debug("command=%s channel=%s", command, channel)

        # todo need logic to compile answers and save wins

    robitchat('The answer is ' + str(citytemp), ROBITSHOP)


def runstats(r_channel):
    """
           Scheduled function and command available from Slack
           Pull obi query counts by subject area, and max user counts, for the day
    """
    sqlconnection = 'C:/Python27/sysprod.sql'
    # Pull stats
    sqlcommand = 'select PRESENTATION_NAME,sum(NUM_DB_QUERY) from schema.NQ_ACCT where ' \
                 'START_DT = TO_DATE(trunc(sysdate),\'DD-MON-YY\') and ' \
                 'PRESENTATION_NAME is not null and USER_NAME NOT IN (\'tester\') ' \
                 'group by PRESENTATION_NAME;'

    # Connect (sqlConnection) and run command (sqlCommand). Return result into queryResults
    robitchat('It\'s OBI Stats Time, for ' + time.strftime("%m/%d/%Y") + '!', r_channel)
    queryresult, errormessage = runsqlquery(sqlcommand, sqlconnection)

    if errormessage:
        logger.info('Error running query - %s ', errormessage)
    logger.debug('queryResult = %s', queryresult)

    robitchat(queryresult, r_channel)

    sqlcommand = 'select count(distinct user_name) from schema.NQ_ACCT where ' \
                 'START_DT = TO_DATE(trunc(sysdate),\'DD-MON-YY\') ' \
                 'and USER_NAME NOT IN (\'tester\');'

    queryresult, errormessage = runsqlquery(sqlcommand, sqlconnection)

    if errormessage:
        logger.info('Error running query - %s ', errormessage)
    logger.debug('queryResult = %s', queryresult)

    robitchat('Max OBI user count, so far today: ' + queryresult, r_channel)

#This is still under construction
def longrunning():
    """
           Scheduled function available from Slack
           Checks for long running queries and returns info to Slack
    """

    #Connect to db and load long running query table
    db = dataset.connect('sqlite:///robit.db')
    longrun_tbl = db.load_table('longrun')
    res = longrun_tbl.all()

    for row in res:
        logger.logit("resrows=%s",(row['id'],row['presname'], row['user'],row['start_tm'],row['dashboard'],row['total_min']))

    sqlconnection = 'C:/Python27/sysprod.sql'

    sqlcommand = 'select PRESENTATION_NAME, USER_NAME, START_HOUR_MIN ' \
                 ', CASE (SAW_DASHBOARD || \'/\' || SAW_DASHBOARD_PG) WHEN \'/\' THEN SAW_SRC_PATH ' \
                 'ELSE SAW_DASHBOARD || \'/\' || SAW_DASHBOARD_PG END AS DASHBOARD ' \
                 ', ROUND(TOTAL_TIME_SEC/60,2) TOTAL_MIN ' \
                 'FROM schema.NQ_ACCT ' \
                 'WHERE USER_NAME NOT IN (\'tester\') ' \
                 'AND QUERY_SRC_CD IN (\'Report\') AND START_DT = TRUNC(SYSDATE-3) ' \
                 'AND TOTAL_TIME_SEC/60 > 2;'

    queryresult, errormessage = runsqlquery(sqlcommand, sqlconnection)

    #todo check for no rows selected

    logger.logit("query= %s",queryresult)

    rows = queryresult.split("\n")
    logger.logit("rows= %s", rows)

    for fields in rows:
        fields.split("\r")

    logger.logit("fields= %s",fields)
    field = []

    #put data in each field, into an array
    for data in fields:
        field.append(data.strip())

    logger.logit("field=%s",field)

    longrun_tbl.insert(dict(presname=field[0], user=field[1], start_tm=field[2], dashboard=field[3], total_min=field[4]))

    logger.logit ("Fields inserted into robit.db")

    if errormessage:
        logger.info('Error running query - %s ', errormessage)
    logger.debug('queryResult = %s', queryresult)

    #robitchat(queryresult, r_channel)


# Function takes a sqlCommand and connectString and returns the queryResult and errorMessage (if any)
def runsqlquery(sqlcmd, sqlconn):
    session = Popen(['sqlplus', '-S', '/NOLOG'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    logger.debug('Starting sqlplus...\n')

    logger.info("Connecting to DB using " + sqlconn + '\n')
    f = open(sqlconn, 'r')
    cmd = f.read()
    session.stdin.write(cmd + '\n')

    logger.debug("Running command - %s\n", sqlcmd)

    session.stdin.write(sqlcmd)
    result = session.communicate()

    return result


# end of runsqlquery ---------------------------------------------


# Robit chats in the given Slack channel (attachments optional) -------------------------------
def robitchat(r_text, r_channel, *attach):
    if attach:
        slack_client.api_call("chat.postMessage", channel=r_channel, text=r_text, as_user=True, attachments=attach[0])
    else:
        slack_client.api_call("chat.postMessage", channel=r_channel, text=r_text, as_user=True)

    return None


# -- end of robitchat -------------------------------------------

# Check website status. Sends alert to chat room if code 200 is not returned ------------
def website_status(r_channel, website, verbose):
    # If not verbose, only down status will alert the chat room
    # 0 is Monday, and 6 is Sunday
    if (datetime.datetime.today().weekday() in [0, 1, 2, 3, 4] and (
            dt.time() > datetime.time(07, 30) and dt.time() < datetime.time(17, 30))):
        try:
            myurl = urllib.urlopen('http://' + website).getcode()
        except IOError:
            myurl = 0

        if myurl != 200:
            robitchat('*ALERT* ' + website + ' may be down! *ALERT*', r_channel)
        elif myurl == 200 and verbose:
            robitchat('http://' + website + ' is up', r_channel)


# Parse ALL slack output, by User, and chatroom. Return text, user  -----------
def parse_user_output(slack_rtm_output):
            """
                The Slack Real Time Messaging API is an events fire hose.
                this parsing function returns None unless a message is
                posted, that doesn't belong to a Bot. Testing
            """
            # Capture chat output
            output_list = slack_rtm_output

            if output_list and len(output_list) > 0:
                #logger.logit('outputlist = %s',output_list)
                for output in output_list:
                    #logger.logit('output = %s', output)
                    if output and 'type' in output and output['type'] == 'message' and 'text' in output and 'bot_id' not in output:
                        # return text after the @ mention, whitespace removed
                        if isinstance(output['text'],(int)):
                            logger.logit('mynum=%s',int(output['text']))
                            return output['user'], output['text'], output['channel']

            return None, None, None


# end of parse_slack_output --------------------------------------

# PARSE OUTPUT in channel, and check if sent to robit  -----------
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events fire hose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    # Capture chat output
    output_list = slack_rtm_output
    logger.debug('Chat output List = %s', output_list)

    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                logger.debug('Robit command/channel = %s/%s', output['text'].split(AT_BOT)[1].strip().lower(),
                             output['channel'])
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']

    return None, None


# end of parse_slack_output --------------------------------------


# The code instantiates the SlackClient client with our SLACK_BOT_TOKEN exported as an environment variable.
# function 'handle_command' will determine what to do.
if __name__ == "__main__":

    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose

    logger.logit('Connecting to slack server...')

    """
       Job scheduler  - Add functions/tasks for Robit to run at given intervals
       Source: https://schedule.readthedocs.io/en/stable/
    """
    logger.logit('Scheduling jobs...')

    schedule.every().day.at("12:00").do(runstats, CHATROOM)
    schedule.every().day.at("16:45").do(runstats, CHATROOM)

    if datetime.datetime.today().weekday() in [0,1,2,3,4]: # Monday is 0 and Sunday is 6
        schedule.every(5).minutes.do(website_status,CHATROOM,OBISITE,0)

    longrunning()

    # End of Job Scheduler ------------------------------------------------------------------------------------

    # Slack loop until bot exited
    if slack_client.rtm_connect():
        print("ROBIT connected and running!")

        dt = datetime.datetime.now()

        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            logger.debug("command=%s channel=%s", command, channel)

            # Check for any scheduled tasks and run
            schedule.run_pending()

            if command and channel:
                handle_command(command, channel)

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

# ---------- END OF MAIN ----------------------------------------------
