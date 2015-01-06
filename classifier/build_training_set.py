import numpy as np 
import itertools as it
import csv

PATH_TO_DATA = '../data/'

seasons = ['2007_2008', '2008_2009', '2009_2010', '2010_2011',\
           '2011_2012', '2012_2013', '2013_2014', '2014_2015']

NUM_TEAMS = 20
NUM_SEASONS = len(seasons)
MDS_PER_SEASON = 38
MATCHES_PER_MD = 10
MATCHES_PER_SEASON = MDS_PER_SEASON * MATCHES_PER_MD
CURRENT_MD = 17

teams = ['Arsenal','Aston Villa','Birmingham City','Blackburn Rovers',\
         'Blackpool','Bolton Wanderers','Burnley','Cardiff City','Chelsea',\
         'Crystal Palace','Everton','Fulham','Hull City','Leicester City',\
         'Liverpool','Manchester City','Manchester United','Newcastle United',\
         'Norwich City','Queens Park Rangers','Portsmouth','Reading',\
         'Southampton','Stoke City','Sunderland','Swansea City',\
         'Tottenham Hotspur','West Bromwich Albion','West Ham United',\
         'Wigan Athletic','Wolverhampton Wanderers']


def match_file_name(season):
	"""Generates the name of the file containing the match data for season"""
	return PATH_TO_DATA + 'matches' + season + '.csv'

def standing_file_name(season):
	"""Generates the name of the file containing the match data for season"""
	return PATH_TO_DATA + 'tables' + season + '.csv'	

#Read the csv files

#Matches
match_history = []

for season in seasons:
	csv_file_object = csv.reader(open(match_file_name(season))) 	
	
	data=[] 	

	for row in csv_file_object: 							
		if(row != []):
			data.append(row[3:])	

	data = np.array(data)
	match_history.append(data)								

match_history = np.array(match_history)

#Standings 
standings_history = []

for season in seasons:
	csv_file_object = csv.reader(open(standing_file_name(season)))

	data = []
	
	for row in csv_file_object: 							
		if(row != []):
			data.append(row[:2])	

	data = np.array(data)
	standings_history.append(data)								

standings_history = np.array(standings_history)

#Transform strings to integers 

np_int = np.vectorize(int)

match_history = np_int(match_history)

standings_history = np_int(standings_history)

#Replace game dates by match day numbers

match_history_new = np.zeros([NUM_SEASONS, MDS_PER_SEASON * MATCHES_PER_MD, 5])

for season in range(NUM_SEASONS):
	for match_day in range(MDS_PER_SEASON):
		for match in range(MATCHES_PER_MD):
			match_history_new[season,  MATCHES_PER_MD * match_day +  match, :] = \
			np.insert(match_history[season, MATCHES_PER_MD * match_day +  match, :], 0, match_day + 1, 0)

match_history = match_history_new

#Now for each season i match_history[i,:,:] 
#looks as following  | Match day | Team 1 | Team 2 | Team 1 score | Team 2 score |
#                    |    ...    |  ...   |  ...   |      ...     |      ...     |


"""************ HELPER FUNCTIONS ***********************************"""

def find_standing(team, season, match_day):
	"""Determines standing of team on match_day of season"""

	position = -1

	for pos in range((match_day - 1) * NUM_TEAMS, match_day * NUM_TEAMS):
		if(standings_history[season, pos, 1] == team):
			position =  standings_history[season, pos, 0]

	if(match_day == 0):
		position = 0

	return position


def find_matches_two(team1, team2, till_season, till_md):
	"""Finds all the matches between team1 and team2 up to till_md of till_season and returns them as an np.array 
	containing [ Season | Match day | Team 1 scored | Team 1 missed ]"""
	
	matches = []

	for season in range(till_season):

	#For all the seasons except till_season check all the match days
		for match in range(MATCHES_PER_SEASON):
			if(match_history[season, match, 1] == team1 and match_history[season, match, 2] == team2): 
				matches.append(np.hstack((season, match_history[season, match, [0, 3, 4]])))

			#Swap the score if the teams are in reversed order in the match table 
			elif(match_history[season, match, 1] == team2 and match_history[season, match, 2] == team1):
				matches.append(np.hstack((season,match_history[season, match, [0, 4, 3]])))

	season = till_season

	for match in range((till_md - 1) * MATCHES_PER_MD):
		if(match_history[season, match, 1] == team1 and match_history[season, match, 2] == team2): 
			matches.append(np.hstack((season, match_history[season, match, [0, 3, 4]])))

		elif(match_history[season, match, 1] == team2 and match_history[season, match, 2] == team1):
			matches.append(np.hstack((season,match_history[season, match, [0, 4, 3]])))

	return np.array(matches)


