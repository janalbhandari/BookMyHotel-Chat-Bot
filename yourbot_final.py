import os
import time
from slackclient import SlackClient
import re 
import MySQLdb
# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"


hostname = 'localhost'
usernamesql = 'root'
passwordsql = 'nehanikki'
database = 'hotelbot'
myConnection = MySQLdb.connect( host=hostname, user=usernamesql, passwd=passwordsql, db=database )
cur = myConnection.cursor()

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


#constants
NUMBER_OF_SUITES = 10
NUMBER_OF_DELUXE =10
NUMBER_OF_FAMILY =10

COST_OF_DELUXE=600
COST_OF_SUITES=800
COST_OF_FAMILY=700

def getlistbook(command,channel):
       lst = []
       s=re.search("suite",command)
       d = re.search("deluxe",command)
       f= re.search("family",command)
       a = re.search("all",command)
       if (s != None) or (a!=None):
          lst.append("suite")
       if (d != None) or (a!=None):
          lst.append("deluxe")
       if (f != None) or (a != None):
          lst.append("family")
       return lst

def getchange(command,channel):
    lst =[]
    n = re.search("number",command)
    if (n != None):
         n = search("day",command)
         r = search("room",command)
         if (n != None ): lst.append("numdays")
         if (r != None): lst.append("numrooms")
    else :
        d = search("day",command)
        dt = search("date",command)
        if (d != None or dt != None): lst.append("date")
    t = re.search("type",command)
    if ( t != None): lst.append("type")
    return lst
  
def getlistcncl(command,channel):
       lst = []
       s=re.search("suite",command)
       d = re.search("deluxe",command)
       f= re.search("family",command)
       #a = re.search("all",command)
       if (s != None):
          #count=1
          lst.append("suite")
       if (d != None):
          #count = count+1
          lst.append("deluxe")
       if (f != None):
          #count = count+1
          lst.append("family")
       return lst

def cancelroom(roomtype,command,channel,name):
    cur.execute("SELECT * from bookingdetails where user = %s and roomtype = %s",[name,roomtype])
    for row in cur.fetchall():
      name = row[0]
      roomtype = row[1]
      nums = row[2]
      date = row[3]
      cost = row[5]
      days = row[6]
    response = "I understand that you have booking for  "+str(nums) +" " +roomtype+ "rooms in the name of "+name+", from "+date+" for " + str(days)+" days.The Billing Amount is $"+str(cost)+" .Please confirm the cancellation with y/n"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
    command, channel = parse_slack_output(slack_client.rtm_read())
    while (command==None) and (channel==None):
      command, channel = parse_slack_output(slack_client.rtm_read())
    command = command.lower()
    m = re.search("y",command)
    if(m!=None):
      cur.execute("delete from bookingdetails where user = %s and roomtype = %s",[name,roomtype])
      myConnection.commit()
      response = "Your cancellation is confirmed. Your amount will be refunded with a deduction of $100 with next 24hrs.Thanks for choosing BookMyHotel.Have a Nice Day!Bye!"
      slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
      return;
    else:
      m = re.search("n",command)
      if (m!=None):
        response = "I understand that you have not confirmed your cancellation.Your booking is still confirmed with us.Thanks for choosing BookMyHotel.Have a Nice Day!Bye!"
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
        return;
      else:
        response = "Sorry! You didn't answer my question right. I ll repeat!"
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def cancelall(command,channel,name):
    cur.execute("SELECT * from bookingdetails where user = %s",[name])
    for row in cur.fetchall():
      name = row[0]
      roomtype = row[1]
      nums = row[2]
      date = row[3]
      cost = row[5]
      days = row[6]
    response = "I understand that you have multilple bookings..Please confirm the cancellation of all with y/n"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
    command, channel = parse_slack_output(slack_client.rtm_read())
    while (command==None) and (channel==None):
      command, channel = parse_slack_output(slack_client.rtm_read())
    command = command.lower()
    m = re.search("y",command)
    if(m!=None):
      cur.execute("delete from bookingdetails where user = %s",[name])
      myConnection.commit()
      response = "Your cancellation is confirmed. Your amount will be refunded with a deduction of $100 within next 24hrs.Thanks for choosing BookMyHotel.Have a Nice Day!Bye!"
      slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
      return;
    else:
      m = re.search("n",command)
      if (m!=None):
        response = "I understand that you have not confirmed your cancellation.Your booking is still confirmed with us.Thanks for choosing BookMyHotel.Have a Nice Day!Bye!"
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
        return;
      else:
        response = "Sorry! You didn't answer my question right. I ll repeat!"
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def change(command, channel):
  print("Change")
  response = "I understand that you want to make changes to your booking. Please provide the booking name for the change process"
  slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
  command, channel = parse_slack_output(slack_client.rtm_read())
  while (command==None) and (channel==None):
    command, channel = parse_slack_output(slack_client.rtm_read())
  name = command.lower()
  lst=[]
  cur.execute("select * from bookingdetails where user = %s",[name])
  if (cur.rowcount==0):
     response = "We don't have any bookings in the name of %s. Thank you!" % command
     slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)
     return;
  for row in cur.fetchall():
    roomtype = row[1]
    print roomtype
    lst.append(roomtype)
  print lst
  if (len(lst) >1 ):
    response = "I understand that you have booking for "+str(len(lst))+ " types of rooms. Lets do the changes to one by one."
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
  for roomtype in lst:
    changeroom(roomtype,command,channel,name)
  return

