import pygame
import mpd
from dynamic_background import DynamicBackground

class Playlist_View:

	def __init__(self,surface,client):
		self.client=client
		self.surface = surface
		self.currentPage = 0
		self.touchList = {'PLAYLIST0': None, 'PLAYLIST1' : None, 'PLAYLIST2': None, 'PLAYLIST3' : None, 'PLAYLIST4' : None, 'PLAYLIST5' : None}

	def showScreen(self):
		playList = []
		DynamicBackground().fillDynamicBackgroundColor(self.surface)
		self.playlists = self.client.listplaylists()
		myfont = pygame.font.SysFont(None, 30)
		y = 0
		for i in range(0,5):
			playList.append(myfont.render(self.playlists[i]['playlist'], 1, [255,255,255]))
			self.touchList[('PLAYLIST'+str(i))] = playList[i]
        		self.surface.blit(playList[i],(0, y))
			y = y + playList[i].get_height()
		return self.surface