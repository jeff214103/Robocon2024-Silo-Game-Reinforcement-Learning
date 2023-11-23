from silo import VirtualSilo
import shutil
import sys
import os
import re
import numpy as np
import pickle
import random

class Player:
    PADDY_RICE_NUM = 12
    def __init__(self, name:str, marker:str, speed:float=None, freeze_time:int=None, success_rate:float=None) -> None:
        # Name: just player name for display
        # Marker: the mark placed inside the silo (Either 'b', 'r')
        # Speed: The interval of placing a paddy rice into silo (0-30)
        # Freeze Time: The start time of the player (0-170), more than 170 = lose

        if (not isinstance(name,str)):
            raise TypeError("name must have string type")
        if (not isinstance(marker,str)):
            raise TypeError("marker must have string type")
        # if (not isinstance(speed_profile,list)):
        #     raise TypeError("speed_profile must be in list type")
        if(len(marker) != 1 and (marker.lower() != 'b' or marker.lower() != 'r')):
            raise ValueError("marker must be either 'b' or 'r' ")
        self.name = name
        self._marker = marker.lower()

        # Determining the speed
        if (speed is not None):
            speed = max(speed, 0)
            speed = min(speed, 18)
            self._speed = speed
        else:
            self._speed = Player.generateSpeed()

        # Determining the drop rate
        if (success_rate is not None):
            success_rate = max(success_rate, 0.7)
            success_rate = min(success_rate, 1.0)
            self._success_rate = success_rate
        else:
            self._success_rate = Player.generateSuccessRate()

        # Determining the freeze time
        if (freeze_time == None):
            #A random time getting to zone 3
            self._freeze_time = random.randint(0, 170)
        else:
            freeze_time = max(freeze_time, 0)
            freeze_time = min(freeze_time, 170)
            self._freeze_time = freeze_time

        #Number of paddy rice the player hold
        self._paddy_rice = Player.PADDY_RICE_NUM

        #The next available time for placing the paddy rice
        self._next_place_time = 0

        #The last motion that the robot place the paddy rice
        self._last_place_col = None

        print("Initialized player {} (Mark: {}) with speed {}, Time to zone 3: {}, Success rate: {}".format(self.name, self._marker, self._speed, self._freeze_time, self._success_rate))

    @property
    def marker(self) -> str:
        return self._marker

    @property
    def paddy_rice_alert(self) -> bool:
        return self._paddy_rice <= Player.PADDY_RICE_NUM * self._success_rate

    #Generate a speed
    def generateSpeed(slowest:float=18, fastest:float=0) -> float:
        return random.randint(fastest,slowest)

    #Generate freeze time, meaning the time start zone 3
    def generateFreezeTime() -> int:
        return random.randint(0, 170)

    #Generate a success rate, meaning the rate that it successfully place the paddy rice into the silo
    def generateSuccessRate() -> float:
        available_rate = [0.7, 0.8, 0.9, 1.0]
        idx = np.random.choice(len(available_rate))
        return available_rate[idx]

    # #Generate a speed profile
    # def generateSpeedProfile(slowest:float=30, fastest:float=0) -> list:
    #     return sorted([random.uniform(fastest,slowest) for _ in range(5)])

    # Place function, will determine the speed and the next action time
    def place(self, silo:VirtualSilo, col:int, t:float) -> None:
        # No action case
        if (col < 0):
            return

        time_need = None
        # if (self._last_place_col == None):
        #     time_need = min(self._speed_profile)
        # else:
        #     time_need = self._speed_profile[abs(self._last_place_col - col)]

        # The time required to place a paddy rice
        time_need = self._speed

        # Next determine time
        self._next_place_time = t + time_need

        # Random determine if it could successfully place the paddy rice
        if (np.random.uniform(0, 1) <= self._success_rate):
            # Silo will handle the event, and refresh silo based on the decision
            silo.place(self._marker, col=col, next_place_time=self._next_place_time)

        # The action decided
        self._last_place_col = col

        # Remove one paddy rice
        self._paddy_rice -= 1
    
    def _getNextAvailableMove(self, silo:VirtualSilo, t:float) -> list:
        #Cool down time from action to next place time
        #-1 means cannot make any action
        # still under cool down or there is no more paddy rice
        if (t < self._next_place_time or self._paddy_rice == 0):
            return [-1]
        return silo.getAvailableMove() + [-1]

    def getMove(self, silo:VirtualSilo, t:float) -> int:
        raise RuntimeError("It is just an abstract class. Please choose either human or computer player")

    

