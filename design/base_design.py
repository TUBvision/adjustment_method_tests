import numpy as np
import pandas as pd
import random
import time
import sys
import re

def main(sbj):
	"""
	generates base experiment design
	  4 decrement ellipses on light check inside shadow
	+ 4 increment ellipses on dark check outside shadow
	---------------------------------------------------------
	  8 stimuli
	x10 repeats
	---------------------------------------------------------
	 80 trials
	"""

	LumeS_fix = np.linspace(28,48,4)
	LumeCD_fix = np.linspace(68,88,4)

	totLum = np.arange(0,255)

	nTarget = len(LumeS_fix)
	nRepeat = 10

	Lcomb = np.zeros((nTarget*nRepeat,3))
	Dcomb = np.zeros((nTarget*nRepeat,3))
	
	for i in range(nTarget):
		for j in range(nRepeat):
			Lcomb[i*nRepeat+j,:] = np.array([LumeS_fix[i], np.random.choice(totLum), 1.0])
			Dcomb[i*nRepeat+j,:] = np.array([np.random.choice(totLum), LumeCD_fix[i], 0.0])

			Ddesign_random = np.random.permutation(Dcomb)
			DdesignMatrix = pd.DataFrame(Ddesign_random, columns=['Lum_S', 'Lum_CD', 'target_type'])
			DdesignMatrix.to_csv('base_design_onDark_' + sbj +'_.csv', sep = ' ', index_label='trl')

			Ldesign_random = np.random.permutation(Lcomb)
			LdesignMatrix = pd.DataFrame(Ldesign_random, columns=['Lum_S', 'Lum_CD', 'target_type'])
			LdesignMatrix.to_csv('base_design_onLight_' + sbj +'_.csv', sep = ' ', index_label='trl')


		
if __name__ == '__main__':
	initials = raw_input("initals :  ")
	main(str(initials))
	print "generated base experiment design!"
