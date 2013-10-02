import pygame
import mpd
from dynamic_background import DynamicBackground
from text_control import Text_Control

class Song_View:

	def __init__(self,surface,client):
		self.client=client
		self.surface = surface
		self.currentPage = 0
		self.maxInView = 0
		self.touchList = {}
		self.currentSong = 0


 	def mouseClick(self, mouseDownPos, mouseUpPos, longPress):
		for key in self.touchList:
			if longPress:
				continue
			else:
				for i in range(0, self.maxInView):
					if key == ('SONG'+str(i)):
						if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
							self.changeSong(i)

	def setVariable(self,playList):
		self.playlist = playList
		self.setSongs()
	
	def changeSong(self, i):
		i = self.currentSong + i
		if i < len(self.songs):
			self.client.clear()
			self.client.addid(self.songs[i]['file'])
			self.client.load(self.playlist)
			if self.client.status()['state'] != 'play':
				self.client.play()

	def swipe(self,swipe):
		if swipe == 1:
			self.currentSong = self.currentSong + self.maxInView
			if self.currentSong > len(self.songs):
				self.currentSong = self.currentSong - self.maxInView
			self.setSongs()
		elif swipe == 2:
			self.currentSong = self.currentSong - self.maxInView
			if self.currentSong < 0:
				self.currentSong = 0
			self.setSongs()
		
	def getMax(self):
		return len(self.songs)	

	def setSongs(self):
		songList = []
		self.myfont = pygame.font.SysFont(None, 30)
		self.mainText = self.myfont.render('Songs in '+self.playlist, 1, [255,255,255])
		self.songs = self.client.listplaylistinfo(self.playlist)
		y = self.mainText.get_height()
		exitLoop = False
		i = self.currentSong
		showNum = 0
		while not exitLoop and i < self.getMax():
			current = Text_Control().changeText(('SONG'+str(showNum)), self.songs[i]['title'], 0, y,-1,self.surface,self.myfont)
			if (current.get_rect().height+y < self.surface.get_height()):
				songList.append(current)
				self.touchList[('SONG'+str(showNum))] = pygame.Rect(0,y,songList[showNum].get_rect().width,songList[showNum].get_rect().height)
				y = y + songList[showNum].get_height()
				i = i +1
				showNum = showNum +1
			else:
				self.maxInView = i - self.currentSong
				exitLoop = True
		
	
	def showScreen(self):
		DynamicBackground().fillDynamicBackgroundColor(self.surface)
		self.myfont = pygame.font.SysFont(None, 30)
		self.songs = self.client.listplaylistinfo(self.playlist)
		self.mainText = self.myfont.render('Songs in '+self.playlist, 1, [255,255,255])
		self.surface.blit(self.mainText,(self.surface.get_width()/2-self.mainText.get_rect().width/2, 0))
		for i in range(0,self.maxInView):
			tc = Text_Control()
			tc.printKey('SONG'+str(i))
		return self.surface
