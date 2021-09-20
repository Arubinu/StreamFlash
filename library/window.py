#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

# since PIP
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

# globals
app = None
win = None

class Window( QMainWindow ):
	_icon = ''
	_title = ''

	sigerror = pyqtSignal()
	sigflash = pyqtSignal( int )

	def __init__( self, icon = None, title = None, parent = None ):
		super( Window, self ).__init__( parent )

		self._icon = icon
		self._title = ( title or 'Flash' )

	def setup( self ):
		self.setWindowTitle( self._title )
		self.setWindowFlags( Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput )
		self.setAttribute( Qt.WA_TranslucentBackground, True )
		self.setWindowOpacity( 0 )

		if self._icon:
			icon = QIcon()
			icon.addPixmap( QPixmap( self._icon ), QIcon.Normal, QIcon.Off )
			self.setWindowIcon( icon )

		self.centralWidget = QWidget( self )
		self.setCentralWidget( self.centralWidget )

		self.show()
		self.center()
		self.color( '255, 255, 255' )

		self.sigerror.connect( self.error )
		self.sigflash.connect( self.flash )

	def center( self ):
		self.move( QPoint( 0, 0 ) )

		size = QApplication.desktop().screenGeometry().size()
		self.setFixedSize( size.width(), size.height() )

	def color( self, color ):
		self.setStyleSheet( 'background-color: rgb( %s );' % color )

	def error( self ):
		self.color( '255, 0, 0' )
		self.flash()
		self.color( '255, 255, 255' )

	def flash( self, duration = 1000 ):
		opacity = 0

		while opacity < 1:
			opacity += ( 1 / ( 60 * ( duration / 1000 ) ) )
			self.setWindowOpacity( opacity )
			QApplication.processEvents()
			time.sleep( duration / 60 / 1000 )

		while opacity > 0:
			opacity -= ( 1 / ( 60 * ( duration / 1000 ) ) )
			self.setWindowOpacity( opacity )
			QApplication.processEvents()
			time.sleep( duration / 60 / 1000 )

def init( icon = None, title = None ):
	global app, win

	app = QApplication( [] )

	win = Window( icon, title )
	win.setup()

def exec():
	global app, win

	sys.exit( app.exec_() )

def main( icon = None, title = None ):
	init( icon, title )
	exec()

if __name__ == '__main__':
	main( os.path.dirname( __file__ ) + '/../resources/logo.png' )
