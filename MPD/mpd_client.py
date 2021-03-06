import requests
from fanart.music import Artist
from fanart.music import Album
import fanart
from fanart.core import Request
import os
import musicbrainz2.webservice as ws
import json
import thread
import random
import math
import time
import pygame
from dynamic_background import DynamicBackground
from ConfigParser import SafeConfigParser

class MPD:

    def __init__(self,surface,client):
	self.client=client
	self.setPluginVariables()
	self.surface = surface



    def showProgress(self, position, barsize, bordercolour, fillcolour, bgcolour):
        try:
            if position < 0 : position = 0
            if position > 1 : position = 1
        except:
            position = 0
        progress = pygame.Surface(barsize,flags=pygame.SRCALPHA)
        progress.fill(bgcolour)
        progresswidth = int(barsize[0] * position)
        pygame.draw.rect(progress,fillcolour,(0,0,progresswidth,barsize[1]))
        pygame.draw.rect(progress,bordercolour,(0,0,barsize[0],barsize[1]),1)
        return progress

    def setPluginVariables(self):

	self.touchList = {'PROGRESSBAR': None, 'PLAYBUTTON' : None, 'VOLUMEBAR': None, 'RANDOM' : None, 'REPEAT' : None, 'VOLUMEBUTTON' : None}
	self.lastVolume = 50
	self.lastTimeMusicBrainz = -1

	#Load MDP server config file
	fpath = os.path.expanduser("~")+'/.config/fanart_api'
	parser = SafeConfigParser()
	parser.read(fpath)
	self.fanarttvkey = parser.get('DEFAULT','fanart_api_key')
	os.environ.setdefault('FANART_APIKEY', self.fanarttvkey)

	self.backgroundshow = '1'
	self.covershow = '1'

	#Set position and size variables
	self.textStartX = 10
	self.textStartY = 20
	self.barSize = 20

	self.setNoSong()

    



    # Set No Song
    def setNoSong(self):
	self.currenttrack = None
        self.currentart = None
        self.currenttrackname = None
        self.currentartist = None
        self.currentalbum = None
	self.elapse = 0.0
	self.currenttime = 0.0
	self.background_ready = False
	self.artistId = None
	self.disc_ready = False
	self.albumId = None

    
    # Get current track information
    def getCurrentTrackInfo(self):
        self.currentSong = self.client.currentsong()
	self.currenttrack = self.currentSong['id']
        self.currentart = None
        self.currenttrackname = self.currentSong['title']
        self.currentartist = self.currentSong['artist']
        self.currentalbum = self.currentSong['album']
	self.currenttime = float(self.currentSong['time'])
	self.back_filepath = os.path.join("MPD/background", '%s%s' % (self.currentartist, '.jpg'))
	self.disc_filepath = os.path.join("MPD/disc", '%s%s' % (self.currentalbum, '.jpg'))
	self.artistId = None
	self.albumId = None

	#load images
	if self.backgroundshow == '1':
		self.loadBackground()
	if self.covershow == '1':
		self.loadDiscImage()

	
    
     
    def loadBackground(self):
	#see if there is a background
	#if there is not it will try to download
	try:
   		with open(self.back_filepath): pass
		self.currentart = pygame.transform.scale(pygame.image.load(self.back_filepath),(self.surface.get_width(),self.surface.get_height()))
		self.background_ready = True
	except IOError:
   		self.background_ready = False
		thread.start_new_thread(self.downloadBackground,())

    
    #find artistID in MusicBrainz
    def getArtistId(self):
	if self.lastTimeMusicBrainz != -1 and self.lastTimeMusicBrainz + 3 < time.time():
		time.sleep(1)
	if self.artistId == None:
		self.lastTimeMusicBrainz = time.time()
		q = ws.Query()

		#See if the there is more than an artist
		#If true it will use the first one
		if "," in self.currentartist:
			artistOne=self.currentartist.split(",")[0]
		else:
			artistOne=self.currentartist
		filter = ws.ArtistFilter(artistOne)
		artist=q.getArtists(filter)

		#Choose the artist with highest score
		artists=q.getArtists(filter)
		maxscore = 0
		doubt = False
		for artist in artists:
			if maxscore < artist.getScore():
				match_artist = artist.getArtist()
				maxscore = artist.getScore()
			else:
				if maxscore == artist.getScore():
					doubt = True
		if doubt:
			match_artist = self.findRealArtist(maxscore,artists).getArtist()			
		artistId = match_artist.getId()
		artistId = artistId.split("/")
		self.artistId=artistId[len(artistId)-1]

    	
    def findRealArtist(self,score,artists):
	#this takes artists who has that score
	#it will try to find the artist who has the current song
	found = False
	artist_found = None
	num = 0
	while not found and num<len(artists):
		artist = artists[num]

		if score == artist.getScore():
			if self.isRealArtist(artist.getArtist().getId()):
				found = True
				artist_found=artist
		num = num +1
	if found:
		return artist_found
	else:
		return artist

    def isRealArtist(self, idArtist):
	#looks if the artist has the curren track in MusicBrainz
	q = ws.Query()
	filter = ws.TrackFilter(self.currenttrackname,artistId=idArtist)
	tracks=q.getTracks(filter)
	if len(tracks) > 0:
		return True
	else:
		return False

    #get the albumId (ReleaseGroup ID) in MusicBrainz
    def getAlbumId(self):
	if self.lastTimeMusicBrainz != -1 and self.lastTimeMusicBrainz + 3 < time.time():
		time.sleep(1)
	if self.albumId == None:
		self.lastTimeMusicBrainz = time.time()
		q = ws.Query()

		#Filter the releases of MusicBrainz with the artistID
		filter = ws.ReleaseGroupFilter(self.currentalbum,artistId=self.artistId)
		releases=q.getReleaseGroups(filter)
		match_release = None

		#Choose the album with best match
		maxscore = 0
		for release in releases:
			if maxscore < release.getScore():
				maxscore = release.getScore()
				match_release = release.getReleaseGroup()

		#if the album was found get the id from MusiBrainz url
		if match_release != None:
			albumId = match_release.getId()
			albumId = albumId.split("/")
			self.albumId=albumId[len(albumId)-1]

    def downloadDiscImage(self):
	#Download cover from fanart.tv
	self.getArtistId()
	self.getAlbumId()
	target_album = None
	#Find album in the artist discs
	artist = Artist.get(id=self.artistId)
	for album in artist.albums:
		if album.mbid == self.albumId:
			target_album = album
	if target_album != None and len(target_album.covers)>0:
		disc_image = target_album.covers[0]
		with open(self.disc_filepath, 'wb') as fp:
				fp.write(disc_image.content())
	self.loadDiscImage()

    def loadDiscImage(self):
	#see if there is a disc cover
	#if there is not it will try to download
	try:
   		with open(self.disc_filepath): pass
		self.currentdisc = pygame.transform.scale(pygame.image.load(self.disc_filepath),(self.surface.get_width(),self.surface.get_height()))
		self.disc_ready = True
	except IOError:
   		self.disc_ready = False
		thread.start_new_thread(self.downloadDiscImage,())

    def downloadBackground(self):
	#Download background from fanart.tv
	try:
		self.getArtistId()
		#Start with fanart.tv
		artist = Artist.get(id=self.artistId)
		background = artist.backgrounds[0]
		with open(self.back_filepath, 'wb') as fp:
			fp.write(background.content())
		self.currentart = pygame.transform.scale(pygame.image.load(self.back_filepath),(self.surface.get_width(),self.surface.get_height()))
		self.loadBackground()
    	except:
		print "Error Downloading background"

    # See if the track has changed
    def hasTrackChanged(self):

	#Update the status of the client
	self.client_info = self.client.status()

	#See if it is playing

	if self.client_info['state'] == 'play':
		playing = 1
		#See if the track has changed
		if  'songid' in self.client_info:
			if self.currenttrack != self.client_info['songid']:
				self.getCurrentTrackInfo()
			self.elapse = float(self.client_info['elapsed'])
	else:
		if self.client_info['state'] == 'pause':
			playing = 0
		else:
			self.setNoSong()
			playing = -1
	return playing

    

    def nextTrack(self):
	self.client.next()

    def seekTrack(self, rect, mousePos):
	#Get sec to seek to
	sec = self.getPosBar(rect, mousePos, self.currenttime)
	self.client.seekcur(sec)

    def setVolume(self, rect, mousePos):
	vol = self.getPosBar(rect, mousePos, 100)
	self.client.setvol(vol)

    #Get the clicked position in the bar
    def getPosBar(self, rect, mousePos, maxValue):
	return (((mousePos[0]-rect.left)*100/rect.width) * int(maxValue)) /100

    def event(self, event):
	 if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_RIGHT):
		self.nextTrack()

    def play(self):
	if self.hasTrackChanged()==1:
		self.client.pause()
	else:
		self.client.play()

    def mute(self):
	if self.client_info['volume']=="0":
		self.client.setvol(self.lastVolume)
	else:
		self.lastVolume = int(self.client_info['volume'])
		self.client.setvol(0)

    def changeTrack(self ,next):
	if next ==3:
		self.client.next()
	elif next == 4:
		self.client.previous()


    def changeRepeat(self):
	if self.client_info['repeat'] == "0":
		self.client.repeat("1")
	else:
		self.client.repeat("0")

    def changeRandom(self):
	if self.client_info['random'] == "0":
		self.client.random("1")
	else:
		self.client.random("0")		

    def mouseClick(self, mouseDownPos, mouseUpPos,longPress):
	for key in self.touchList:
		if self.touchList[key] != None:
			if key == 'PROGRESSBAR':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					self.seekTrack(self.touchList[key], mouseDownPos)
			elif key == 'VOLUMEBAR':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					self.setVolume(self.touchList[key], mouseDownPos)
			elif key == 'PLAYBUTTON':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					self.play()
			elif key == 'REPEAT':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					self.changeRepeat()
			elif key == 'RANDOM':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					self.changeRandom()
			elif key == 'VOLUMEBUTTON':
				if self.touchList[key].collidepoint(mouseDownPos) and self.touchList[key].collidepoint(mouseUpPos):
					self.mute()
		

    def swipe(self, swipe):
	self.changeTrack(swipe)

    # Main function - returns screen to main script
    def showScreen(self):

	#paint background and cover
		
        if self.disc_ready: 
		self.surface.blit(self.currentdisc, (0,0))
	elif self.background_ready:
		self.surface.blit(self.currentart, (0,0))
	else:
		DynamicBackground().fillDynamicBackgroundColor(self.surface)
        myfont = pygame.font.SysFont(None, 30)
        mybigfont = pygame.font.SysFont(None, 38)
        mysmallfont = pygame.font.SysFont(None, 24)


        playing = self.hasTrackChanged()

        y = self.textStartY
        # get artist name
        artisttext = mybigfont.render(self.currentartist, 1, [255,255,255])
        self.surface.blit(artisttext, (self.textStartX,y))
	y = y + artisttext.get_rect().height	

        # get track name
       	tracktext = myfont.render(self.currenttrackname, 1, [255,255,255])
       	self.surface.blit(tracktext, (self.textStartX,y))       
	y = y + tracktext.get_rect().height
	
        # get track album
       	albumtext = myfont.render(self.currentalbum, 1, [255,255,255])
       	self.surface.blit(albumtext, (self.textStartX,y))  


       	# Show progress bar and time if a song is playing
	if playing==1:
        	trackposition = self.elapse / self.currenttime
		progressSurface = self.showProgress(trackposition,(self.surface.get_width(),self.barSize),(255,255,255),(0,0,144,150),(0,0,0,120))
		
		y = self.surface.get_height()- (2*self.barSize)
        	self.surface.blit(progressSurface,(0,y))
		self.touchList['PROGRESSBAR'] = pygame.Rect(0,y,self.surface.get_width(),self.barSize)
                	    
        	elapsem, elapses = divmod(int(self.elapse),60)
        	elapseh, elapsem = divmod(elapsem, 60)
        	elapsestring = "%02d:%02d" % (elapsem, elapses)
        	if elapseh > 0 : elapsestring = elapsestring + "%d:" % (elapseh)
                		    
        	durationm, durations = divmod(int(self.currenttime),60)
        	durationh, durationm = divmod(durationm, 60)             
        	durationstring = "%02d:%02d" % (durationm, durations)
        	if durationh > 0 : durationstring = durationstring + "%d:" % (durationh)    
                	    
        	progressstring = "%s / %s" % (elapsestring, durationstring)
                	    
       		progresstext = myfont.render(progressstring, 1, (255,255,255))
        	self.surface.blit(progresstext, (self.surface.get_width()/2-progresstext.get_rect().width/2, y))


		#Show Playback controls on the screen
		x = 0
		playtext = myfont.render('Pause', 1, [255,255,255])
		#Put a little bit darker to see the text in bright images
		topBack = pygame.Surface((self.surface.get_rect().width,playtext.get_rect().height),flags=pygame.SRCALPHA)
		topBack.fill([0,0,0,120])
		self.surface.blit(topBack, (0, 0))

		if self.client_info['repeat']!='1':
			repeattext = myfont.render('Repeat', 1, [255,255,255])
		else:
			repeattext = myfont.render('Repeat', 1, [30,200,40])
		x = x + playtext.get_rect().width+15
		self.surface.blit(repeattext, (x,0)) 
		self.touchList['REPEAT'] = pygame.Rect(x,0,repeattext.get_rect().width,repeattext.get_rect().height) 
		if self.client_info['random']!='1':
			randomtext = myfont.render('Random', 1, [255,255,255])
		else:
			randomtext = myfont.render('Random', 1, [30,200,40])
		x = x + repeattext.get_rect().width+15
		self.surface.blit(randomtext, (x,0))
		self.touchList['RANDOM'] = pygame.Rect(x,0,randomtext.get_rect().width,randomtext.get_rect().height)
		x = x + randomtext.get_rect().width+15

		#Show volume
		if self.client_info['volume']!='0':
			volumetext = myfont.render('Mute', 1, [255,255,255])
		else:
			volumetext = myfont.render('Mute', 1, [30,200,40])
		self.surface.blit(volumetext, (x,0))
		self.touchList['VOLUMEBUTTON'] = pygame.Rect(x,0,volumetext.get_rect().width,volumetext.get_rect().height)
		x = 0
		y = self.surface.get_height()- self.barSize
		volume = float(self.client_info['volume'])/100.0
		volumeBar = self.showProgress(volume,(self.surface.get_width(),self.barSize),(255,255,255),(0,0,144,100),(0,0,0,100))
        	self.surface.blit(volumeBar,(x,y))
		self.touchList['VOLUMEBAR'] = pygame.Rect(x,y,self.surface.get_width(),self.barSize)

	else:
		playtext = myfont.render('Play', 1, [255,255,255])
        self.surface.blit(playtext, (0,0)) 
	self.touchList['PLAYBUTTON'] = pygame.Rect(0,0,playtext.get_rect().width,playtext.get_rect().height)
        return self.surface