class HumanPlayer(Player):
    def __init__(self, name:str, marker:str, speed:int, freeze_time:int=None, success_rate:float=None) -> None:
        super(HumanPlayer, self).__init__(name, marker, speed=speed, freeze_time=freeze_time, success_rate=success_rate)

    #Manual deciding factor
    def getMove(self, silo:VirtualSilo, t:float) -> int:
        if (t < self._freeze_time):
            return -1
        
        available_actions = self._getNextAvailableMove(silo=silo, t=t)
        if (len(available_actions) <= 1):
            return -1
        print("Player {} (Marker {}) Available Actions {} at Time {:.1f} (Remaining: {})".format(self.name, self.marker, available_actions, t, self._paddy_rice))
        while(True):
            data = input("Please input column (-1 for stay): ")
            if (data == ''):
                return -1
            try:
                data = int(data)
                if (data not in available_actions):
                    raise ValueError('Invalid input! ')                
                return data
            except Exception:
                print("Invalid Input! Avaiable Action: {}".format(available_actions))

class AIPlayer(Player):
    def __init__(self, name:str, marker:str, random_rate:int=0, speed:int=None, freeze_time:int=None, success_rate:float=None, verbose:bool=False) -> None:
        if (not os.path.exists('models')):
            os.mkdir('models')
        super(AIPlayer, self).__init__(name, marker, speed=speed, freeze_time=freeze_time, success_rate=success_rate)
        self.__original_speed = speed
        self.__original_freeze_time = freeze_time
        self.__original_success_rate = success_rate
        self.__verbose = verbose # determine if show debug message
        self.__states = []  # record all positions taken
        self.__learning_rate = 0.2
        self.__random_rate = random_rate #Only applicable when training
        self.__decay_gamma = 0.9

        if (os.path.exists('./models')):
            self.__game_dictionary = self.loadPolicy(verbos=verbose)
        
        if (self.__profile not in self.__game_dictionary):
            self.__game_dictionary[self.__profile] = {}

    @property
    def __profile(self):
        return 'S{}_R{:.1f}'.format(int(self._speed), self._success_rate)

    def __generateProfile(self, speed:int, success_rate:float) -> None:
        return 'S{}_R{:.1f}'.format(int(speed), success_rate)

    # Helper function to find out correct files
    def __isValidFilename(string):
        pattern = r'^AI_S\d+_R\d+\.\d+\.ai$'
        if re.match(pattern, string):
            return True
        return False
    
    # Helper function to get the speed trained for that file
    def __extractSpeedFromFilename(string):
        pattern = r'^AI_S(\d+)_R(\d+\.\d+)\.ai$'
        match = re.match(pattern, string)
        if match:
            int_value = int(match.group(1))
            float_value = float(match.group(2))
            return int_value, float_value
        return None
    
    # Hash state of the robot agent
    def __getGameDictionaryHashState(self, silo:VirtualSilo, t:float, action:str) -> str:
        # speed_profile = ["{:.1f}".format(speed) for speed in self._speed_profile]
        current_table_states = silo.getSiloHash(self._marker)
        # time = "{:.1f}".format(180-t)
        return f"{current_table_states}-{self.paddy_rice_alert}-{action}"
        # return f"{speed_profile}-{current_table_states}-{time}-{valid_actions}-{action}"

    # The movement decision
    def getMove(self, silo:VirtualSilo, t:float) -> None:
        if (t < self._freeze_time):
            return -1
        
        # Get all availabe actions
        available_actions = self._getNextAvailableMove(silo=silo, t=t)
        if (len(available_actions) > 1):
            if (self.__verbose == True):
                print("Player {} (Marker {}) Available Actions {} at Time {:.1f}".format(self.name, self.marker, available_actions, t))

        #Only one action availabe, that's mean not able to do the things
        else:
            # Means there is nothing to do
            return -1
        
        # Random Behaviour when for training
        if np.random.uniform(0, 1) <= self.__random_rate:
            idx = np.random.choice(len(available_actions))
            final_action = available_actions[idx]
        else:
            # Choose the max value choice
            max_value = -sys.maxsize - 1
            for action in available_actions:
                hash_state = self.__getGameDictionaryHashState(silo=silo, t=t, action=action)
                # hash_state = self.__getGameDictionaryHashState(silo=silo, t=t, valid_actions=available_actions, action=action)
                value = 0 if hash_state not in self.__game_dictionary[self.__profile] else self.__game_dictionary[self.__profile][hash_state]
                # print(f"Action: {action}, Value: {value}")
                if (value >= max_value):
                    max_value = value
                    final_action = action
        
        # Record the decision made
        self.__addState(self.__getGameDictionaryHashState(silo=silo, t=t, action=final_action))

        if (self.__verbose == True):
            print("Player {} (Marker {}) choose {} at Time {:.1f}".format(self.name, self.marker, final_action, t))

        return final_action

    def __addState(self, state) -> None:
        self.__states.append(state)

    #Feed reward to the player
    def feedReward(self, winner:str, score:dict) -> int:
        original_reward = None
        # Case not even place one paddy rice to the silo
        if (self._marker not in score):
            original_reward = -999
        # The player is the winner
        elif (winner == self._marker):
            original_reward = 10
        # There is no one to end game
        elif (winner == 'f' or winner == None):
            # Check if overwhelmed success
            overwhelmed = True
            for key in score:
                if (key == self._marker):
                    continue
                overwhelmed = False

                #Determine the score by comparison
                if (score[self._marker] > score[key]):
                    original_reward = 2
                elif (score[self._marker] < score[key]):
                    original_reward = -2
                else:
                    original_reward = 1
            #only self got score
            if (overwhelmed == True):
                original_reward = 2
        # Losed in the game, others win by end game
        else:
            original_reward = -10

        # Bring forward
        reward = original_reward
        for state in reversed(self.__states):
            if state not in self.__game_dictionary[self.__profile]:
                self.__game_dictionary[self.__profile][state] = 0
            self.__game_dictionary[self.__profile][state] += self.__learning_rate * (self.__decay_gamma * reward - self.__game_dictionary[self.__profile][state])
            reward = self.__game_dictionary[self.__profile][state]

        return original_reward

    # Reset the player
    def reset(self) -> None:
        self._paddy_rice = Player.PADDY_RICE_NUM
        self._next_place_time = 0
        self._last_place_col = None

        self.__states = []

        if (self.__original_speed == None):
            self._speed = Player.generateSpeed()

        if (self.__original_freeze_time == None):
            self._freeze_time = Player.generateFreezeTime()
        
        if (self.__original_success_rate == None):
            self._success_rate = Player.generateSuccessRate()
        
        if (self.__profile not in self.__game_dictionary):
            self.__game_dictionary[self.__profile] = {}

    # Save the model
    def savePolicy(self) -> None:
        game_dictionary = {}
        game_dictionary = self.loadPolicy()
        for profile in game_dictionary:
            if (profile not in self.__game_dictionary):
                self.__game_dictionary[profile] = {}
             
            for key in game_dictionary[profile]:
                #Average two learning Q values
                if (key not in self.__game_dictionary[profile]):
                    self.__game_dictionary[profile][key] = game_dictionary[profile][key]
                    
        
        for profile in self.__game_dictionary:
            fw = open('./models/AI_{}.ai'.format(profile), 'wb')
            pickle.dump(self.__game_dictionary[profile], fw)
            fw.close()

    # Load the model
    def loadPolicy(self, verbos=False) -> dict:
        game_dictionary = {}
        for filename in os.listdir('./models'):
            
            if (AIPlayer.__isValidFilename(filename) == False):
                continue
            
            speed, success_rate = AIPlayer.__extractSpeedFromFilename(filename)
            
            if (verbos == True):
                print("Reading {}... (Extracted as speed {}, success rate {})".format(filename, speed, success_rate))
            fr = open('./models/{}'.format(filename), 'rb')
            profile = self.__generateProfile(speed=speed, success_rate=success_rate)
            game_dictionary[profile] = pickle.load(fr)

            fr.close()

        return game_dictionary