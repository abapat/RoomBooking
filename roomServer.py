# Purpose: Server side code for room booking system
# Amit Bapat 
# 10/26

import copy
import socket

from socket import *

daysWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class Day:
    #self.day = None
    #self.slots = None
    def __init__(self, dayofweek):
        self.day = dayofweek
        self.slots = [0 for i in range(48)] #list length 48
        
    #def debug_printSlots():


    #prints available timeslots
    def printDay(self):
        string = self.day + ":"
        i = 0
        flag = 0
        
        while i < len(self.slots):
            if self.slots[i] == 1:
                i = i + 1
            else:
                startInd = self.translate(i)
                while (i < len(self.slots) and self.slots[i] == 0):
                    i = i + 1
                endInd = self.translate(i) 
                string = string + " " + startInd + "-" + endInd

        return string

    #returns when the day is free in certain time frame and duration
    #params: array of timeslots (already checked for errors) ex) 7:00-9:30
    #returns: array of valid times
    def getAvailableTimes(self, timeslot, duration):
        times = []
        for time in timeslot:
            parts = time.split("-")
            startInd = self.getIndex(parts[0])
            endInd = self.getIndex(parts[1])
            dur = 0
            i = startInd
            while i < endInd:
                if self.slots[i] == 0:
                    #startInd = i
                    dur = dur + 0.5
                    i = i + 1
    
                elif dur >= duration and startInd != i: #found timeslot with correct duration
                    nextSlot = self.translate(startInd) + "-" + self.translate(i)
                    times.append(nextSlot)
                    dur = 0
                    i = i + 1
                    startInd = i

                else: #no match
                    dur = 0
                    i = i + 1
                    startInd = i


            if dur >= duration and startInd != i:
                nextSlot = self.translate(startInd) + "-" + self.translate(i)
                times.append(nextSlot)
                
        return times




        '''
        while i < len(self.slots):
            if self.slots[i] == 0 and day.slots[i] == 0:
                startInd = self.translate(i)
                while i < len(self.slots) and self.slots[i] == 0 and day.slots[i] == 0:
                    i = i + 1

                endInd = self.translate(i)
                str = str + " " + startInd + "-" + endInd

            else:
                i = i + 1

        return str '''

    #tries to book certain timeslot for day, returns error if bad time
    #param: str, ex) 5:00-8:00; op= book or free
    #return: int errorcode, str message
    def modifyTiming(self, string, op):
        times = string.split("-")
        book = 1
        if op == "free":
            book = 0 #free

        if timeCheck(times[0]) == 1 or timeCheck(times[1]) == 1:
            errCode = 1
            message = "Incorrect time format. Please enter a valid timeslot. Error occured at: " + string
            return errCode, message

        startInd = self.getIndex(times[0])
        endInd = self.getIndex(times[1]) - 1

        i = startInd
        while i <= endInd:
            if self.slots[i] == book:
                timeslot = self.translate(i)
                errCode = 1
                message = "Timeslot already "
                if book == 1:
                    message = message + "booked!"
                else:
                    message = message + "freed!"
                message = message + " Error occured at time " + timeslot
                return errCode, message

            self.slots[i] = book
            i = i + 1

        errCode = 0
        message = "Sucess. Debug:(book = " + str(book) + ") modified indices " + str(startInd) + "-" + str(endInd)
        return errCode, message

    #string time-> index; ex) 4:30 => 9
    def getIndex(self, str):
        parts = str.split(":")
        hour = int(parts[0])
        ind = hour * 2
        mins = int(parts[1])
        if mins == 30:
            ind = ind + 1

        return ind

    #index to string time
    def translate(self, index):
        ind = index / 2
        string = str(ind) + ":"
        if index % 2 != 0:
            string = string + "30"
        else:
            string = string + "00"

        return string