# def changeroomtype(roomtype,command,channel,name):
#    while True:
#     response = "Do you want to change the roomtype instead of  "+ roomtype+" room? Answer with Y/N"
#     slack_client.api_call("chat.postMessage", channel=channel,
#                           text=response, as_user=True)
#     command, channel = parse_slack_output(slack_client.rtm_read())
#     while (command==None) and (channel==None):
#          command, channel = parse_slack_output(slack_client.rtm_read())
#     command = command.lower()
#     y = re.search("y",command)
#     n = re.search("n",command)
#     if (y!=None):
#          response = " Please specify the room type to be changed to instead of  "+ roomtype+" room? "
#          slack_client.api_call("chat.postMessage", channel=channel,
#                            text=response, as_user=True)
#          command, channel = parse_slack_output(slack_client.rtm_read())
#          while (command==None) and (channel==None):
#               command, channel = parse_slack_output(slack_client.rtm_read())
#          command = command.lower()
         

#          if command == roomtype :
#               response = "The room type to be changed is same as the booking.Let me ask you again"
#               slack_client.api_call("chat.postMessage", channel=channel,
#                            text=response, as_user=True)
#          #make the change to the for roomtype (out of: above if statement
#          response = "Arrival date is changed"
#          slack_client.api_call("chat.postMessage", channel=channel,
#                            text=response, as_user=True)
#          return
#     else if (n != None):  return
#     else :
#          response = "Sorry! I donot understand what you are saying. Let me ask you again."

def changedate(roomtype,command,channel,name):
  while True:
    response = "Do you want to change the arrival date for "+ roomtype+" room? Answer with Y/N"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
    command, channel = parse_slack_output(slack_client.rtm_read())
    while (command==None) and (channel==None):
         command, channel = parse_slack_output(slack_client.rtm_read())
    command = command.lower()
    y = re.search("y",command)
    n = re.search("n",command)
    if (y!=None):
         response = " Please specify the new arrival date for "+ roomtype+" room?"
         slack_client.api_call("chat.postMessage", channel=channel,
                           text=response, as_user=True)
         command, channel = parse_slack_output(slack_client.rtm_read())
         while (command==None) and (channel==None):
              command, channel = parse_slack_output(slack_client.rtm_read())
         command = command.lower()
         lst = []
         cur.execute("update bookingdetails set checkin=%s where user=%s and roomtype=%s",[command,name,roomtype])
         myConnection.commit()
         #make the change to arrival date 
         response = "Arrival date is changed"
         slack_client.api_call("chat.postMessage", channel=channel,
                           text=response, as_user=True)
         return
    elif (n != None):  
      return
    else :
         response = "Sorry! I donot understand what you are saying. Let me ask you again."

def changeroom(roomtype,command,channel,name):
    response = "Below is the booking details for your room type : "+roomtype
    #display booking details for that particular room type
    changedate(roomtype,command,channel,name)
    #changeroomtype(roomtype,command,channel,name)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
   
    response = "Hello! How can I help you today?"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
    command, channel = parse_slack_output(slack_client.rtm_read())
    while (command==None) and (channel==None):
         command, channel = parse_slack_output(slack_client.rtm_read())
    command = command.lower()
    m = re.search("cancel",command)
    if (m != None):
         cancel(command, channel)
    else:
        m= re.search("change", command)
        if(m!= None):
            change(command, channel)
        else:
            m= re.search("book", command)
            if (m != None):
                book(command,channel)
            else:
                response = "Sorry! I don't understand what you are saying"
                slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

             
    return 
             

