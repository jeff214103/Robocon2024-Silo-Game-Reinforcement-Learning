import heapq
import numpy as np
class Silo:
    def __init__(self) -> None:
        self._silo = [[None]*3 for _ in range(5)]

    # Return from sensors data
    def updateBoard(self, values:list) -> None:
        if (len(values) != 5):
            raise ValueError('There should only be 5 columns')
        if (len(values[0]) != 5):
            raise ValueError('There should only be 3 rows')
        
        for i in range(5):
            for j in range(3):
                self._silo[i][j] = values[i][j]

    # Compute the available moves from the current silo
    def getAvailableMove(self) -> list:
        positions = list()
        for i in range(5):
            if self._silo[i][2] == None:
                positions.append(i)
        return positions
    
    # For deep learning, based on user marker.  1 = self, -1 = opponent, 0 = nothing
    def getSiloHash(self, own:str) -> str:
        res = [[None]*3 for _ in range(5)]
        for i in range(5):
            for j in range(3):
                if (self._silo[i][j] == own):
                    res[i][j] = 1
                elif (self._silo[i][j] == None):
                    res[i][j] = 0
                else:
                    res[i][j] = -1
        return str(res)
    
#Virtual Game board
class VirtualSilo(Silo):
    def __init__(self) -> None:
        super(VirtualSilo, self).__init__()
        self.__update_list = []
    
    #When player start the decision to place the rice into the silo, there is a delay action from decision to action
    def place(self, player: str, col: int, next_place_time: float) -> None:
        #player in string
        #col in int, the column the rice being placed
        #delay is the decision to action time
        heapq.heappush(self.__update_list, (next_place_time, player, col))

    #It will try to refresh the board if the task list being update
    def refreshBoard(self, current_time:float) -> None:
        placed = False
        while (len(self.__update_list) > 0 and current_time >= self.__update_list[0][0]):
            time, player, col = heapq.heappop(self.__update_list)

            # Case if two player place at the same time, random either one successfully place inside
            if (len(self.__update_list) > 0 and time == self.__update_list[0][0]):
                time2, player2, col2 = heapq.heappop(self.__update_list)
                options = [player2, player]
                idx = np.random.choice(len(options))
                player = options[idx]
            
            placed = True
            for i in range(3):
                if (self._silo[col][i] == None):
                    self._silo[col][i] = player
                    break
        
        if (placed == True):
            print("Current Time: {:.1f}".format(current_time))
            print("=====PLACE======")
            self.printSilo()
            print("================")

    #Print board when update happens
    def printSilo(self) -> None:
        for j in reversed(range(3)):
            for i in range(5):
                print(f"|{self._silo[i][j] if self._silo[i][j] is not None else ' '}|", end=' ')
            print('')
            for i in range(5):
                print('---', end=' ')
            print('')

    #Decide if there is a winner
    def isEndGame(self) -> str:
        
        is_full = True
        need_detail_check_team = None

        #Check for the top rice
        top_count = {}
        for i in range(5):
            if (self._silo[i][2] not in top_count):
                top_count[self._silo[i][2]] = 0
            top_count[self._silo[i][2]] += 1

            #Top own by same team for 3 rice
            if (top_count[self._silo[i][2]] >= 3):
                need_detail_check_team = self._silo[i][2]
                
            if (self._silo[i][2] == None):
                is_full = False
        
        # There is no further 
        if (need_detail_check_team == None):
            return 'f' if is_full == True else None
        
        # Check if underneath is remained by the same color
        success_col_count = 0
        for i in range(5):
            if (self._silo[i][2] != need_detail_check_team):
                continue
            # Success for one column and break
            for j in range(2):
                if (self._silo[i][j] == need_detail_check_team):
                    success_col_count += 1
                    break
            
            if (success_col_count >= 3):
                return need_detail_check_team
        return 'f' if is_full == True else None
    
    # Get the scoring
    def scoreBoard(self) -> dict:
        score_baord = {}
        for i in range(5):
            for j in range(3):
                if (self._silo[i][j] != None):
                    if (self._silo[i][j] not in score_baord):
                        score_baord[self._silo[i][j]] = 0
                    score_baord[self._silo[i][j]] += 30
        return score_baord

