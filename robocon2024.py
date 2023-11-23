from argparse import ArgumentParser
from silo import VirtualSilo
from player import HumanPlayer
from player import AIPlayer
import sys
import os
from tqdm import tqdm
import traceback
import time

GAMETIME = 180
class Robocon2024Game:
    def __init__(self, player:list):
        if (len(player) != 2):
            raise ValueError("There can only be two player in the game")
        if (player[0].marker == player[1].marker):
            raise RuntimeError("Two player contains the same mark")
        self.player = player
    
    def start(self):
        self.silo = VirtualSilo()
        start_time = 0
        current_time = 0

        print("================")
        self.silo.printSilo()
        print("================")

        #Either it is 3 mins game or it has Winner
        while self.silo.isEndGame() == None and current_time - start_time < GAMETIME:
            self.silo.refreshBoard(current_time=current_time)
            for i in range(2):
               move = self.player[i].getMove(silo=self.silo, t=current_time)
               self.player[i].place(silo=self.silo, col=move, t=current_time)
            
            current_time += 0.1
            self.silo.refreshBoard(current_time=current_time)
        
        print("================")
        self.silo.printSilo()
        print("================")
        winner = self.silo.isEndGame()
        score = self.silo.scoreBoard()
        print(f"{'Winner '+ winner if winner != 'f' and winner != None else 'No one end Game'}")
        print(score)
        #Return which player win
        return winner, score
       
    def trainAI(self, round):
        if (not isinstance(round, int)):
            raise ValueError("Round must have int type")
        if (all (type(player) != AIPlayer for player in self.player)):
            raise RuntimeError("train AI must have all player to be AIPlayer class")
        train_count = {self.player[0].name: {'win':0, 'lose':0, 'draw':0}, self.player[1].name:  {'win':0, 'lose':0, 'draw':0}}
        try:
            for i in tqdm(range(round)):
                sys.stdout = open(os.devnull, 'w')
                print("======= Round {} =======".format(i))
                winner, score = self.start()
                
                for i in range(2):
                    reward = self.player[i].feedReward(winner=winner, score=score)
                    print(f"{self.player[i].name} : {reward}")

                    if (reward == 1):
                        train_count[self.player[i].name]['draw'] += 1
                    elif (reward >= 1):
                        train_count[self.player[i].name]['win'] += 1     
                    elif (reward <= 1):
                        train_count[self.player[i].name]['lose'] += 1

                    self.player[i].reset()
                # input()
                # time.sleep(0.5)
                sys.stdout = sys.__stdout__
            
            print(train_count)
            print("Saving Policy...")
            self.player[0].savePolicy()
            self.player[1].savePolicy()
        except KeyboardInterrupt:
            sys.stdout = sys.__stdout__
            print(train_count)
            print("Trying to save player policy before end..")
            try:
                self.player[0].savePolicy()
                self.player[1].savePolicy()
            except Exception as e:
                print(traceback.format_exc())
                print(e)


if (__name__ == "__main__"):
    parser = ArgumentParser(description="Robocon 2024 AI Training")

    subparsers = parser.add_subparsers(dest="mode", required=True, help="sub commands")
    train_parser = subparsers.add_parser("train", help="AI Training")
    play_parser = subparsers.add_parser("play", help="Play a game")

    train_parser.add_argument("--iteration",type=int, help="Numbers of epoch would like to train", dest="epoch", default=10000)
    train_parser.add_argument("--rs", type=int, help="red player speed (from 0 to 18)", dest="red_player_speed")
    train_parser.add_argument("--rf", type=int, help="red player start time (from 0 to 170)", dest="red_player_freeze_time")
    train_parser.add_argument("--rr", type=float, help="red player success rate (from 0.7 to 1.0)", dest="red_player_rate")
    train_parser.add_argument("--bs", type=int, help="blue player speed (from 0 to 18)", dest="blue_player_speed")
    train_parser.add_argument("--bf", type=int, help="blue player start time (from 0 to 170)", dest="blue_player_freeze_time")
    train_parser.add_argument("--br", type=float, help="blue player success rate (from 0.7 to 1.0)", dest="blue_player_rate")

    play_parser.add_argument("--r", type=int, help="red player (0: AI/1: player)", dest="red_player", required=True)
    play_parser.add_argument("--rs", type=int, help="red player speed (from 0 to 18)", dest="red_player_speed")
    play_parser.add_argument("--rf", type=int, help="red player zone 3 start time (from 0 to 170)", dest="red_player_freeze_time")
    play_parser.add_argument("--rr", type=float, help="red player success rate (from 0.7 to 1.0)", dest="red_player_rate")
    play_parser.add_argument("--b", type=int, help="blue player (0: AI/1: player)", dest="blue_player", required=True)
    play_parser.add_argument("--bs", type=int, help="blue player speed (from 0 to 18)", dest="blue_player_speed")
    play_parser.add_argument("--bf", type=int, help="blue player zone 3 start time (from 0 to 170)", dest="blue_player_freeze_time")
    play_parser.add_argument("--br", type=float, help="blue player success rate (from 0.7 to 1.0)", dest="blue_player_rate")

    opt = parser.parse_args()

    if(opt.mode == "train"):
        players = [
            AIPlayer('Red','r', 0.8, speed=opt.red_player_speed, freeze_time=opt.red_player_freeze_time, success_rate=opt.red_player_rate, verbose=True),
            AIPlayer('Blue','b', 0.8, speed=opt.blue_player_speed, freeze_time=opt.blue_player_freeze_time, success_rate=opt.blue_player_rate, verbose=True)
        ]
        game = Robocon2024Game(players)
        game.trainAI(opt.epoch)

    elif(opt.mode == "play"):
        players = []
        if (opt.red_player == 0):
            players.append(AIPlayer('com_1','r', speed=opt.red_player_speed, freeze_time=opt.red_player_freeze_time, success_rate=opt.red_player_rate, verbose=True))
        elif (opt.red_player == 1):
            players.append(HumanPlayer('1','r', speed=opt.red_player_speed, freeze_time=opt.red_player_freeze_time, success_rate=opt.red_player_rate))
        if (opt.blue_player == 0):
            players.append(AIPlayer('com_2','b', speed=opt.blue_player_speed, freeze_time=opt.blue_player_freeze_time, success_rate=opt.blue_player_rate, verbose=True))
        elif (opt.blue_player == 1):
            players.append(HumanPlayer('2','b', speed=opt.blue_player_speed, freeze_time=opt.blue_player_freeze_time, success_rate=opt.blue_player_rate))
        Robocon2024Game(players).start()
