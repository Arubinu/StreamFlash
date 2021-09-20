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
APP_VERSION = '1.1'

# globals
app = None
tcs = None
win = None
last = 0
screen = 0
options = { 'username': '', 'oauth': '', 'screen': 0, 'duration': 400, 'delay': 5, 'pause': 0 }

def systray( app ):
	global APP_ICON, APP_TITLE, APP_VERSION, options

	from PyQt5.QtGui import QIcon
	from PyQt5.QtCore import Qt, QTimer
	from PyQt5.QtWidgets import QMenu, QLabel, QSpinBox, QWidgetAction, QSystemTrayIcon

	tray = QSystemTrayIcon( app )
	tray.setIcon( QIcon( APP_ICON ) )

	menu = QMenu()
	menu.setStyleSheet( 'QMenu::item, QLabel { padding: 3px 6px 3px 6px; } QMenu::item:selected { background-color: rgba( 0, 0, 0, .1 ); }' )

	action = menu.addAction( '%s v%s' % ( APP_TITLE, APP_VERSION ) )
	action.setEnabled( False )

	menu.addSeparator()

	action = menu.addAction( 'Reconnect' )
	action.triggered.connect( lambda: connect( send_flash, send_error, verbose = True ) )

	action = menu.addAction( 'Next Screen' )
	action.triggered.connect( lambda: next_screen() )

	menu.addSeparator()

	# Duration
	submenu = menu.addMenu( 'Duration (ms)' )

	action = QWidgetAction( menu )
	spinbox = QSpinBox()
	spinbox.setFixedWidth( 80 )
	spinbox.setRange( 100, 5000 )
	spinbox.setSingleStep( 10 )
	spinbox.setValue( options[ 'duration' ] )
	spinbox.valueChanged.connect( lambda value: set_option( 'duration', value ) )
	action.setDefaultWidget( spinbox )
	submenu.addAction( action )
	#! Duration

	# Delay
	submenu = menu.addMenu( 'Delay (sec)' )

	action = QWidgetAction( menu )
	spinbox = QSpinBox()
	spinbox.setFixedWidth( 80 )
	spinbox.setRange( 1, ( 60 * 5 ) )
	spinbox.setSingleStep( 10 )
	spinbox.setValue( options[ 'delay' ] )
	spinbox.valueChanged.connect( lambda value: set_option( 'delay', value ) )
	action.setDefaultWidget( spinbox )
	submenu.addAction( action )
	#! Delay

	# Pause
	submenu = menu.addMenu( 'Pause (min)' )

	action = QWidgetAction( menu )
	spinbox_pause = QSpinBox()
	spinbox_pause.setFixedWidth( 80 )
	spinbox_pause.setRange( 1, ( 60 * 24 ) )
	spinbox_pause.setSingleStep( 1 )
	spinbox_pause.setValue( 0 )
	action.setDefaultWidget( spinbox_pause )
	submenu.addAction( action )

	submenu.addSeparator()

	action_pause = QWidgetAction( menu )
	button_pause = QLabel()
	button_pause.setFixedWidth( 80 )
	button_pause.setAlignment( Qt.AlignCenter )
	button_pause.setText( 'Start' )
	action_pause.setDefaultWidget( button_pause )
	submenu.addAction( action_pause )

	timer = QTimer()
	timer.setSingleShot( False )
	def interval( init = False ):
		global options
		nonlocal timer, spinbox_pause

		value = options[ 'pause' ]
		if value > 0:
			if init:
				timer.stop()
				timer.start( 1000 * 60 )
			else:
				value -= 1
		else:
			timer.stop()
			value = 0

		set_option( 'pause', value )
		spinbox_pause.setEnabled( not value )
		spinbox_pause.setValue( max( 1, value ) )
		spinbox_pause.setFocusPolicy( Qt.NoFocus )
		button_pause.setText( 'Stop' if value > 0 else 'Start' )
	timer.timeout.connect( lambda: interval() )

	def set_pause( force = None ):
		nonlocal timer, spinbox_pause

		value = 0
		pause = ( timer.isActive() if force is None else ( not force ) )
		if not pause:
			value = max( 1, spinbox_pause.value() )

		set_option( 'pause', value )
		interval( True )

	action_pause.triggered.connect( lambda: set_pause() )
	#! Pause

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
				success( True )

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
		send_flash( True )

def send_error():
	global win

	win.sigerror.emit()

def send_flash( force = False ):
	global win, last, options

	delay = max( 1, options[ 'delay' ] )
	duration = max( 100, options[ 'duration' ] )

	if force or not last or ( last + delay ) < time.time():
		last = time.time()
		win.sigflash.emit( duration )

def set_option( name, value ):
	global options

	if name in options and type( options[ name ] ) == type( value ):
		options[ name ] = value

def main():
	global app, win, options

	import json

	try:
		config = os.path.join( os.path.dirname( __file__ ), 'config.json' )
		with open( config, 'rb' ) as f:
			data = json.loads( f.read() )
			for key, value in data.items():
				set_option( key, value )
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
