import pygame
from dynamic_background import DynamicBackground
import os

class ShutdownMenu:

    def __init__(self,surface,control):
	self.surface = surface
	self.touchList = {}
	self.control = control



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
	y = y + mainText.get_rect().height
	mainText = myfont.render('Update', 1, [255,255,255])
	self.surface.blit(mainText,(x,y))
	self.touchList['UPDATE'] = pygame.Rect(x,y,mainText.get_rect().width,mainText.get_rect().height)
	y = y + mainText.get_rect().height
	mainText = myfont.render('Back', 1, [255,255,255])
	self.surface.blit(mainText,(x,y))
	self.touchList['BACK'] = pygame.Rect(x,y,mainText.get_rect().width,mainText.get_rect().height)
	y = y + mainText.get_rect().height
	mainText = myfont.render('Exit', 1, [255,255,255])
	self.surface.blit(mainText,(x,y))
	self.touchList['EXIT'] = pygame.Rect(x,y,mainText.get_rect().width,mainText.get_rect().height)
	return self.surface

    def swipe(self, swipe):
	pass
	
    def mouseClick(self, mouseDownPos, mouseUpPos, longPress):
		for key in self.touchList:
			if key == 'UPDATE':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					os.system('./update.sh')
			elif key == 'EXIT':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					exit()
			elif key == 'SHUTDOWN':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					os.system('sudo shutdown now')
			elif key == 'RESTART':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					os.system('sudo shutdown -r now')
			elif key == 'BACK':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					self.control.changeScreen(1,True)





