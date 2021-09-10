#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This file contains the python code used to interface with the Twitch
chat. Twitch chat is IRC-based, so it is basically an IRC-bot, but with
special features for Twitch, such as congestion control built in.
"""
from __future__ import print_function

import os
import time

from library.twitch import TwitchChatStream

# defines
APP_ICON = os.path.dirname( __file__ ) + '/resources/logo.png'
APP_TITLE = 'StreamFlash'
APP_VERSION = '1.0'

# globals
app = None
tcs = None
win = None
last = 0
screen = 0
options = { 'username': '', 'oauth': '', 'screen': 0, 'duration': 400 }

def systray( app ):
	global APP_ICON, APP_TITLE, APP_VERSION

	from PyQt5.QtGui import QIcon
	from PyQt5.QtWidgets import QMenu, QSystemTrayIcon

	tray = QSystemTrayIcon( app )
	tray.setIcon( QIcon( APP_ICON ) )

	menu = QMenu()

	action = menu.addAction( '%s v%s' % ( APP_TITLE, APP_VERSION ) )
	action.setEnabled( False )

	menu.addSeparator()

	action = menu.addAction( 'Reconnect' )
	action.triggered.connect( lambda: connect( send_flash, send_error, verbose = True ) )

	action = menu.addAction( 'Next Screen' )
	action.triggered.connect( lambda: next_screen() )

	menu.addSeparator()

	action = menu.addAction( 'Exit' )
	action.triggered.connect( lambda: app.quit() )

	tray.setContextMenu( menu )
	tray.setVisible( True )

	return ( tray )

def connect( success = None, error = None, verbose = False ):
	global tcs

	connected = False
	if tcs:
		try:
			tcs.connect()
		except:
			if verbose:
				print( 'connexion failed' )

			if error:
				error()
		else:
			connected = True
			if verbose:
				print( 'connected' )

			if success:
				success()

	return ( connected )

def listener( username, oauth, success = None, error = None, verbose = False ):
	global tcs

	def reconnect():
		connected = False
		for i in range( 3 ):
			time.sleep( .1 )
			connected = connect()
			if connected:
				break

		return ( connected )

	try:
		tcs = TwitchChatStream( username.lower(), oauth, verbose )
	except:
		print( 'connexion failed' )
	else:
		connected = reconnect()
		if connected:
			print( 'connected' )
			if success:
				success()

			while True:
				receive = []
				time.sleep( 1 )

				try:
					receive = tcs.twitch_receive_messages()
				except ( ConnectionResetError, ConnectionAbortedError ):
					connected = reconnect()
					if not connected:
						print( 'connexion lost' )
						if error:
							error()

				if receive:
					print( receive )
					if success:
						success()
		else:
			print( 'connexion failed' )

def next_screen( force = None, without_flash = False ):
	global app, win, screen

	screen += 1
	screens = app.screens()
	if type( force ) is int and force >= 0:
		screen = force

	screen = ( screen % len( screens ) )
	geometry = screens[ screen ].availableGeometry()

	win.windowHandle().setScreen( screens[ screen ] );
	win.setGeometry( geometry );
	win.showFullScreen();

	if not without_flash:
		send_flash()

def send_error():
	global win

	win.sigerror.emit()

def send_flash():
	global win, last, options

	if not last or last < time.time():
		last = ( time.time() + 1 )
		win.sigflash.emit( options[ 'duration' ] )

def main():
	global app, win, options

	import json

	try:
		config = os.path.join( os.path.dirname( __file__ ), 'config.json' )
		with open( config, 'rb' ) as f:
			data = json.loads( f.read() )
			for key, value in data.items():
				if key in options and type( options[ key ] ) == type( value ):
					options[ key ] = value
	except:
		pass

	try:
		from library import window

		from threading import Thread
		from PyQt5.QtCore import Qt

		window.init( APP_ICON, APP_TITLE )
		app = window.app
		win = window.win

		win.setWindowFlags( win.windowFlags() | Qt.Tool )
		win.setWindowFlags( win.windowFlags() | Qt.WindowFullScreen )
		win.setVisible( True )

		if options[ 'screen' ] >= 0:
			next_screen( force = options[ 'screen' ], without_flash = True )

		tray = systray( app )

		args = ( options[ 'username' ], options[ 'oauth' ] )
		kwargs = { 'success': send_flash, 'error': send_error, 'verbose': True }

		t = Thread( target = listener, args = args, kwargs = kwargs, daemon = True )
		t.start()

		window.exec()
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()
