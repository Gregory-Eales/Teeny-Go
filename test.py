from utils.tester import Tester
from teeny_go.teeny_go_network import TeenyGoNetwork

import torch

import time


tgn1 = TeenyGoNetwork(num_channels=32, num_res_blocks=3, is_cuda=False)
tgn2 = TeenyGoNetwork(num_channels=64, num_res_blocks=5, is_cuda=False)
#tgn3 = TeenyGoNetwork(num_channels=64, num_res_blocks=5, is_cuda=False)

tgn1.load_state_dict(torch.load("models/Model-R3-C32/Model-R3-C32-V8.pt"))
tgn2.load_state_dict(torch.load("models/Model-R5-C64/Model-R5-C64-V7.pt"))
#tgn3.load_state_dict(torch.load("models/Model-R5-C64/Model-R5-C64-V2.pt"))


tester = Tester()


tester.play_through_games(tgn1, tgn2, num_games=100)
