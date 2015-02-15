import numpy as np
import pandas as pd

def main():
    PATH_TO_DATA = '../data/'

    seasons = ['2007_2008', '2008_2009', '2009_2010', '2010_2011',\
               '2011_2012', '2012_2013', '2013_2014', '2014_2015']

    NUM_TEAMS = 20
    NUM_SEASONS = len(seasons)
    SEASONS_TO_CONSIDER = 2
    MDS_PER_SEASON = 38
    MATCHES_PER_MD = 10
    MATCHES_PER_SEASON = MDS_PER_SEASON * MATCHES_PER_MD
    CURRENT_MD = 26
    WIN_PTS = 3
    DRAW_PTS = 1
    LOSS_PTS = 0

    def read_data():
        """Reads data from the csv files, return two arrays containing match_history and standings_history"""
        def match_file_name(season):
            """Generates the name of the file containing the match data for season"""
            return "%smatches/matches%s.csv" % (PATH_TO_DATA, season) 

        def standing_file_name(season):
            """Generates the name of the file containing the match data for season"""
            return "%stables/tables%s.csv" % (PATH_TO_DATA, season) 

        #Read the csv files
        match_history = []
        standings_history = []

        for season in seasons:
            match_history.append(pd.read_csv(match_file_name(season)))
            standings_history.append(pd.read_csv(standing_file_name(season)))

        return [match_history, standings_history]


    def performance_till_date(team, seasons_to_consider, season, match_day):
        """Calculates the average performance of team in the past seasons_to_consider seasons

        Arguments:
            team - (int) team id
            seasons_to_consider - (int) number of seasons to collect data about
            season - (string) season name
            match_day - (int) number of the current match day in range(1, MDS_PER_SEASON + 1)

        Returns:
            A pd.Series object containing
            [avg_points_per_game, avg_scored_per_game, avg_missed_per_game]
        """
        try:
            season_index = seasons.index(season)
        except ValueError:
            print("Incorrect season name for performance_till_date!")
            return pd.Series(None)

        cnt = 0
        standings_38 = standings_history[0]['match_day'] == 38
        standings_extracted = []

        points_past = []
        scored_past = []
        missed_past = []
        seasons_plyed = []
        standings_curr_extracted = 0

        # getting the stats from the past
        for i in range(season_index, season_index - seasons_to_consider, -1):
        # first the stats from previous seasons
            standings_extracted.append(standings_history[season_index - cnt - 1][standings_38])
            in_season = standings_extracted[cnt].loc[standings_extracted[cnt]['team'] == team].empty
            # print(standings_extracted[cnt])
            if not(in_season):
                points_past.append(int(standings_extracted[cnt][standings_extracted[cnt]['team'] == team]['points']))
                scored_past.append(int(standings_extracted[cnt][standings_extracted[cnt]['team'] == team]['scored']))
                missed_past.append(int(standings_extracted[cnt][standings_extracted[cnt]['team'] == team]['missed']))
                seasons_plyed.append(i-1)
            cnt += 1

        tot_games = len(seasons_plyed) * MDS_PER_SEASON
        tot_points_past = np.sum(points_past) 
        tot_scored_past = np.sum(scored_past) 
        tot_missed_past = np.sum(missed_past)

        # now the stats for current season
        stats = []
        points_curr = 0
        scored_curr = 0
        missed_curr = 0

        standings_curr = 0
        if(match_day > 1):
           standings_curr = standings_history[0]['match_day'] == (match_day - 1)
           standings_curr_extracted =  standings_history[season_index][standings_curr]
           points_curr = int(standings_curr_extracted[standings_curr_extracted['team'] == team]['points'])
           scored_curr = int(standings_curr_extracted[standings_curr_extracted['team'] == team]['scored'])
           missed_curr = int(standings_curr_extracted[standings_curr_extracted['team'] == team]['missed'])
           tot_games += match_day - 1

        stats = pd.Series({'avg_points_per_game' : (tot_points_past + points_curr) / tot_games,
                           'avg_scored_per_game' : (tot_scored_past + scored_curr) / tot_games,
                           'avg_missed_per_game' : (tot_missed_past + missed_curr) / tot_games})

        return stats


    def get_standing(team, season, match_day):
        """Determines team's standing on the previous match day

        If it's the first day of the season, standing from the last day of the last season is used
        If the team hasn't played last season, lowest possible place (20) is returned

        Arguments:
            team - (int) team id
            season - (string) name of the season
            match_day - (int) number of the match day in range(1, MDS_PER_SEASON + 1)
        Returns:
            standing - (int) team's standing on the given match_day of season  
        """

        #Check if the season name is valid
        try:
            season_index = seasons.index(season)
        except ValueError:
            print("Incorrect season name for get_standing!")
            return None

        standing = -1

        #Check if the team is participating in the season #season_index
        if standings_history[season_index].loc[standings_history[season_index]['team'] == team].empty:
            print("Team doesn't participate in the current season!")
            return standing

        #Check if it is the first day of the season
        if match_day == 1:
            standing = standings_history[season_index - 1].loc[standings_history[season_index - 1]['match_day'] == MDS_PER_SEASON].\
                        loc[standings_history[season_index - 1]['team'] == team]['standing']
            
            #if the team hasn't played last season
            if standing.empty:
                standing = 20
            else:
                standing = int(standing)
        else:
            standing = standings_history[season_index].loc[standings_history[season_index]['match_day'] == (match_day - 1)].\
                        loc[standings_history[season_index]['team'] == team]['standing']
            standing = int(standing)

        return standing


    def matchups_till_date(team1, team2, seasons_to_consider, season, match_day):
        """Computes (team1 vs. team2) or (team2 vs. team1) parameters for specified seasons up to the current match day
        
        Arguments:
            team1, team2 - (int) team id
            seasons_to_consider - (int) number of past seasons to consider
            season - (string) current season name
            match_day - (int) current match day index
        
        Returns:
            results - (pd.Series) average column values of result
            (contains: [t1_avg_pts, t2_avg_pts, t1_avg_scrd, t1_avg_recv])
        """

        def compute_parameters(matches, team1, team2):
            """Finds (team1 vs. team2) or (team2 vs. team1) matches and compute results for one specified season
            
            Arguments:
                team1, team2 - (int) team id
                matches - (pd.DataFrame) all matches of one season
            
            Returns:
                result - (pd.DataFrame) parameters_for_all_match_days
                (each row contains: [t1_pts, t2_pts, t1_scrd, t1_recv])
            """

            # Search for two cases:
            # 1. team1 - home
            # 2. team1 - away
            common_home = matches.loc[matches['team1'] == team1].loc[matches['team2'] == team2]
            common_away = matches.loc[matches['team1'] == team2].loc[matches['team2'] == team1]
            
            # Rearrange columns in order to put team1 on the first place (for away matches)
            for index, row in common_away.iterrows():
                temp_team = row['team1']
                temp_score = row['score1']
                row['team1'] = row['team2']
                row['score1'] = row['score2']
                row['team2'] = temp_team
                row['score2'] = temp_score

            # Concatenate and compute parameters for each match
            common = pd.concat([common_home, common_away])

            # Init empty DataFrame
            result = pd.DataFrame(None)

            # Compute parameters according to the scores for each match 
            for index, row in common.iterrows():
                if row['score1'] > row['score2']:
                    t1_avg_pts = WIN_PTS
                    t2_avg_pts = LOSS_PTS
                    t1_avg_scrd = row['score1']
                    t1_avg_recv = row['score2']

                elif row['score1'] < row['score2']:
                    t1_avg_pts = LOSS_PTS
                    t2_avg_pts = WIN_PTS
                    t1_avg_scrd = row['score1']
                    t1_avg_recv = row['score2']

                else:
                    t1_avg_pts = DRAW_PTS
                    t2_avg_pts = DRAW_PTS
                    t1_avg_scrd = row['score1']
                    t1_avg_recv = row['score2']

                # Accumulating results in the DataFrame
                df = pd.DataFrame({'t1_avg_pts_mu': [t1_avg_pts], 't2_avg_pts_mu': [t2_avg_pts],
                                   't1_avg_scrd_mu': [t1_avg_scrd], 't1_avg_recv_mu': [t1_avg_recv]})
                result = pd.concat([result, df])

            return result

        # Init empty DataFrame
        common_matches = pd.DataFrame(None)

        # Read current season string
        try:
            season_index = seasons.index(season)
        except ValueError:
            print("Incorrect season name for matchup_till_season")
            return pd.Series(None)

        # Iterate over seasons
        for season_id in range(season_index - seasons_to_consider, season_index + 1):

            # Matches for each season
            matches = match_history[season_id]

            # Search and accumulate common matches in the DataFrame
            if season_id == season_index:
                matches = matches[:(match_day - 1)*MATCHES_PER_MD] # Restrict matches to current match day
                common_matches = pd.concat([common_matches, compute_parameters(matches, team1, team2)])
            else:
                common_matches = pd.concat([common_matches, compute_parameters(matches, team1, team2)])

        # Write result
        results = (common_matches.sum())/len(common_matches)

        return results


    def is_team_home(team, season, match_day):
        """Return 1 if the team is playing home at the match_day of season, 0 if away

        Returns -1 if the team doesn't play on the match_day of the season

        Arguments:
            team - (int) team id
            season - (string) name of the season
            match_day - (int) number of the match day in range(1, MDS_PER_SEASON + 1)
        Returns:
            result - (int) 1 if the team is playing home at the match_day of season, 0 if away
            -1 if the team doesn't play on the match_day of the season
        """
        #Check if the season name is valid
        try:
            season_index = seasons.index(season)
        except ValueError:
            print("Incorrect season name for get_standing!")
            return None

        match = match_history[season_index].loc[match_history[season_index]['match_day'] == match_day]

        if not match.loc[match_history[season_index]['team1'] == team].empty:
            result = 1
        elif not match.loc[match_history[season_index]['team2'] == team].empty:
            result = 0
        else:
            print("Team %d doesn't play on md %d of season %d" %(team, match_day, season_index))
            result = -1

        result = pd.Series({'t1_home' : result})
        return result


    def build_vector_for_match(team1, team2, seasons_to_consider, season, match_day):
        """Builds a training vector for one match between team1 and team2

        Arguments:
            team1, team2 - (int) team id
            seasons_to_consider - (int) number of seasons to collect data about
            season - (string) name of the season
            match_day - (int) number of the match day in range(1, MDS_PER_SEASON + 1)
        Returns:
            vector - (pd.Series) containing all the data relevant to the match between two teams
        """
        #home = is_team_home(team1, season, match_day)
        standing = pd.Series({'t1_standing' : get_standing(team1, season, match_day), 
                              't2_standing': get_standing(team2, season, match_day)})
        perf1 = performance_till_date(team1, seasons_to_consider, season, match_day)
        perf1.rename(index={'avg_missed_per_game' : 't1_avg_recv_tot',
                            'avg_points_per_game' : 't1_avg_pts_tot',
                            'avg_scored_per_game' : 't1_avg_scrd_tot'}, inplace=True)
        perf2 = performance_till_date(team2, seasons_to_consider, season, match_day)
        perf2.rename(index={'avg_missed_per_game' : 't2_avg_recv_tot',
                            'avg_points_per_game' : 't2_avg_pts_tot',
                            'avg_scored_per_game' : 't2_avg_scrd_tot'}, inplace=True)
        matchups = matchups_till_date(team1, team2, seasons_to_consider, season, match_day)
        vector = pd.concat([standing, perf1, perf2, matchups])
        return vector


    def build_training_set():
        def training_file_name():
            return "%s/training/training_set.csv" % (PATH_TO_DATA) 

        training_set = pd.DataFrame()
        for season in seasons[SEASONS_TO_CONSIDER : NUM_SEASONS]:
            season_index = seasons.index(season)
            for match_day in range(1, MDS_PER_SEASON + 1):
                md = match_history[season_index].loc[match_history[season_index]['match_day'] == match_day]
                for match in md.iterrows():
                    team1 = match[1]['team1']
                    team2 = match[1]['team2']
                    score1 = match[1]['score1']
                    score2 = match[1]['score2']

                    this_game = build_vector_for_match(team1, team2, SEASONS_TO_CONSIDER, season, match_day)

                    if score1 > score2:
                        result = 1 #t1 won
                    elif score2 > score1:
                        result = 2 #t2 won
                    else:
                        result = 0 #draw

                    this_game = this_game.append(pd.Series({'result' : result}))

                    training_set = training_set.append( this_game, ignore_index=True)
           
            print("training examples for season %s calculated" % (season))

        training_set.to_csv(training_file_name())
        print("training examples successfully exported")
        
    match_history, standings_history = read_data()

    build_training_set()


if __name__ == "__main__":
    main()
 