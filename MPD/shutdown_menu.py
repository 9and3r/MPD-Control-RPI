import pygame
from dynamic_background import DynamicBackground

class ShutdownMenu:

    def __init__(self,surface):
	self.surface = surface
	self.touchList = {'SHUTDOWN': None, 'RESTART' : None}



    def showScreen(self):
	DynamicBackground().fillDynamicBackgroundColor(self.surface)
	x = 0
	y = 0
	myfont = pygame.font.SysFont(None, 50)
	mainText = myfont.render('Shutdown', 1, [255,255,255])
	self.surface.blit(mainText,(x,y))
	self.touchList['SHUTDOWN'] = pygame.Rect(x,y,mainText.get_rect().width,mainText.get_rect().height)
	y = mainText.get_rect().height
	mainText = myfont.render('Restart', 1, [255,255,255])
	self.surface.blit(mainText,(x,y))
	self.touchList['RESTART'] = pygame.Rect(x,y,mainText.get_rect().width,mainText.get_rect().height)
	return self.surface
