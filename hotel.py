import os
import time
from slackclient import SlackClient
import MySQLdb

hostname = 'localhost'
usernamesql = 'root'
passwordsql = 'nehanikki'
database = 'hotel'

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
#EXAMPLE_COMMAND = "how many rooms"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
myConnection = MySQLdb.connect( host=hostname, user=usernamesql, passwd=passwordsql, db=database )
cur = myConnection.cursor()

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    print command
    cmd = command.split(" ")
    count=len(cmd)
    #print count
    match=0
    list =""
    for i in range(0,count):
        print cmd[i]
        cur.execute("SELECT resp FROM Query WHERE req LIKE %s", ("%" + cmd[i] + "%",))   
        if cur.rowcount > 0: 
            if cmd[i] != "i" and cmd[i] != "a":
                #list.append(cmd[i])
                list+=str(cmd[i])
                #print list
                #match++
                #print match
            response = "matched"
        else:
            response = "Not sure what you mean. "  
    print list 

    if list=="howroomshotel":
        cur.execute("SELECT resp FROM Query WHERE req = %s", [list])
        res = cur.fetchall()
        for row in res:
            val = int(row[0])
            val = val - 1
            #val = str(val)
        cur.execute("UPDATE Query set resp = %s WHERE req = %s", [val,list])
    cur.execute("SELECT resp FROM Query WHERE req = %s", [list])
    result = cur.fetchall()
        #print query
        #cur.execute(query,("%" + cmd + "%"))
    if cur.rowcount == 0:
        response = "Not sure what you mean. "
    else:
        for row in result:
            response = row[0]
            print response

    #response = "Not sure what you mean. "
    #if command.startswith(EXAMPLE_COMMAND):
        #response = "Sure...write some more code then I can do that!"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
