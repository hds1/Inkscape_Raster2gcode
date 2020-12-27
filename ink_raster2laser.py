'''
# Inkscape raster to gcode
# Heiko Schroeter, 12/2020
# Tested with 15W China Laser, grbl 1.1, arduino nano
# 1) Create 8-Bit BW PNG picture file
# 2) Import into Inkscape
# 3) Extension -> Inkraster2Gcode
# 4) Set params
# 5) Create PNG preview and gcode file
#
# Needs: png.py
#
# Operation;
# The orig PNG file is transformed by inkscape to wanted size and then
# read back by png.py into workking matrix.
# Matrix X-row is laser scan- and burnline
# The gcode file uses a general speed set and varies the burn intensity
# by {S} param. This is needed because wen using M4 and M5 the movement
# is shattering due the acceleration and decelration from burn px to burn px.
#
#
# ----------------------------------------------------------------------------
# Copyright (C) 2014 305engineering <305engineering@gmail.com>
# Original concept by 305engineering.
#
# "THE MODIFIED BEER-WARE LICENSE" (Revision: my own :P):
# <305engineering@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff (except sell). If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
'''


import sys
import os
import re

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions')

import subprocess
import math

import inkex
import png
import array


class GcodeExport(inkex.Effect):

######## 	Invoked by _main()
	def __init__(self):
		"""init the effect library and get options from gui"""
		inkex.Effect.__init__(self)

		# Image export options
		self.OptionParser.add_option("-d", "--directory",action="store", type="string", dest="directory", default="/home/",help="Directory for files") ####check_dir
		self.OptionParser.add_option("-f", "--filename", action="store", type="string", dest="filename", default="-1.0", help="Export File name")

		self.OptionParser.add_option("","--add-numeric-suffix-to-filename", action="store", type="inkbool", dest="add_numeric_suffix_to_filename", default=True,help="Add numeric suffix to filename")
		self.OptionParser.add_option("","--linewidth",action="store", type="float", dest="linewidth", default="0.2",help="")
		self.OptionParser.add_option("","--picwidth",action="store", type="float", dest="picwidth", default="25.0",help="Pic width in [mm]")
		self.OptionParser.add_option("","--picheigth",action="store", type="float", dest="picheigth", default="25.0",help="Pic heigth in [mm]")

		# Modal Options for the China 15W Laser module
		self.OptionParser.add_option("","--Laser_Max",action="store", type="int", dest="Laser_Max", default="320",help="")
		self.OptionParser.add_option("","--Laser_Min",action="store", type="int", dest="Laser_Min", default="25",help="")
		#Black Velocity and Moving
		self.OptionParser.add_option("","--speed_ON",action="store", type="int", dest="speed_ON", default="1500",help="")

		# Commands
		self.OptionParser.add_option("","--laseron", action="store", type="string", dest="laseron", default="M04", help="Dynamic Laser ON")
		self.OptionParser.add_option("","--laseroff", action="store", type="string", dest="laseroff", default="M05", help="Laser Off")

######## 	Invoked by __init __ ()
########	Here everything is done
	def effect(self):


		current_file = self.args[-1]
                # inkex.errormsg("FILE: " + current_file)
		bg_color = "#ffffff"
		suffix = "_Gray_8bit"

		##Implementare check_dir

		if (os.path.isdir(self.options.directory)) == True:

			##CODE THAT IS THE DIRECTORY
			#inkex.errormsg("OK") #DEBUG

			#Generate file paths to use
			pos_file_png_exported = os.path.join(self.options.directory,self.options.filename + suffix + ".png")
			pos_file_gcode = os.path.join(self.options.directory,self.options.filename + suffix + ".ngc")

			#Export the image to PNG
			self.exportPage(pos_file_png_exported,current_file,bg_color)

			#Manipulate the PNG image to generate the Gcode file
			self.PNGtoGcode(pos_file_png_exported,pos_file_gcode)

		else:
			inkex.errormsg("Directory does not exist! Please specify existing directory!")