def find_matches_one(team, till_season, till_md):
	"""Finds all the matches that team has played up to till_md of till_season and returns them as an np.array 
	containing [ Season | Match day | Team scored | Team missed ]"""
	
	matches = []

	for season in range(till_season):
	#For all the seasons except till_season check all the match days
		for match in range(MATCHES_PER_SEASON):
			if(match_history[season, match, 1] == team): 
				matches.append(np.hstack((season, match_history[season, match, [0, 3, 4]])))

			#Swap the score if the teams are in reversed order in the match table 
			elif(match_history[season, match, 2] == team):
				matches.append(np.hstack((season,match_history[season, match, [0, 4, 3]])))	

	season = till_season

	for match in range((till_md - 1) * MATCHES_PER_MD):
		if(match_history[season, match, 1] == team): 
			matches.append(np.hstack((season, match_history[season, match, [0, 3, 4]])))

		elif(match_history[season, match, 2] == team):
			matches.append(np.hstack((season,match_history[season, match, [0, 4, 3]])))

	return np.array(matches)


def build_team_stats(team1, team2, season, match_day, seasons_to_consider):
	"""Build the performance vector of team1 against team2 containing
	[ Standing as of (match_day - 1) | Win rate against team2 | Avg goals scored against team2 | 
	Avg goals missed from team2 | Avg win rate | Avg goals scored | Avg goals missed ]"""

	NUM_PARAMS = 7

	stats = np.zeros(NUM_PARAMS)

	#Determine standing 
	stats[0] = find_standing(team1, season, (match_day - 1))

	""" ********** TEAM 1 VS TEAM 2 ********** """
	#Find the matches between the two teams in the last seasons_to_consider seasons
	confrontations = find_matches_two(team1, team2, season, match_day)
	confrontations_new = [];
	num_confrontations = confrontations.shape[0]

	for match in range(num_confrontations):
		if(confrontations[match,0] >= (season -  seasons_to_consider)):
			confrontations_new.append(confrontations[match])

	confrontations = np.array(confrontations_new)

	#Calculate stats against team2
	num_confrontations = confrontations.shape[0]

	wr_t2 = 0
	scored_t2 = 0
	missed_t2 = 0

	for match in range(num_confrontations):
		scored_t2 += confrontations[match, 2]
		missed_t2 += confrontations[match, 3]

		if(confrontations[match, 2] > confrontations[match, 3]):
			wr_t2 += 1
		elif(confrontations[match, 2] == confrontations[match, 3]):
			wr_t2 += 0.5
		else:
			pass

	#Normalize the values
	wr_t2 /= num_confrontations
	scored_t2 /= num_confrontations
	missed_t2 /= num_confrontations

	stats[1] = wr_t2
	stats[2] = scored_t2
	stats[3] = missed_t2

	""" ********** TOTAL STATS ********** """
	#Find all the matches of the team1 in the last seasons_to_consider seasons
	matches = find_matches_one(team1, season, match_day)
	matches_new = []
	num_matches = matches.shape[0]

	for match in range(num_matches):
		if(matches[match,0] >= (season -  seasons_to_consider)):
			matches_new.append(matches[match])

	matches = np.array(matches_new)

	#Calculate the stats

	num_matches = matches.shape[0]

	wr_tot = 0
	scored_tot = 0
	missed_tot = 0

	for match in range(num_matches):
		scored_tot += matches[match, 2]
		missed_tot += matches[match, 3]

		if(matches[match, 2] > matches[match, 3]):
			wr_tot += 1
		elif(matches[match, 2] == matches[match, 3]):
			wr_tot += 0.5
		else:
			pass

	#Normalize the values
	wr_tot /= num_matches
	scored_tot /= num_matches
	missed_tot /= num_matches

	stats[4] = wr_tot
	stats[5] = scored_tot
	stats[6] = missed_tot

	return stats