class Schedule:
    def __init__(self):
        i = 0
        self.week1 = []
        self.week2 = []
        while i < len(daysWeek):
            strDay = daysWeek[i]
            strDay1 = daysWeek[i]
            d = Day(strDay)
            d1 = Day(strDay1) #different instance for different week
            self.week1.append(d)
            self.week2.append(d1)
            i = i + 1
        #print "DEBUG: len week = " + str(len(self.week1))

    def printDays(self, week, days):
        dayArr = days.split(" ")
        arr = []
        output = ""
        i = 0
        while (i < len(daysWeek)):
            arr.append(daysWeek[i].lower())
            i = i+1

        #print "DEBUG: arr= " + str(arr) + "\nWeek= " + str(len(self.week1))
        #print "DEBUG: dayArr= " + str(dayArr)
        for string in dayArr:
            if string == "":
                continue
            
            if string.lower() in arr: #it will be in week
                ind = arr.index(string.lower())
                output = output + week[ind].printDay() + "\n" + str(week[ind].slots) + "\n"
            else:
                output = output + "Invalid input: " + string + "\n"

        return output

    #finds day and modifies the timeslot in week 'week' with operation 'op' (either book or free) and times 'times'
    #op must be either book or free
    #days must be valid days
    def modifyTimeslot(self, week, days, times, op):
        msg = ""
        for d in days:
            curr = self.getDay(week, d)
            for t in times:
                errCode,message = curr.modifyTiming(t, op)
                if errCode == 1:
                    return str(errCode),message
                else: 
                    msg = msg + message + "\n"

        return 0,msg

    #param: string week, array of days and array of timeslots to check for availability. all args have been checked for errors
    def queryTimeslot(self, week, days, times,duration):
        
        res = ""
        flag = 0
        for d in days:
            day = self.getDay(week, d)
            t = day.getAvailableTimes(times,duration)
            if len(t) != 0:
                if flag == 0:
                    res = res + d
                    flag = 1
                else:
                    res = res + ";" + d

                for validTime in t:
                    res = res + " " + validTime

        print "DEBUG: in queryTimeslot, returning=" + res + "\n"
        return res
        



    def getDay(self, week, day):
        arr = []
        i = 0
        while (i < len(daysWeek)):
            arr.append(daysWeek[i].lower())
            i = i+1

        ind = arr.index(day.lower())
        #return proper day, finsh modify method

        if week == "week1":
            return self.week1[ind]
        #else
        return self.week2[ind]


    #expects param in form of list, slot[0] is week: 1, 2, or 1&2. slot[1] is days: can be specific days or 'all' for all days
    def showTimeSlot(self, slot):
        str = ""
        daysToPrint = ""
        if slot[1] == "all":
            i = 0
            while (i < len(daysWeek)):
                daysToPrint = daysToPrint + " " + daysWeek[i]
                i = i +1
        else:
            daysToPrint = slot[1]

        #print "DEBUG: daysofweek= " + daysToPrint

        if slot[0] != "2": #print week 1
            str = str + "\t\t\tWEEK 1\n----------------------------------------------------------------\n"
            text = self.printDays(self.week1, daysToPrint)
            str = str + text
            str = str + "----------------------------------------------------------------\n"
        if slot[0] != "1":
            str = str + "\t\t\tWEEK 2\n----------------------------------------------------------------\n"
            text = self.printDays(self.week2, daysToPrint)
            str = str + text
            str = str + "----------------------------------------------------------------\n"

        return str

class User:
    #self.name = ""
    #self.email = ""
    #self.schedule
    def __init__(self, username, useremail):
        self.name = username
        self.email = useremail
        self.schedule = Schedule()

##########################################################################################################################################
def login(name, users):
    arr =[]
    for i in users:
        arr.append(i.name.lower())

    #print "DEBUG: name = " + name + ", arr = " + str(arr)

    if name.lower() in arr:
        #print "DEBUG: name found"
        return "0,Success"

    return "1,User not found"

def getUser(user, users):
    
    for u in users:
        #print "DEBUG: Checking: " + str(u.name.lower()) + " vs: " + user.lower()
        if u.name.lower() == user.lower():
            return u

    return None

def validDay(text):
    for i in daysWeek:
        if text.lower() == i.lower():
            return 1

    return 0

