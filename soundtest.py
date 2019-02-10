import time
import importlib
import pygame

def play(filename='./cartoon-telephone_daniel_simion.mp3', blocking=True):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(loops=-1)

    # print([player.get_state()])

play()

input("")