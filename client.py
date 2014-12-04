#e Purpose: Client side code for room booking system
# Amit Bapat 
# 10/26


import sys, time
from socket import *

def printRules():
    print "Rules: \nEnter in [Day] [time1] [time2] format, where [time2] is optional. Example: Tuesday 7:00-11:30 12:00-14:00 16:00-17:30"
    print "You may enter a recurring rule using the format [Day1/Day2] [time], such as Monday/Thursday/Friday 5:00-6:00. A hyphen must be used to specify time range, with no spaces in between"
    print "You may add multiple rules by using \';\' to separate arguments: [Day1] [time1];[Day2] [time2]. There must be a space between the day and time"

#sends message and recieves response from server with address
def send(clientSocket, data):
    # Get the server hostname and port as command line arguments
    argv = sys.argv                      
    host = argv[1]
    port = argv[2]

    # Command line argument is a string, change the port into integer
    port = int(port)  
    msg = ""
    try:
    # Send the UDP packet with the data
        clientSocket.sendto(data, (host, port)) 
    # Receive the server response
        message, address = clientSocket.recvfrom(1024)
    
        msg = message.split(",")

    except timeout:
        return 1,"Request timed out\n"


        #errCode must be int
    return int(msg[0]),msg[1]

#shows available timeslots for current user and/or others
def showAvailableSlots(clientSocket, user):
    user = raw_input("Show Available Timeslots for which user? ")
    week = raw_input("Which week should be displayed? (Enter 1, 2, or \'both\') ")
    days = raw_input("Which days should be displayed? (Enter specific days followed by space or \'all\' for all days) ")

    if week.lower() == "both":
        week = "1&2"

    data = "display," + user + ";" + week + ";" + days;

    errCode, msg = send(clientSocket, data)

    if errCode == 1: #some error ocurred, return to main menu loop
        print "Error: " + msg
        return 0

    print msg
    return 0


#Modify current user's timeslot
def modifyTimeslot(clientSocket, user):
    data = ""
    op = raw_input("Would you like to:\n1)Enter availability\n2)Delete a timeslot\n")

    if int(op) == 1:
        printRules()
        #accepts [Day] [time1] [time2]; [Day1/Day2] [time]
        week1 = raw_input("\nEnter your Availability for week 1: ")
        week2 = raw_input("\nEnter your Availability for week 2: ")
        data = "enter," + user + "_" + week1 + "_" + week2
        errCode, msg = send(clientSocket, data)
        if errCode == 1:
            print "Error: " + msg
        
    elif int(op) == 2:
        printRules()
        week1 = raw_input("\nWhich timeslots do you want to free in week 1? (Hit enter if none) ")
        week2 = raw_input("\nWhich timeslots do you want to free in week 2? (Hit enter if none) ")
        data = "delete," + user + "_" + week1 + "_" + week2
        errCode, msg = send(clientSocket, data)
        if errCode == 1:
            print "Error: " + msg

    else:
        print "Please enter a valid choice"


    return 0

#Queries for a timeslot to schedule meeting, books meeting for specified users, sends email
def bookMeeting(clientSocket, user):
    print "Querying Timeslots\n"
    return 0
 
def badInput():
    print "Bad Input, Please choose a correct option\n"

def quitProg():
    return 1


 
# Create UDP client socket
clientSocket = socket(AF_INET,SOCK_DGRAM)

# Set socket timeout as 1 second
clientSocket.settimeout(2)



user = raw_input("Please enter your name: ")
print "Connecting to the server...\n"
data = "login," + user
#send request to server, get response
errCode, message = send(clientSocket, data)


if errCode == 1:
    print "Error: " + message
    clientSocket.close()
    exit()


quit = 0

while (quit == 0):
    print "Main Menu\n-------------------------------------------------"
    opt = raw_input("Enter an option: \n1)Show all Available Timeslots\n2)Enter availability/Modify my timeslot\n3)Book a Meeting\n4)Quit\n")
    if opt == '1':
        quit = showAvailableSlots(clientSocket, user)
    elif opt == '2':
        quit = modifyTimeslot(clientSocket, user)
    elif opt == '3':
        quit = bookMeeting(clientSocket, user)
    elif opt == '4':
        quit = quitProg()
    else: 
        badInput()


# Close the client socket
clientSocket.close()
 
