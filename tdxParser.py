'''
AUTHOR: Alexa Roskowski
2/16/23


This is a parser of CSV files specifically for the use of TDX ticket reports

This is just a protype that takes one specific file (FA 2022) and will display a
matplot graph of the distribution of the number of tickets that USS Classrooms
were responsible for by week.
'''

import csv #used for reading the file
import os
from datetime import datetime,date #used for sorting by modified date
import matplotlib.pyplot as plt #used for plotting pretty graphs




def ticketCountPerTerm(fp):
	#will eveuntally want this to take any filename
	f = open(fp, mode = 'r')

	csv_reader = csv.DictReader(f)

	classroomTickets = [] #list of all the tickets where USS Classrooms are responsible
	for row in csv_reader:
		#loop through and check the responsible group
		if row['Resp Group'] == 'USS-Classrooms':
			#add to the list
			classroomTickets.append(row)

	f.close() #we are done taking the important data from the csv file so close it




	#sort the tickets by the modified date
	classroomTickets.sort(key=lambda d: datetime.strptime(d['Modified'], "%m/%d/%Y %H:%M"))

	ticketPerWeek = [0] * 11 #list of the counts of tickets per week

	first_ticket = datetime.strptime(classroomTickets[0]['Modified'], "%m/%d/%Y %H:%M")

	for ticket in classroomTickets:
		#figure out which week the ticket is in
		date = datetime.strptime(ticket['Modified'], "%m/%d/%Y %H:%M")
		delta = date - first_ticket
		index = delta.days // 7
		#incase you pulled a date a little too far
		index = index - 1  if index >= 11 else index

		#add to the count of whcih week its in
		ticketPerWeek[index] += 1

	print(ticketPerWeek)


	## GRAPHING TIME ##

	weeks = ["Week " + str(i + 1) for i in range(11)] # list of week count for graph
	#print(weeks)

	#initialize the graph
	fig,ax = plt.subplots(figsize = (10, 5))
	ax.bar(weeks, ticketPerWeek, color = 'green')

	#plt.xlabel("Weeks") # removed cause each bar is labeled Week (num)
	ax.set_ylabel("Count")
	ax.set_title("Number of Tickets Per Week for Fall 2022")

	rect = ax.patches
	for rect, c in zip(rect, ticketPerWeek):
		#add the count to the graph
		height = rect.get_height()
		ax.text(
	            rect.get_x() + rect.get_width() / 2,
	            height + 0.01,
	            c,
	            horizontalalignment='center',
	            verticalalignment='bottom',
	            color='Black',
	            fontsize='medium'
			)

	plt.show()




def main():
	while(1):
		print("To quit just enter nothing")
		filename = input("Enter a csv file: ")
		filename.strip()
		if filename == "":
			#person want to quit, so return so the graph funct isn't called
			return
		if not (os.path.exists(filename)):
			#file does not exist make them try again
			print("Sorry that file does not exist :(")
		else:
			#file exists
			#check if its a cvs file
			if (os.path.splitext(filename)[-1].lower()) != '.csv':
				#not a csv file make them try again
				print("Sorry that file is not a csv file :( ")
			else:
				#file exists and is a csv file so break out of the loop
				break




	ticketCountPerTerm(filename)
	return


if __name__ == "__main__":
	main()








