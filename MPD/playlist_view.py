import pygame
import mpd
from dynamic_background import DynamicBackground

class Playlist_View:

	def __init__(self,surface,client):
		self.client=client
		self.surface = surface
		self.currentPage = 0
		self.touchList = {'PLAYLIST0': None, 'PLAYLIST1' : None, 'PLAYLIST2': None, 'PLAYLIST3' : None, 'PLAYLIST4' : None, 'PLAYLIST5' : None}


 	def mouseClick(self, mouseDownPos, mouseUpPos, longPress):
		for key in self.touchList:
			if longPress:
				continue
			else:
				for i in range(0, 5):
					if key == ('PLAYLIST'+str(i)):
						if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
							self.changePlayList(i)

	def changePlayList(self, i):
		self.client.clear()
		self.client.load(self.playlists[i]['playlist'])
		if self.client.status()['state'] != 'play':
			self.client.play()

	
	def showScreen(self):
		playList = []
		DynamicBackground().fillDynamicBackgroundColor(self.surface)
		self.playlists = self.client.listplaylists()
		myfont = pygame.font.SysFont(None, 30)
		y = 0
		for i in range(0,5):
			playList.append(myfont.render(self.playlists[i]['playlist'], 1, [255,255,255]))
        		self.surface.blit(playList[i],(0, y))
			self.touchList[('PLAYLIST'+str(i))] = pygame.Rect(0,y,playList[i].get_rect().width,playList[i].get_rect().height)
			y = y + playList[i].get_height()
		return self.surface
