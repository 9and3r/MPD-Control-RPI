#!/usr/bin/python
# touchv5
# Texy 1/6/13

import pygame, sys, os, time
from pygame.locals import *
from MPD.mpd_screen_control import MPD_Control
import time

from evdev import InputDevice, list_devices


def exit():
	mpd.exit()
	pygame.quit()
	sys.exit()

def mouseLongPress(downTime, upTime):
	if (upTime - downTime) > 0.2:
		return True
	else:
		return False


mousePos = (0,0)

devices = map(InputDevice, list_devices())
eventX=""
for dev in devices:
    if dev.name == "ADS7846 Touchscreen":
        eventX = dev.fn
print eventX

os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = eventX

FPS = 30

pygame.init()

# set up the window
screen = pygame.display.set_mode((320, 240), 0, 32)
pygame.display.set_caption('MPD')

#Set up the mpd
mpd = MPD_Control()
mpd.prepare(screen)

running = True
# run the game loop
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
	    exit()
            running = False  
        elif event.type == pygame.MOUSEBUTTONDOWN:
	    mousePos = pygame.mouse.get_pos()
	    downTime = time.time()
	elif event.type == pygame.MOUSEBUTTONUP:
	    mpd.mouseClick( mousePos, pygame.mouse.get_pos(),mouseLongPress(downTime,time.time()))
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
    screen = mpd.showScreen()
    pygame.display.flip()
    pygame.display.update()
    pygame.time.Clock().tick(FPS)

