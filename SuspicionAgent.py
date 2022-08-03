from agent import Agent
import random

"""This agent is written in pair
Name: RAO YUNHUI Student number: 22551999
Name: XIE CHUNGUANG Student number: 22555027
"""
class SuspicionAgent(Agent):        
    '''implementation of suspicion score agent with reinforcement learning in resistance in CITS3001'''

    def __init__(self, name='SuspicionAgent'):
        '''
        Initialises the agent.
        The betray_probability should not be renewed when new game is started with same opponents so is initialized here
        '''
        self.name = name
        self.betray_probability = 0

    def new_game(self, number_of_players, player_number, spy_list):
        '''
        initialises the game, informing the agent of the 
        number_of_players, the player_number (an id number for the agent in the game),
        and a list of agent indexes which are the spies, if the agent is a spy, or empty otherwise
        missions_in_a_round is the number of missions in one round
        no_of_rounds is the number of rounds happened
        failed_missions is the number of failed missions
        last_vote is the vote for in last mission
        '''
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list
        self.suspicion = {}
        self.missions_in_a_round = 0
        self.no_of_rounds = 0
        self.failed_missions = 0
        self.last_vote = []
        for player in range(number_of_players):
            self.suspicion[player] = 0

    def is_spy(self):
        '''
        returns True iff the agent is a spy
        '''
        return self.player_number in self.spy_list

    def propose_mission(self, team_size, betrayals_required = 1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive) and number_of_players (exclusive)
        to be returned. 
        betrayals_required are the number of betrayals required for the mission to fail.
        resistance will propose a team with least suspicion score while spies will propose a team with enough spies to fail the mission
        '''
        team = []
        suspects = self.sort_suspects()
        suspects.reverse()
        team.append(self.player_number)
        if not self.is_spy():
            i = 0
            while len(team)<team_size:
                team.append(suspects[i])
                i += 1
        else:
            i = 0
            random.shuffle(self.spy_list)
            while len(team) < betrayals_required:
                if self.spy_list[i] not in team:
                    team.append(self.spy_list[i])
                i += 1
            for i in range(self.number_of_players):
                if len(team) < team_size and i not in team:
                    team.append(i)
        return team

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The function should return True if the vote is for the mission, and False if the vote is against the mission.
        '''
        #The agent will vote for the team when it is the leader or when it is the first mission, or when it is the 5th mission in a round
        if self.no_of_rounds == 0 or self.player_number == proposer or self.missions_in_a_round == 4:
            return True
#         As a spy, the agent will vote for a team with exactly the number of spies needed to fail a mission
#         or vote for a team with number of spies more than needed if this is last mission to win, if not, vote for 50%
#         and will vote against if the number of spies is not enough
        if self.is_spy():
            number_in_team = 0
            for spy in self.spy_list:
                if spy in mission:
                    number_in_team += 1
            if number_in_team == self.fails_required[self.number_of_players][self.no_of_rounds] or\
               (number_in_team > self.fails_required[self.number_of_players][self.no_of_rounds] and self.failed_missions == 2):
                return True
            elif number_in_team > self.fails_required[self.number_of_players][self.no_of_rounds]:
                return True
            else:
                return False
        #As a resistance, the agent will vote according to who is suspicious
        else:
            #The resistance will vote against the team without itself if the number of members is greater than half the number of players
            if len(mission) * 2 > self.number_of_players and self.player_number not in mission:
                return False
            suspects = self.sort_suspects()
            spy_count = self.spy_count[self.number_of_players]
            for i in range(spy_count - 1):
                if suspects[i] in mission and self.suspicion[suspects[i]] > 0:
                    return False
            return True

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for the mission, False otherwise).
        No return value is required or expected.
        The suspicion of one agent will raise if it vote for most suspicious agents
        '''
        self.last_vote = votes
        self.missions_in_a_round += 1
        suspects = self.sort_suspects()
        if suspects[0] in mission and self.suspicion[suspects[0]] >= 0:
            for i in votes:
                if i != suspects[0]:
                    self.suspicion[i] += 20
        if suspects[1] in mission and self.suspicion[suspects[1]] > 0:
            for i in votes:
                if i != suspects[1]:
                    self.suspicion[i] += 10
        

    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        The method should return True if this agent chooses to betray the mission, and False otherwise. 
        The agent as a spy should betray when only all spies in the mission need to betray to fail the mission
        (whether with a condition that number of people is greater than half is TBD)
        The agent will not betray if the number of spies is smaller than needed
        When the number of spies is greater than the number needed to betray, if only one need to betray, the proposer will betray
        or the spies betray in a probabilty
        '''
        if self.is_spy():
            num_spies = 0
            for i in mission:
                if i in self.spy_list:
                    num_spies += 1
            if num_spies == self.fails_required[self.number_of_players][self.no_of_rounds]:
                return True
            elif num_spies > self.fails_required[self.number_of_players][self.no_of_rounds]:
                if self.fails_required[self.number_of_players][self.no_of_rounds] == 1:
                    if self.player_number == proposer:
                        return True
                    elif proposer in self.spy_list:
                        return False
                    else:
                        probability_betray = 0.8 - (num_spies - self.fails_required[self.number_of_players][self.no_of_rounds]) * 0.1 + self.betray_probability
                        return random.random() < probability_betray
                        
            

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission. 
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player who proposed the mission.
        betrayals is the number of people on the mission who betrayed the mission, 
        and mission_success is True if there were not enough betrayals to cause the mission to fail, False otherwise.
        It iss not expected or required for this function to return anything.
        the suspicion score of an agent will change if it does suspicious actions
        '''
        if betrayals < len(mission):
            if mission_success:
                for i in mission:
                    self.suspicion[i] -= 20
                for i in self.last_vote:
                    self.suspicion[i] -= 10
                self.suspicion[proposer] -= 5
            else:
                for i in mission:
                    self.suspicion[i] += 100 * betrayals
                for i in self.last_vote:
                    self.suspicion[i] += 50 * betrayals
                self.suspicion[proposer] += 50 * betrayals
        else:
            for i in mission:
                self.suspicion[i] += 1000
            for i in self.last_vote:
                self.suspicion[i] += 200
                
        #reinforcement learning on probability to betray
        num_spies = 0
        for i in mission:
            if i in self.spy_list:
                num_spies += 1
        if self.is_spy() and num_spies >= self.fails_required[self.number_of_players][self.no_of_rounds]:
            if betrayals > self.fails_required[self.number_of_players][self.no_of_rounds]:
                self.betray_probability -= 0.01
            elif betrayals < self.fails_required[self.number_of_players][self.no_of_rounds]:
                self.betray_probability += 0.01

    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        self.no_of_rounds += 1
        self.missions_in_a_round = 0

    
    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        #nothing to do here
        pass
    
    def sort_suspects(self):
        players = []
        for i in range(self.number_of_players):
            players.append(i)
        suspects = sorted(players, key=lambda i:self.suspicion[i], reverse = True)
        suspects.remove(self.player_number)
        return suspects





