import torch
#import pyspiel
import gym
import argparse
from matplotlib import pyplot as plt
from copy import copy
import numpy as np
import time

from policy_network import PolicyNetwork
from value_network import ValueNetwork


class TeenyGo(object):

    def __init__(self, vn=None, pn=None, mcts_width=5, mcts_depth=1):

        self.value_network = vn
        self.policy_network = pn

        self.mcts_width = mcts_width
        self.mcts_depth = mcts_depth

    def generate_game(self):

        parser = argparse.ArgumentParser(description='Go Simulation')
        #parser.add_argument('--randai', action='store_true')
        parser.add_argument('--boardsize', type=int, default=9)
        args = parser.parse_args()

        go_env = gym.make('gym_go:go-v0',size=args.boardsize,reward_method='real')

        return go_env

    def copy_game(self, game):
        return deepcopy(game)

    def get_move(self, state, valid_moves):
        p = self.policy_network.forward(state).detach().numpy()
        p = p*valid_moves
        return np.argmax(p)


    def get_state(self, board_sim):

        pass

    def get_winrate(self, x):
        pass

    def mcts(self, game, width, depth):

        # MCTS

        # take game, mcts width, and mcts depth
        # make move prediction from game
        # simulate n=width moves
        # for each sim apply MCTS
        # if depth is reached return V


        x = game.get_state()[0:3]

        if depth == 0:
            v = self.value_network.forward(x).detach().numpy()
            return 


        # get policy
        p = self.policy_network.forward(x).detach().numpy()

        # remove invalid moves
        p = p*game.get_valid_moves()

        # get best moves
        moves = self.get_best_moves(p, width)


        # get simulated moves
        sims = self.get_simulated_games(game, moves)

        values = []
        # test each sim
        for sim in sims:
            values.append(self.mcts_step(sim, width, depth-1))

        if depth==self.mcts_depth:
            return moves[np.argmax(values)]

        return np.max(values)

    def get_best_moves(self, p, width):
        
        moves = []

        for i in range(width):
            moves.append(np.argmax(p))
            p[0][moves[-1]] = 0

        return moves

    def get_best_single_move(self, board):

        state = board.get_state()[0:3].reshape([1, 3, 9, 9])

        valid_moves = board.get_valid_moves()
        p = self.policy_network.forward(state).detach().numpy()
        p = p*valid_moves
        moves = self.get_best_moves(p, 10)

        sims = []
        values = []
        for i, move in enumerate(moves):
            sims.append(copy(board))
            state, reward, done, _ = sims[-1].step(move)
            state = state[0:3].reshape([1, 3, 9, 9])
            values.append(self.value_network.forward(state).detach().numpy()[0][0]*-1)

        #print(values)
        return moves[np.argmax(values)]

            

    def get_simulated_games(self, game, moves):
        
        sims = []

        for move in moves:
            sims.append(self.copy_game(game))
            sims[-1].step(move)

        return sims

def main():

    policy_net = PolicyNetwork(alpha = 0.001,num_res=12, num_channel=256 ,in_chan=3)
    policy_net.load_state_dict(torch.load("PN-R12-C256-P7.pt", map_location={'cuda:0': 'cpu'}))
    value_net = ValueNetwork(alpha = 0.001, num_res=12, num_channel=256 ,in_chan=3)
    value_net.load_state_dict(torch.load("VN-R12-C256-VFinal.pt", map_location={'cuda:0': 'cpu'}))
    teeny_go = TeenyGo(pn=policy_net, vn=value_net)

    parser = argparse.ArgumentParser(description='Demo Go Environment')
    parser.add_argument('--randai', action='store_true')
    parser.add_argument('--boardsize', type=int, default=9)
    args = parser.parse_args()

    wins = 0
    for i in range(10):

        go_env = gym.make('gym_go:go-v0',size=args.boardsize,reward_method='heuristic')
        done = False

        rewards = []

        #while not done:
        for i in range(40):


            """
            state = go_env.get_state()[0:3].reshape([1, 3, 9, 9])
            valid_moves = go_env.get_valid_moves()
            t = time.time()
            #action = go_env.render('terminal')
            action = teeny_go.get_move(state, valid_moves)

              
            print(value_net.forward(state))
            print("Time:", time.time()-t)
            """
            action = teeny_go.get_best_single_move(go_env)

            go_env.render("human")

            try:
                state, reward, done, _ = go_env.step(action)
            except Exception as e:
                print(e)
                continue
            if True:
                if go_env.game_ended():
                    break
                action = go_env.uniform_random_action()
                state, reward, done, _ = go_env.step(action)


        if go_env.get_winning() == 1:
            print("Teeny-Go Won!")
            wins += 1

        else: print("Teeny-Go Lost!")

    print("Teeny-Go Won {} Games".format(wins))
        

if __name__ == "__main__":
    main()