def cancel(command,channel):
    response = "Please tell me the booking name"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
    command, channel = parse_slack_output(slack_client.rtm_read())
    while (command==None) and (channel==None):
         command, channel = parse_slack_output(slack_client.rtm_read())
    command = command.lower()
    usrname = command;
    cur.execute("SELECT * FROM bookingdetails where  user = %s",[command])
    if cur.rowcount == 0:
      response = "We don't have any bookings in the name of %s. Thank you!" % command
      slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)
      return;
    elif cur.rowcount == 1:
      for row in cur.fetchall():
        name = row[0]
        roomtype = row[1]
        nums = row[2]
        date = row[3]
        cost = row[5]
        days = row[6]
    else:
      response = "You have rooms booked for the following roomtypes. Please confirm which roomtype to cancel"
      slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)
      cur.execute("SELECT user,roomtype from bookingdetails where user = %s",[command])
      for res in cur.fetchall():
        name = res[0]
        response = res[1]
        slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)
      command, channel = parse_slack_output(slack_client.rtm_read())
      while (command==None) and (channel==None):
        command, channel = parse_slack_output(slack_client.rtm_read())
      command = command.lower()
      lst = getlistcncl(command,channel)
      cncl1 = re.search("entire",command)
      cncl2 = re.search("all",command)
      cncl3 = re.search("both",command)
      if ((cncl1 != None) or (cncl2 != None) or (cncl3 != None)):
        cancelall(command,channel,usrname)
      if (len(lst) >0):
        if len(lst)>1 :
          response = "I understand that you want to book "+ str(len(lst))+" types of rooms.Lets book one by one"
          slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
        for roomtype in lst:
          cancelroom(roomtype,command,channel,usrname)
        return
      else :
        response = "Sorry! I dont understand what you are saying. Let me ask you again"
        slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
      #print command
    return 

def book(command,channel):           
    print("book")
    print(command)
    lst = getlistbook(command,channel)
    
    if (len(lst) != 0):
        if len(lst)>1 :
           response = "I understand that you want to book "+ str(len(lst))+" types of rooms.Lets book one by one"
           slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
        for roomtype in lst:
            bookroom(roomtype,command,channel)   
        return 
    else :
           while True:
               response = "What type of room do you want to book? Deluxe, Suite or family?"
               slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
               command, channel = parse_slack_output(slack_client.rtm_read())
               while (command==None) and (channel==None):
                      command, channel = parse_slack_output(slack_client.rtm_read())
               command = command.lower()
               lst = getlistbook(command,channel)
               if (len(lst) >0):
                    if len(lst)>1 :
                         response = "I understand that you want to book "+ str(len(lst))+" types of rooms.Lets book one by one"
                         slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
                    for roomtype in lst:
                          bookroom(roomtype,command,channel)
                    return
               else :
                    response = "Sorry! I dont understand what you are saying. Let me ask you again"
                    slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)

               
    return