########	EXPORT IMAGE IN PNG
######## 	Invoked by effect ()

	def exportPage(self,pos_file_png_exported,current_file,bg_color):
		######## CREATING THE FILE PNG ########
                # Needs to be Inkscape.png otherwise png.py wont read the PNG file (wrong signature error)

                width  = self.options.picwidth/self.options.linewidth
                heigth = self.options.picheigth/self.options.linewidth

                # Export Image to PNG file to be read back by png.py
		command="inkscape -C -e \"%s\" -w %s -h %s -b\"%s\" %s" % (pos_file_png_exported,width,heigth,bg_color,current_file) #Command from command line to export to PNG
		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return_code = p.wait()
		f = p.stdout
		err = p.stderr


	def PNGtoGcode(self,pos_file_png_exported,pos_file_gcode):

                # Read the exported PNG file by png.py
		reader = png.Reader(pos_file_png_exported)

		w, h, pixels, metadata = reader.read_flat()

                # set gcode Laser Max and Min values
		LaserMax = int(self.options.Laser_Max)
                LaserMin = int(self.options.Laser_Min)

		matrice = [[255 for i in range(w)]for j in range(h)]  #List al posto di un array

		#Just copy. Pic is ready to use.
		for y in range(h): # Y ranges from 0 to h-1
			for x in range(w): # X varies from 0 to w-1
				pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
				matrice[y][x] = int(pixels[pixel_position])

		####Ora matrice_BN contiene l'immagine in Bianco (255) e Nero (0)
		B=255
		N=0

		matrice_BN = [[255 for i in range(w)]for j in range(h)]
		matrice_BN = matrice
                matrice_BN.reverse() # mirror matrix for proper image display

		#### GENERO IL FILE GCODE ####
		Laser_ON  = False
		F_G01     = self.options.speed_ON    # main speed
                linewidth = self.options.linewidth   # laser width or px width
                width     = self.options.picwidth    # X in mm
                heigth    = self.options.picheigth   # Y in mm
                Scala     = 1.0/linewidth            # px/mm
                DPIx      = int(round(w / width * 25.4))   # DPI in X
                DPIy      = int(round(h / heigth * 25.4))  # DPI in Y

		Scaler = float(LaserMax)/255 # Laser Max Setting

		file_gcode = open(pos_file_gcode, 'w')  #Create the file

		#Configurazioni iniziali standard Gcode
		file_gcode.write('; Generated with:\n; "Raster 2 Laser Gcode generator"\n')
                file_gcode.write('; 12/2020 Heiko Schroeter (based on 305 Engineering)\n')
                file_gcode.write('; GCODE for GRBL 1.1\n;\n;\n')

                file_gcode.write('; Width  (wanted): ' + str("%.2f" % float(width)) + ' [mm]\n')
                file_gcode.write('; Height (wanted): ' + str("%.2f" % float(heigth)) + ' [mm]\n;\n')

                file_gcode.write('; Line Width: ' + str("%.2f" % float(linewidth)) + ' [mm]\n')
                file_gcode.write('; Width : ' + str(w) + ' [px]\n')
                file_gcode.write('; Height: ' + str(h) + ' [px]\n')
                file_gcode.write('; Width  (calculated): ' + str("%.2f" % float(float(w)/Scala)) + ' [mm]\n')
                file_gcode.write('; Height (calculated): ' + str("%.2f" % float(float(h)/Scala)) + ' [mm]\n;\n')

		file_gcode.write('; Scala: ' + str("%.2f" % Scala) + ' [px/mm]\n;\n')
		file_gcode.write('; DPIx: ' + str(DPIx) + '\n')
		file_gcode.write('; DPIy: ' + str(DPIy) + '\n;\n')

                file_gcode.write('G21 ; Set units to millimeters\n')
		file_gcode.write('G90 ; Use absolute coordinates\n')
		file_gcode.write('S0  ; We turn off Laser by Zero PWM\n')
		file_gcode.write('M4  ; GRBL Laser on with dynamic\n')
		file_gcode.write('F' + str(F_G01) + '; Set Speed\n;\n')

		#Creazione del Gcode

		#allargo la matrice per lavorare su tutta l'immagine
		for y in range(h):
			matrice_BN[y].append(B)
		w = w+1

                # Map 0-255 to MaxLaser-MinLaser Values
                # i.e.  gray_% = 1 - matrice[][]/255
                #       gray_gcode = (LaserMax-LaserMin)*gray_% + LaserMin
		for y in range(h):
			if y % 2 == 0 : # forward scanline
				for x in range(w):
					if matrice_BN[y][x] != B :
						if Laser_ON == False :
							#file_gcode.write('; newline forward \n')
							file_gcode.write('G00 X' + str("%.2f" % float(float(x)/Scala)) + ' Y' + str("%.2f" % float(float(y)/Scala)) + ' S0 \n')
							Laser_ON = True

						if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
							if x == w-1 : #controllo fine riga
								file_gcode.write('G1 X' + str("%.2f" % float(float(x)/Scala)) + ' S0 \n')
								Laser_ON = False

							else:
                                                                gray_percent = float(1.0 - float(matrice_BN[y][x])/255.0)
                                                                gray_gcode = str(int(round(float((LaserMax-LaserMin)*gray_percent + LaserMin))))
								if matrice_BN[y][x+1] == B :
									file_gcode.write('G1 X' + str("%.2f" % float(float(x+1)/Scala)) + ' S' + gray_gcode + '\n')
									Laser_ON = False

								elif matrice_BN[y][x] != matrice_BN[y][x+1] :
				                                        file_gcode.write('G1 X' + str("%.2f" % float(float(x+1)/Scala)) + ' S' + gray_gcode +'\n')

			else: # backward scanline
				for x in reversed(range(w)):
					if matrice_BN[y][x] != B :
						if Laser_ON == False :
							#file_gcode.write('; newline backward \n')
							file_gcode.write('G00 X' + str("%.2f" % float(float(x+1)/Scala)) + ' Y' + str("%.2f" % float(float(y)/Scala)) + ' S0 \n')
							Laser_ON = True

						if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
							if x == 0 : #controllo fine riga ritorno
								file_gcode.write('G1 X' + str("%.2f" % float(float(x)/Scala)) + ' S0 \n')
								Laser_ON = False
							else:
                                                                gray_percent = float(1.0 - float(matrice_BN[y][x])/255.0)
                                                                gray_gcode = str(int(round(float((LaserMax-LaserMin)*gray_percent + LaserMin))))
								if matrice_BN[y][x-1] == B :
									file_gcode.write('G1 X' + str("%.2f" % float(float(x)/Scala)) + ' S' + gray_gcode + '\n')
									Laser_ON = False
								elif  matrice_BN[y][x] != matrice_BN[y][x-1] :
									file_gcode.write('G1 X' + str("%.2f" % float(float(x)/Scala)) + ' S' + gray_gcode + '\n')

	        #Configurazioni finali standard Gcode
		file_gcode.write('M5; Laser Off\n')
		file_gcode.write('G00 X0 Y0; home\n')
		file_gcode.close() #Chiudo il file

######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	########

def _main():
	e=GcodeExport()
	e.affect()
	exit()

if __name__=="__main__":
	_main()
