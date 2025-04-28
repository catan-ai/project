# import agent
import consts
import game
import pygame
import math
from board import Board
from draw import print_screen
from dice import Dice
from player import Player, ComputerPlayer
from agent import Agent

import sys
import argparse

board = Board()  # Pass the flag to the Board class
dice = Dice()
players = [ Agent(1) ] + [ ComputerPlayer(i) for i in range(2,5) ]
player_turn = 0
game.pick_settlements(players, board)
first_turn = True
winner = None