def bookroom(roomtype,command,channel):
  print("In book room function")
  while True :
    response = "I understand that you want to book "+roomtype+" room.Please confirm with Y/N"
    slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
    command, channel = parse_slack_output(slack_client.rtm_read())
    while (command==None) and (channel==None):
             command, channel = parse_slack_output(slack_client.rtm_read())
    command = command.lower()
    m = re.search("y",command)
    if (m!=None):    #confrim type 
        response = "How many "+roomtype+" rooms do you want to book? "
        slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
        command, channel = parse_slack_output(slack_client.rtm_read())
        while (command==None) and (channel==None):
              command, channel = parse_slack_output(slack_client.rtm_read())
        command = command.lower()
        nums = int(filter((lambda x :x.isdigit()),command))
        response ="I understand that you want to book " + str(nums) + " " + roomtype +"rooms"
        slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
        check = get_cost(roomtype,0,nums)
        if check=="error":
            response = "Sorry we dont have"+str(nums)+" " +roomtype+" rooms."
            slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
            return
        response = "Please type just  the booking name"
        slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
        command, channel = parse_slack_output(slack_client.rtm_read())
        while (command==None) and (channel==None):
             command, channel = parse_slack_output(slack_client.rtm_read())
        name = command;
        command = command.lower()
        response = "Please type the arrival date "
        slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
        command, channel = parse_slack_output(slack_client.rtm_read())
        while (command==None) and (channel==None):
             command, channel = parse_slack_output(slack_client.rtm_read())
        date = command
        response = "For how many days do you want to make the booking? "
        slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
        command, channel = parse_slack_output(slack_client.rtm_read())
        while (command==None) and (channel==None):
             command, channel = parse_slack_output(slack_client.rtm_read())
        days =  int(filter((lambda x :x.isdigit()),command))
        cost = get_cost(roomtype,days,nums)     #get the availibility and cose of the 
        if (cost == "error"):
              response = "Sorry! We don't have "+str(nums)+ " "+roomtype+ " rooms."
              slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
              return;
        else :
          while True:
            response = "I understand that you would want to book "+str(nums) +" " +roomtype+ "rooms in the name of "+name+", from "+date+" for " + str(days)+" days.This would cost you $"+str(cost)+" .Please confirm the booking with y/n"
            slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
            command, channel = parse_slack_output(slack_client.rtm_read())
            while (command==None) and (channel==None):
                 command, channel = parse_slack_output(slack_client.rtm_read())
            command= command.lower()
            m = re.search("y",command)
            if (m!=None): 
              # confirmed booking
               cur.execute("Insert into bookingdetails (user,roomtype,numrooms,checkin,totalcost,numdays) values (%s,%s,%s,%s,%s,%s)" ,[name,roomtype,nums,date,cost,days])
               myConnection.commit()
               print ("Confirmed booking")
               # PUT DATA IN DATABASE 
               response = "Your booking for "+str(nums)+" "+roomtype+" rooms is confirmed!"
               slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
               response = "In the event of failure for making payment within the next 24 hours will cause the cancellation of the booking"
               slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
               #response = "Thanks for Choosing us!Have a nice day! Bye !"
               #slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
               return
            else:       #not confirmed
               m = re.search("n",command)
               if (m!=None):
                  response = "I understand that you don't want to book now.You can contact us again. We are here to help you."
                  slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
                  return
               else:
                  response = "You dint answer my question right. I ll repeat."
                  slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
    else:
        m = re.search("n",command)
        if (m!=None): # confirmed no
           response = "Oh! I understand the you dint confirm the "+roomtype+ " room.Something must have gone wrong."
           slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
           return 
        else :
            response = "Sorry! You dint answer my question right. Let me ask you again"           
            slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)



def get_cost(roomtype,days,nums):
    global NUMBER_OF_DELUXE,NUMBER_OF_SUITES,NUMBER_OF_FAMILY
    global COST_OF_DELUXE,COST_OF_SUITES,COST_OF_FAMILY
    if roomtype == "deluxe":
       if( NUMBER_OF_DELUXE >= nums):
             NUMBER_OF_DELUXE = NUMBER_OF_DELUXE- nums
             return (nums*COST_OF_DELUXE*days)
    if roomtype == "suite":
        if( NUMBER_OF_SUITES >= nums):
             NUMBER_OF_SUITES = NUMBER_OF_SUITES-nums
             return (nums*COST_OF_SUITES*days)
    if roomtype == "family":
        if( NUMBER_OF_FAMILY >= nums):
             NUMBER_OF_FAMILY = NUMBER_OF_FAMILY-nums
             return (nums*COST_OF_FAMILY*days)
    return "error"
      


def parse_slack_output(slack_rtm_output):  
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
            print("reading the input")
            response = "Hello! How can I help you today?"
            while True:
              command, channel = parse_slack_output(slack_client.rtm_read())
              while (command==None) and (channel==None):
                    command, channel = parse_slack_output(slack_client.rtm_read())
              handle_command(command, channel)
              response = "Thanks for choosing us!Bye!"
              slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


              time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


def getlist(command,channel):
       lst = []
       s=re.search("suite",command)
       d = re.search("deluxe",command)
       f= re.search("family",command)
       if (s != None):
          count=1
          lst.append("suite")
       if (d != None):
          count = count+1
          lst.append("deluxe")
       if (f != None):
          count = count+1
          lst.append("family")
       return lst