#checks for valid time: 1) valid hour 2)valid minute 3)valid format
def timeCheck(string):
    if ":" not in string:
        return 1

    parts = string.split(":")
    if (len(parts[0]) > 2 or len(parts[1]) > 2):        
        return 1
    hours = int(parts[0])
    mins = int(parts[1])

    if hours < 0 or hours > 24:
        print "DEBUG: hourcheck- returning 1 for hrs " + str(hours)
        return 1
    if mins != 0 and mins != 30:
        print "DEBUG: mincheck- returning 1 for mins " + str(mins)
        return 1
    if hours == 24 and mins > 0:
        print "DEBUG: invalid- 24:xx " + str(mins)
        return 1

    return 0

def display(str, users):
    result = ""
    parts = str.split(";") #user;weeks;days
    res = login(parts[0], users)
    arr = res.split(",")
    if arr[0] == 1: #cannot find user
        return res
    #TODO check if valid day?

    userArr =[]
    for i in users:
        userArr.append(i.name.lower())    
    #find user
    ind = userArr.index(parts[0].lower())

    slot = []
    slot.append(parts[1])
    slot.append(parts[2])

    usr = users[ind]
    result = "0," + usr.schedule.showTimeSlot(slot)
    return result


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~TODO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#************************************************************************************
#ex) 'amit_Monday 7:00-9:00 12:00-14:30; Tuesday/Thursday 13:00-16:30 19:00-21:00_'
def modify(string, users, op):
    parts = string.split("_")
    user = getUser(parts[0], users)
    if user == None:
        return "1,Invalid User"
    sched = user.schedule
    response = ""
    i = 1
    while i <= 2:
        week = parts[i]
        if week == "":
            i = i+1
            continue
        entries = []
        if ";" not in week:
            entries.append(week)
        else:
            entries = week.split(";")

        for e in entries:
            args = e.split(" ")
            flag = 0 #0- day not found. 1- day was found
            days = []
            times = []
            for a in args:
                if a == "":
                    continue

                if flag == 0 and "/" in a:
                    for d in a.split("/"):
                        if d != "" and validDay(d) == 0: #not valid day
                            return "1,Please enter a valid day. Error occured at: " + d

                    days = a.split("/")
                    flag = 1

                elif flag == 0 and validDay(a) == 1:
                    days.append(a)
                    flag = 1

                if flag == 1 and "-" in a:
                    t = a.split("-")
                    if timeCheck(t[0]) == 1 or timeCheck(t[1]) == 1:
                        return "1, invalid timeslot " + a
                    times.append(a)

            if len(days) == 0:
                return "1,Error while parsing days: could not find day to modify"
            if len(times) == 0:
                return "1,Error while parsing times: could not find time to modify"

            if i == 1:
                errCode,resp = sched.modifyTimeslot("week1", days, times, op)
            if i == 2:
                errCode,resp = sched.modifyTimeslot("week2", days, times, op)

            if errCode == 1:
                return "1," + "\n" + resp
            else:
                response = response + resp + "\n"

        i = i+1

    return "0," + "\n" + response


