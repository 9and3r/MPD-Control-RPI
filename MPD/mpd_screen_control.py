import mpd
import thread
import logging
import time
import math
import pygame
from playlist_view import Playlist_View
from mpd_client2 import MPD
from dynamic_background import DynamicBackground

class MPD_Control:

	def __init__(self, surface):
		self.surface = surface
		# Connect to MDP server
		self.ip = 'localhost'
		self.port = '6600'
		logging.basicConfig()
		self.client = mpd.MPDClient()
		self.connected = False
		thread.start_new_thread(self.connectMDPserver,())
		self.screens = []
		self.screens.append(MPD(self.surface,self.client))
		self.screens.append(Playlist_View(self.surface,self.client))
		self.currentScreen = 0

	def connectMDPserver(self):
		# Connect to MDP server
		try:
			self.client.connect(self.ip, self.port)
			self.connected = True
		except:
			print "Could not connect to MDP server. Check configuration"
			self.connected = False
			time.sleep(10)
			self.connectMDPserver()

		
	def mouseClick(self, mouseDownPos, mouseUpPos, longPress):
		swipe = self.swipe(mouseDownPos, mouseUpPos)
		if swipe == -1:
			self.screens[self.currentScreen].mouseClick(mouseDownPos, mouseUpPos,longPress)
		elif swipe==1:
			if self.currentScreen ==0:
				self.currentScreen = self.currentScreen + 1
		elif swipe ==3:
			if self.currentScreen ==0:
				self.screens[self.currentScreen].swipe(swipe)
			else:
				self.currentScreen = self.currentScreen + 1
		elif swipe ==4:
			if self.currentScreen == 0:
				self.screens[self.currentScreen].swipe(swipe)
			else:
				self.currentScreen = self.currentScreen -1

	def swipe(self, mouseDownPos, mouseUpPos):
		if(math.fabs(mouseDownPos[0]-mouseUpPos[0])<50):
			if(mouseDownPos[1]-mouseUpPos[1]>50):
				return 1
			else:
				if(mouseUpPos[1]-mouseDownPos[1]>50):
					return 2

				else:
					return -1
		elif (math.fabs(mouseDownPos[1]-mouseUpPos[1])<50):
			if(mouseDownPos[0]-mouseUpPos[0]>50):
				return 3
			else:
				if(mouseUpPos[0]-mouseDownPos[0]>50):
					return 4

				else:
					return -1
		else:
			return -1


	def showScreen(self):
		if self.connected:
			return self.screens[self.currentScreen].showScreen()
		else:
			return self.showNotConnected()

	def showNotConnected(self):
		DynamicBackground().fillDynamicBackgroundColor(self.surface)
		myfont = pygame.font.SysFont(None, 30)
		nowtext = myfont.render("Could not connect to MPD server", 1, (255,255,255))
        	self.surface.blit(nowtext, (0, 0))
		nowtext = myfont.render("Check the configuration", 1, (255,255,255))
        	self.surface.blit(nowtext, (0, 50))
		nowtext = myfont.render("Anyway the software is trying to connect", 1, (255,255,255))
        	self.surface.blit(nowtext, (0, 100))
		return self.surface

	def exit(self):
		self.client.disconnect() 
