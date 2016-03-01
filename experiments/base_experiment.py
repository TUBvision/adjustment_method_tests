### Imports ###

# Package Imports
from hrl import HRL
from PIL import Image

# Qualified Imports
import numpy as np
import sys
import os
import pandas as pd

# Unqualified Imports
from random import uniform
from make_stimulus import image_to_array, add_increment, make_ellipse, array_to_image


### Main ###
#~ curr_image = drawImg('../renTemplate', 13, Lum_S, Lum_CD)

def drawImg(inputImg, radius, sLum, cdLum):
	curr_image2 = image_to_array(inputImg)
	curr_image  = curr_image2/255.0
	elipse = make_ellipse(radius)
	add_increment(stimulus=curr_image, increment=elipse*(sLum/255.0), position=(428,585))
	add_increment(stimulus=curr_image, increment=elipse*(cdLum/255.0), position=(337,442))
	
	return curr_image
	
def unify_localLum():
	## template image
	templateImg = '../stimuli/white_box2'
	## load template image to array
	templateImg_mat = image_to_array(templateImg)

	## masking
	mask43_fname = '../stimuli/mask_ShLi_43' # standard: within shadow, light check
	mask35_fname = '../stimuli/mask_PlDa_35' # comparison dark: outside shadow, dark check
	
	## load mask images to array
	mask43 = image_to_array(mask43_fname)
	mask35 = image_to_array(mask35_fname)

	## set entire checks with values read from center coordinates of each target check
	# S, check 43 : position=(428,585) 
	# CD, check 35 : position=(337,442)
	# CL, check 32 : position=(477,435)
	# CDD, check 26 : position= (294,306)
	# CDD, check 24 : position= (383,295)
	templateImg_mat[mask43 != 0] = templateImg_mat[428,585]
	templateImg_mat[mask35 != 0] = templateImg_mat[428,585]

	# save the rendered image
	array_to_image(templateImg_mat,'../stimuli/renTemplate','png')


	
