from agent import Agent
import random

"""This agent is written in pair
Name: RAO YUNHUI Student number: 22551999
Name: XIE CHUNGUANG Student number: 22555027
"""
class ExpertRule(Agent):
    '''ExpertRule Agent for CITS3001 project in the game The Resistence'''
    
    def __init__(self, name = 'ExpertRule'):
        '''
        initializes agent
        '''
        self.name = name
        #e.g. self.mission_size[8][3] is the number to be sent on the 3rd mission in a game of 8
        self.mission_sizes = {
                5:[2,3,2,3,3], \
                6:[2,3,4,3,4], \
                7:[2,3,3,4,4], \
                8:[3,4,4,5,5], \
                9:[3,4,4,5,5], \
                10:[3,4,4,5,5]
                }
        #number of spies for different game sizes
        self.spy_count = {5:2, 6:2, 7:3, 8:3, 9:3, 10:4} 
        #e.g. self.betrayals_required[8][3] is the number of betrayals required for the 3rd mission in a game of 8 to fail
        self.fails_required = {
                5:[1,1,1,1,1], \
                6:[1,1,1,1,1], \
                7:[1,1,1,2,1], \
                8:[1,1,1,2,1], \
                9:[1,1,1,2,1], \
                10:[1,1,1,2,1]
                }
    
    def __str__(self):
        '''
        Returns a string represnetation of the agent
        '''
        return 'Agent '+self.name
    
    def __repr__(self):
        '''
        returns a representation fthe state of the agent.
        overridde this function to debug
        '''
        return self.__str__()
               
    def new_game(self, number_of_players, player_number, spies):
        '''
        initialises the game, informing the agent of the number_of_players, 
        the player_number (an id number for the agent in the game),
        and a list of agent indexes, which is the set of spies if this agent is a spy,
        or an empty list if this agent is not a spy.
        '''
        self.roundct = 0
        self.missionct = 0
        self.spywins = 0
        self.resistantwins = 0
        self.failed_teams = []
        self.failed_nums = []
        self.number_of_spies = self.spy_count[number_of_players]
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spies
        self.im_spy = True if self.player_number in self.spy_list else False
        self.in_failed_teams = []
        for idx in range(number_of_players):
            self.in_failed_teams.append([idx,0])

    def propose_mission(self, team_size, fails_required = 1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        fails_required are the number of fails required for the mission to fail.
        '''
        # propose a random team for now
        self.in_failed_teams = sorted(self.in_failed_teams, key=lambda x:x[1], reverse = False)
        fail_needed = self.fails_required[self.number_of_players][self.roundct]

        team = [self.player_number] # 1. always include itself in a mission
        
        if self.im_spy: # for spy
            # 2. select enough spies
            # select spy has smallest suspition
            for agent in self.in_failed_teams:
                if len(team)<fail_needed and agent[0] not in team and agent[0] in self.spy_list:
                    team.append(agent[0])
            for agent in self.in_failed_teams:
                if len(team)<team_size and agent[0] not in team and agent[0] not in self.spy_list:
                    team.append(agent[0])
            return team
            
        else: # for resistant
            for agent in self.in_failed_teams:
                if len(team)<team_size and agent[0] not in team:
                    team.append(agent[0])
            return team
    
    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        '''
        print('###in vote',self.name)
        print('this is the {0}th mission, in the {1}th round'.format(self.missionct,self.roundct))
        print('proposer:,',proposer)
        print('mission:,',mission)
        '''
        if self.roundct == 0:
            return True
        if self.missionct == 4: # 1. vote yes for the last mission in the round, as most Resistant would
            return True
        if self.spywins == 0: # 1. no one has any information for now
            return True
        if proposer == self.player_number: # 1. vote yes for itself proposion
            return True
        if self.im_spy:
            fail_needed = self.fails_required[self.number_of_players][self.roundct]
            spyct = 0
            for agent in mission:
                if agent in self.spy_list:
                    spyct += 1
            if spyct == fail_needed: # 2. spy votes yes for team contains enough spy
                return True
            # 3. spy votes for team contains too many spy
            if spyct > fail_needed: 
                if self.player_number not in mission: # 3. -> 2. vote against team without itself
                    return False
                if random.random() > 0.5:
                    return True
                else:
                    return False
            # 4. spy votes for team contains not enough spy
            if spyct < fail_needed: 
                if spyct > 0:
                    return True
                else:
                    return False
        # 5. reject team failed before        
        if mission in self.failed_teams: 
            return False
        # 6. reject team without me
        if self.player_number not in mission: # vote against team without itself
            return False
        # 7. approve a new team
        if mission not in self.failed_teams:
            return self.approve_new_mission(mission)
        
        # I am happy with every mission
        return True
    
    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        Only spies are permitted to betray the mission. 
        '''
        # check how many spies in the mission
        spyct = 0
        for spy in self.spy_list:
            if spy in mission:
                spyct += 1
        # figure out how many spies needed in this mission
        fail_needed = self.fails_required[self.number_of_players][self.roundct] 
        if self.spywins == 2 and spyct >= fail_needed: # 1. win the game
            return True
        if self.resistantwins == 2: # 2. prevent resistant from winning
            return True
        if spyct == fail_needed:
            if len(mission) <= 2:  # 3. avoid being suspicious
                return False
            return True
        if spyct > fail_needed: # 4. avoid  double-sabotaging
            return False
        if spyct < fail_needed: # 5. avoid failing sabotaging
            return False
        
        # I am a spy who betrays everytime
        print('I am a spy who betrays everytime')
        return True

    def approve_new_mission(self, mission):
        '''
        mission is a list of agents to be sent on a mission. 
        '''
        for idx in range(len(self.failed_teams)):
            team = self.failed_teams[idx]
            fails = self.failed_nums[idx]
            ct = 0
            for agent in mission:
                if agent in team:
                    ct += 1
            if ct > len(team) - fails - 1:
                return False   
        return True



    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        '''
        self.missionct += 1
        pass

    def mission_outcome(self, mission, proposer, num_fails, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        num_fails is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        '''
        self.missionct = 0
        if mission_success == False:
            self.failed_teams.append(mission)
            self.failed_nums.append(num_fails)
            for agent in self.in_failed_teams:
                if agent[0] in mission:
                    agent[1] += 1
        

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        self.roundct = rounds_complete
        if missions_failed:
            self.spywins += 1
        else:
            self.resistantwins += 1
    
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        pass