# users_timeframe_duration  ex) 'amit;rohan;alice_1&2_Tuesday/Thursday 13:00-16:30 19:00-21:00; Friday 1:00-4:00_1:30'
#compareDays(self, day1, timeslot, duration) returns array of times 
def runQuery(string, users):
    parts = string.split("_")

    if ";" not in parts[0]:
        return "1,You must book a meeting with more than 1 person!"

    userArr = parts[0].split(";")
    userObjs = []
    for u in userArr:
        if u == "":
            continue
        curr = getUser(u, users)
        if curr == None:
            return "1,Could not find user " + u
        userObjs.append(curr)

    week = []
    
    if parts[1] == "1":
        week.append("week1")
    elif parts[1] == "2":
        week.append("week2")
    else:
        week.append("week1")
        week.append("week2") 

    slot = parts[2]
    duration = float(parts[3])
    
    entries = []
    results = []

    for w in week:
        if ";" not in slot:
            entries.append(slot)
        else:
            entries = slot.split(";")

        print "DEBUG: entering userObj loop, entries=" + str(entries) + "\n"

        slot = ""
        for usr in userObjs:
            sched = usr.schedule
            slot = "" #for each user, building different timeslot of availability ex) Tuesday/Thursday 13:00-16:30 19:00-21:00; Friday 1:00-4:00 
            for e in entries:
                if e == "":
                    continue

                args = e.split(" ")
                flag = 0 #0- day not found. 1- day was found
                days = []
                times = []
                for a in args:
                    if a == "":
                        continue

                    if flag == 0 and "/" in a:
                        for d in a.split("/"):
                            if d != "" and validDay(d) == 0: #not valid day
                                return "1,Please enter a valid day. Error occured at: " + d

                        days = a.split("/")
                        flag = 1

                    elif flag == 0 and validDay(a) == 1:
                        days.append(a)
                        flag = 1

                    if flag == 1 and "-" in a:
                        times.append(a)

                if len(days) == 0:
                    return "1,Error while parsing days: could not find day to modify"
                if len(times) == 0:
                    return "1,Error while parsing times: could not find time to modify"

                output = sched.queryTimeslot(w, days, times, duration)
                if output == "":
                    slot = ""
                else:
                    slot = slot + output + ";"

            if slot == "":
                return [1,"No available timeslot for " + str(duration) + " hours with specified users"]

            entries = slot.split(";")

        #should have updated slot availability time for week x
        results.append((w + "_" + slot)) #may have ";" at end

    return [0,results]


def query(string, users):
    res = runQuery(string, users)
    errCode = int(res[0])
    if errCode == 1:
        return "1," + res[1]

    results = res[1]
    output = ""
    for r in results:
        if r == 0:
            continue
        parts = r.split("_")
        output = output + "\t\t\t" + parts[0] + "\n" + "____________________________________________________________" + "\n"
        days = parts[1].split(";")
        for d in days:
            if d == "":
                continue
            output = output + d + "\n"

        output = output + "\n\n"

    return "0," + output 



#def book(string, users):


#**************************************************************************************

###########################################################################################################################################

#Create a UDP socket
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(('', 7755))

#path = raw_input("Enter path of input file: ")
path = "users"
f = open(path, 'r')
users = []
#create users
for line in f:
    parts = line.split(" ")
    name = parts[0]
    email = parts[1]
    person = User(name, email)
    users.append(person)

print "Result: " + modify("amit_Tuesday/thursday 02:00-4:00; Friday 1:30-3:00_ Sunday 00:00-24:00; Saturday 1:00-4:30 6:00-13:30 15:00-20:00", users, "book") + "\n\n\n"
print "Result: " + modify("alice_Tuesday/thursday 02:00-4:00 8:00-11:00; Friday 1:30-3:00_Saturday 1:00-4:30 6:00-13:30 15:00-20:00", users, "book") + "\n\n\n"
print "Meeting Availability: \n" + query("amit;rohan;alice_1&2_Tuesday/thursday 02:00-4:00 8:00-12:30_1.5", users)
#print "Result: " + modify("amit_Tuesday/thursday 02:00-3:00_", users, "free") + "\n"
#print "result: " + display("Amit;1&2;all", users)
#print "result: " + display("alice;1&2;all", users)
exit()
while True:

    # Receive the client packet along with the address it is coming from
    message, address = serverSocket.recvfrom(1024)

    msg = message.split(",")
    #get data from client
    function = msg[0]
    arg = msg[1]
    print "Recieved arg: " + arg + "\n"
    responseMsg = ""

    if function == "login":
        responseMsg = login(arg, users)
    elif function == "display":
        responseMsg = display(arg, users)
    elif function == "enter":
        responseMsg = modify(arg, users, "book")
    elif function == "delete":
        responseMsg = modify(arg, users, "free")
    elif function == "query":
        responseMsg = query(arg, users)
    elif function == "book":
        responseMsg = book(arg, users)
    else:
        responseMsg = "1, Invalid function argument"

    #Send response 
    #print "DEBUG: response= " + responseMsg
    serverSocket.sendto(responseMsg, address)