def main(subject, target_type):
	### Argument Parser ###

	### HRL Parameters ###
	ttype = target_type

	# Here we define all the paremeters required to instantiate an HRL object.

	# Which devices we wish to use in this experiment. See the
	# pydoc documentation for a list of # options.
	graphics='datapixx' # 'datapixx' is another option
	inputs='responsepixx' # 'responsepixx' is another option
	scrn = 1
	photometer=None

	# Screen size
	wdth = 1024
	hght = 768
	
	# Whether or not to use fullscreen. You probably want to do this when
	# actually running experiments, but when just developing one, fullscreen
	# locks out access to the rest of the computer, so you'll probably want to
	# turn this off.
	fs = True

	# Pass this to HRL if we want to use gamma correction.
	lut = '../stimuli/lut.csv'

	# Design and result matrix information. This allows us the to use the HRL
	# functionality for automatically reading a design matrix, and
	# automatically generating a result matrix. See 'pydoc hrl.hrl' for more
	# information about these.

	if target_type == 0.0:
		dfl = '../design/base_design_onDark_' + subject + '_.csv'
		rfl = '../results/base_onDark_' + subject + '.csv'
		rhds = ['Trial', 'target', 'LumT', 'LumM_start', 'LumM_end', 'RT']
		hrl = HRL(graphics=graphics,inputs=inputs,photometer=photometer,scrn=scrn
			,wdth=wdth,hght=hght,bg=0,dfl=dfl,rfl=rfl,rhds=rhds,fs=fs, lut=lut)
		hrl.results['Trial'] = 0

	elif target_type == 1.0:
		dfl = '../design/base_design_onLight_' + subject + '_.csv'
		rfl = '../results/base_onLight_' + subject + '.csv'
		rhds = ['Trial', 'target', 'LumT', 'LumM_start', 'LumM_end', 'RT']
		hrl = HRL(graphics=graphics,inputs=inputs,photometer=photometer,scrn=scrn
			,wdth=wdth,hght=hght,bg=0,dfl=dfl,rfl=rfl,rhds=rhds,fs=fs, lut=lut)
		hrl.results['Trial'] = float(len(pd.read_csv(dfl, sep=" ", index_col=0)))

	smlstp = 2/255.0
	bgstp = 10/255.0

	for dsgn in hrl.designs:
		# Here we save the values of the design line with appropriately cast
		# types and simple names.
		Lum_S = float(dsgn['Lum_S'])
		Lum_CD = float(dsgn['Lum_CD'])
		#~ Lum_S = float(53)
		#~ Lum_CD = float(68.4285714286)

		curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)

		# stimulus presentation
		frm1 = hrl.graphics.newTexture(curr_image)
		frm1.draw((0,0),(wdth,hght)) 
		hrl.graphics.flip(clr=True)

		# And finally we preload some variables to prepare for our button
		# reading loop.

		# The button pressed
		btn = None
		# The time it took to decide on the mean luminance
		t = 0.0
		# Whether escape was pressed
		escp = False

		print hrl.results['Trial'], '   LumS = ', Lum_S, '    LumCD = ',  Lum_CD
		### Input Loop ####
		
		# Until the user finalizes their luminance choice for the central
		# circle, or pressed escape...
		while ((btn != 'Space') & (escp != True)):

			# Read the next button press
			(btn,t1) = hrl.inputs.readButton()
			# Add the time it took to press to the decision time
			t += t1
			if ttype == 1:
				# Respond to the pressed button
				if btn == 'Up':
					Lum_CD += bgstp*255
					# Make sure the luminance doesn't fall out of the range [0,1]
					if Lum_CD > 255: Lum_CD = 255
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Right':
					Lum_CD += smlstp*255
					if Lum_CD > 255: Lum_CD = 255
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Down':
					Lum_CD -= bgstp*255
					if Lum_CD < 0: Lum_CD = 0
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Left':
					Lum_CD -= smlstp*255
					if Lum_CD < 0: Lum_CD = 0
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Escape':
					escp = True
					break
					
			if ttype == 0:
				# Respond to the pressed button
				if btn == 'Up':
					Lum_S += bgstp*255
					# Make sure the luminance doesn't fall out of the range [0,1]
					if Lum_S > 255: Lum_S = 255
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Right':
					Lum_S += smlstp*255
					if Lum_S > 255: Lum_S = 255
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Down':
					Lum_S -= bgstp*255
					if Lum_S < 0: Lum_S = 0
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Left':
					Lum_S -= smlstp*255
					if Lum_S < 0: Lum_S = 0
					curr_image = drawImg('../stimuli/renTemplate', 25, Lum_S, Lum_CD)
					frm1 = hrl.graphics.newTexture(curr_image)
					frm1.draw((0,0),(wdth,hght)) 
					hrl.graphics.flip(clr=True)
				elif btn == 'Escape':
					escp = True
					break
					
		# Once a value has been chosen by the subject, we save all the relevant
		# variables to the result file by loading it all into the hrl.results
		# dictionary, and then finally running hrl.writeResultLine().
		#rhds = ['Trial', 'target', 'LumS', 'Lum_CD', 'LumCD_end', 'RT']
		
		# We print the trial number simply to keep track during an experiment
		print hrl.results['Trial'], '    LumS= ', Lum_S, '   LumCD= ', Lum_CD
		
		if ttype == 0:
			hrl.results['Trial'] += 1
			hrl.results['target'] = ttype
			hrl.results['LumT'] = Lum_CD
			hrl.results['LumM_start'] = float(dsgn['Lum_S'])
			hrl.results['LumM_end'] = Lum_S
			hrl.results['RT'] = t
			hrl.writeResultLine()
		
		if ttype == 1:
			hrl.results['Trial'] += 1
			hrl.results['target'] = ttype
			hrl.results['LumT'] = Lum_S
			hrl.results['LumM_start'] = float(dsgn['Lum_CD'])
			hrl.results['LumM_end'] = Lum_CD
			hrl.results['RT'] = t
			hrl.writeResultLine()
			
		

		# If escape has been pressed we break out of the core loop
		if escp:
			print "Session cancelled"
			break

	# And the experiment is over!
	hrl.close()
	print "Session complete"


### Run Main ###

if __name__ == '__main__':
	unify_localLum()
	initials = raw_input("initals :  ")
	check01 = raw_input("0 : targets on dark check, 1: targets on light check     ")
	main(str(initials), int(check01))
