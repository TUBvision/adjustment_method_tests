"""
This script implements a simple psychophysics experiment which makes use of all
the functionality of HRL. It forms a good basis from which to write your own
experiment.
The experiment involves three circles of different luminance, and the objective
is to set the middle circle to have a luminance in between the two other
circles. The luminance of the middle circle can be changed via Up and Down for
big steps, and Right and Left for small steps. When the subject feels that the
luminance is correct, Space can be pressed to save the results to a file and
move to the next round. Escape can be pressed at any time to quit the
experiment. Results will be saved in a file called 'results.csv'.
"""

### Imports ###

# Package Imports
from hrl import HRL

# Qualified Imports
import numpy as np
import sys
import os
import time

# Unqualified Imports
from make_stimulus import image_to_array, normalize_image2

### Main ###


def main(sbj, blk):
	#~ observer_id  = raw_input ('Please write the subject\'s initials: ')
	#~ os.path.isfile(observer_id*)
	### HRL Parameters ###


	# Here we define all the paremeters required to instantiate an HRL object.

	# Which devices we wish to use in this experiment. See the
	# pydoc documentation for a list of # options.
	graphics='datapixx' # 'datapixx' is another option
	inputs='responsepixx' # 'responsepixx' is another option
	photometer=None
	scrn = 1

	# Screen size
	wdth = 1024
	hght = 768
	
	# Whether or not to use fullscreen. You probably want to do this when
	# actually running experiments, but when just developing one, fullscreen
	# locks out access to the rest of the computer, so you'll probably want to
	# turn this off.
	fs = True

	# Design and result matrix information. This allows us the to use the HRL
	# functionality for automatically reading a design matrix, and
	# automatically generating a result matrix. See 'pydoc hrl.hrl' for more
	# information about these.

	# Design and Result matrix files names
	#~ designFname = 
	#~ dfl = '../design/' + designFname + '.csv'
	#~ dfl = '../design/%s_design.csv' %(observer_id)
	#~ rfl = '../results/%s_results.csv' %(observer_id)
	
	if blk == 0:
		dfl = '../design/2afc_design_Dark_' + sbj + '.csv'
		rfl = '../results/2afc_results_Dark_' + sbj + '.csv'
	if blk == 1:
		dfl = '../design/2afc_design_Light_' + sbj + '.csv'
		rfl = '../results/2afc_results_Light_' + sbj + '.csv'
	
	# The names of the fields in the results matrix. In each loop of the
	# script, we write another line of values to results.csv under these
	# headings.
	rhds = ['Trial', 'LumTarget', 'LumMatch', 'LT-LM', 'LumComp', '%deviance', 'Choice', 'RT']

	# Pass this to HRL if we want to use gamma correction.
	lut = '../stimuli/lut.csv'

	# Create the hrl object with the above fields. All the default argument names are
	# given just for illustration.
	hrl = HRL(graphics=graphics,
			  inputs=inputs,
			  photometer=photometer,
			  wdth=wdth,
			  hght=hght,
			  bg=0,
			  dfl=dfl,
			  rfl=rfl,
			  rhds=rhds,
			  fs=fs,
			  scrn=scrn,
			  lut=lut )

	# hrl.results is a dictionary which is automatically created by hrl when
	# give a list of result fields. This can be used to easily write lines to
	# the result file, as will be seen later.
	hrl.results['Trial'] = 0
	
	btn = None
	t = 0
	escp = False
	
	#instruction screen 
	frmInst = hrl.graphics.newTexture(np.array([[1]]))
	frmInst.draw((0,0), (wdth,hght))
	hrl.graphics.flip(clr=True)
	while ((btn != 'Space') & (escp != True)):
		(btn,t1) = hrl.inputs.readButton()
		if btn == 'Escape':
			escp = True
			raise Exception('experiment terminated by the subject')
	
	### Experiment setup ###

	# texture creation in buffer : stimulus	   I DO NOT NEED A BUFFERED IMAGE TO DRAW ON
		
	### Core Loop ###

	# hrl.designs is an iterator over all the lines in the specified design
	# matrix, which was loaded at the creation of the hrl object. Looping over
	# it in a for statement provides a nice way to run each line in a design
	# matrix. The fields of each design line (dsgn) are drawn from the design
	# matrix in the design file (design.csv).
	for dsgn in hrl.designs:
		# Here we save the values of the design line with appropriately cast
		# types and simple names.
		LumS = float(dsgn['Lum_S'])
		LumCD = float(dsgn['Lum_CD'])
		LumCL = float(dsgn['Lum_CL'])

		if blk == 1:
			img_fname = '../stimuli/' + sbj +'/lS%d_CD%d_CL%d' %(int(LumS), int(LumCD), int(LumCL))
		if blk == 0:
			img_fname = '../stimuli/' +sbj + '/dS%d_CD%d_CDD%d' %(int(LumS), int(LumCD), int(LumCL))
		#~ curr_image = image_to_array(img_fname)
		curr_image2 = image_to_array(img_fname)
		curr_image  = normalize_image2(curr_image2, 0, 1)
		
		# prestimulus fixation 
		frmFix = hrl.graphics.newTexture(np.array([[float(120.0/255.0)]]))
		frmFix.draw((0,0), (wdth,hght))
		hrl.graphics.flip(clr=False)
		time.sleep(0.5)
		
		# And finally we preload some variables to prepare for our button
		# reading loop.
		
		# stimulus presentation
		#~ frm1 = hrl.graphics.newTexture(curr_image)
		frm1 = hrl.graphics.newTexture(curr_image)
		frm1.draw((0,0),(wdth,hght)) 
		hrl.graphics.flip(clr=True)
		time.sleep(0.25)
		#~ time.sleep(1.0)
		
		# response fixation
		frmFix.draw((0,0), (wdth,hght))
		if hrl.results['Trial'] > 99:
			nte2 = hrl.results['Trial'] / 100
			nte1 = hrl.results['Trial'] / 10 - nte2*10
			nte0 = hrl.results['Trial'] %10
			fileN = 'testingImg_%d' %(nte1)
			fileN2 = 'testingImg_%d' %(nte0)
			fileN3 = 'testingImg_%d' %(nte2)
			nT = normalize_image2(image_to_array(fileN),0,1)
			nT2 = normalize_image2(image_to_array(fileN2),0,1)
			nT3 = normalize_image2(image_to_array(fileN3),0,1)
			hrl.graphics.newTexture(nT).draw((25,0), (20,28))
			hrl.graphics.newTexture(nT2).draw((50,0), (20,28)) 
			hrl.graphics.newTexture(nT3).draw((5,0), (20,28)) 
			hrl.graphics.flip(clr=True) 
			
		elif hrl.results['Trial'] > 9:
			nte1 = hrl.results['Trial'] / 10
			nte0 = hrl.results['Trial'] %10
			fileN = 'testingImg_%d' %(nte1)
			filen2 = 'testingImg_%d' %(nte0)
			nT = normalize_image2(image_to_array(fileN),0,1)
			nT2 = normalize_image2(image_to_array(filen2),0,1)
			hrl.graphics.newTexture(nT).draw((5,0), (20,28))
			hrl.graphics.newTexture(nT2).draw((25,0), (20,28)) 
			hrl.graphics.flip(clr=True) 
			
		else:
			fileN = 'testingImg_%d' %(hrl.results['Trial'])
			nT = normalize_image2(image_to_array(fileN), 0, 1)
			hrl.graphics.newTexture(nT).draw((5,0), (20,28)) 
			hrl.graphics.flip(clr=True)
			
		### Input Loop ####
		
		# Until the user finalizes their luminance choice for the central
		# circle, or pressed escape...
		
		# The button pressed
		btn = None
		# The time it took to decide on which pair is more different
		t = 0
		# Whether escape was pressed
		escp = False
		
		while ((btn != 'Space') & (escp != True)):

			# Read the next button press
			(btn,t1) = hrl.inputs.readButton()
			# Add the time it took to press to the decision time
			t += t1
			# Respond to the pressed button
			if blk == 0:
				if btn == 'Left': # if CDD-CD-S, then Left = CDD-CD looks more similar
								  # if CD-S-CL , then Left = CD- S  looks more similar 
					hrl.results['Trial'] += 1
					hrl.results['LumTarget'] = LumS
					hrl.results['LumMatch'] = LumCD
					hrl.results['LT-LM'] = LumS-LumCD
					hrl.results['LumComp'] = LumCL
					hrl.results['%deviance'] = np.round(((LumCL-LumCD)/LumCD)*100, 0)
					hrl.results['Choice'] = 0
					hrl.results['RT'] = t
					hrl.writeResultLine()
					break
				elif btn == 'Right': # if CDD-CD-S, then Right = CD-S looks more similar
									 # if CD-S-CL , then Right = S- CL  looks more similar 
					hrl.results['Trial'] += 1
					hrl.results['LumTarget'] = LumS
					hrl.results['LumMatch'] = LumCD
					hrl.results['LT-LM'] = LumS-LumCD
					hrl.results['LumComp'] = LumCL
					hrl.results['Choice'] = 1
					hrl.results['%deviance'] = np.round(((LumCL-LumCD)/LumCD)*100, 0)
					hrl.results['RT'] = t
					hrl.writeResultLine()
					break
				elif btn == 'Escape':
					escp = True
					break
			if blk == 1:
				if btn == 'Down': # if CDD-CD-S, then Left = CDD-CD looks more similar
								  # if CD-S-CL , then Left = CD- S  looks more similar 
					hrl.results['Trial'] += 1
					hrl.results['LumTarget'] = LumS
					hrl.results['LumMatch'] = LumCD
					hrl.results['LT-LM'] = LumS-LumCD
					hrl.results['LumComp'] = LumCL
					hrl.results['%deviance'] = np.round(((LumCL-LumCD)/LumCD)*100, 0)
					hrl.results['Choice'] = 0
					hrl.results['RT'] = t
					hrl.writeResultLine()
					break
				elif btn == 'Up': # if CDD-CD-S, then Right = CD-S looks more similar
									 # if CD-S-CL , then Right = S- CL  looks more similar 
					hrl.results['Trial'] += 1
					hrl.results['LumTarget'] = LumS
					hrl.results['LumMatch'] = LumCD
					hrl.results['LT-LM'] = LumS-LumCD
					hrl.results['LumComp'] = LumCL
					hrl.results['Choice'] = 1
					hrl.results['%deviance'] = np.round(((LumCL-LumCD)/LumCD)*100, 0)
					hrl.results['RT'] = t
					hrl.writeResultLine()
					break
				elif btn == 'Escape':
					escp = True
					break
		# We print the trial number simply to keep track during an experiment
		print hrl.results['Trial']
		
		# If escape has been pressed we break out of the core loop
		if escp:
			print "Session cancelled"
			break
				
	# And the experiment is over!
	hrl.close()
	print "session complete"
	#~ print "Session ", session ," complete"

### Run Main ###


if __name__ == '__main__':
	a = str(sys.argv[1])
	b = int(sys.argv[2])
	main(a,b)
