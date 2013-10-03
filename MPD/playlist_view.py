import pygame
import mpd
from dynamic_background import DynamicBackground

class Playlist_View:

	def __init__(self,surface,client,mpd_control):
		self.client=client
		self.surface = surface
		self.currentPage = 0
		self.maxInView = 5
		self.control = mpd_control
		self.touchList = {'PLAYLIST0': None, 'PLAYLIST1' : None, 'PLAYLIST2': None, 'PLAYLIST3' : None, 'PLAYLIST4' : None, 'PLAYLIST5' : None}
		self.showPlaylist = []


 	def mouseClick(self, mouseDownPos, mouseUpPos, longPress):
		for key in self.touchList:
			if longPress:
				for i in range(0, self.maxInView):
					if key == ('PLAYLIST'+str(i)):
						if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
							self.control.changeScreenVariable(1,True,self.playlists[i]['playlist'])
			else:
				for i in range(0, self.maxInView):
					if key == ('PLAYLIST'+str(i)):
						if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
							self.changePlayList(i)

	def changePlayList(self, i):
		self.client.clear()
		self.client.load(self.playlists[i]['playlist'])
		if self.client.status()['state'] != 'play':
			self.client.play()

	def getMax(self):
		if len(self.playlists) > self.maxInView:
			return self.maxInView 
		else:
			return len(self.playlists)	
	

	def swipe(self,swipe):
		pass	

	def showScreen(self):
		self.showPlaylist = []
		DynamicBackground().fillDynamicBackgroundColor(self.surface)
		self.playlists = self.client.listplaylists()
		myfont = pygame.font.SysFont(None, 30)
		mainText = myfont.render('Playlists', 1, [255,255,255])
		self.surface.blit(mainText,(self.surface.get_width()/2-mainText.get_rect().width/2, 0))
		y = mainText.get_height()
		for i in range(0,self.getMax()):
			self.showPlaylist.append(myfont.render(self.playlists[i]['playlist'], 1, [255,255,255]))
        		self.surface.blit(self.showPlaylist[i],(0, y))
			self.touchList[('PLAYLIST'+str(i))] = pygame.Rect(0,y,self.showPlaylist[i].get_rect().width,self.showPlaylist[i].get_rect().height)
			y = y + self.showPlaylist[i].get_height()
		return self.surface
