import re
import pandas as pd
import sys
import os
import csv
import time
import random
import numpy as np
from matplotlib import pyplot as plt

def convert_lum(gs_val):
	""" converts grey-scale value [0,255] to luminance in cd/m2
	"""
	lut = pd.read_csv('../stimuli/lut.csv', sep =" ")
	norm = gs_val/255.0
	a = np.interp(norm, lut['IntensityIn'], lut['Luminance'])
	return a
	
def main(sbj):

	onDark = pd.read_csv('../results/base_onDark_' + sbj + '.csv', sep=" ", index_col=0)
	onLight = pd.read_csv('../results/base_onLight_' + sbj + '.csv', sep=" ", index_col=0)

	# onDark  : target is on dark check
	# onLight : target is on light check

	LumType_dark = onDark['target'].values
	LumType_light = onLight['target'].values

	LumS_dark = onDark['LumM_end'].values
	LumS_light = onLight['LumT'].values

	LumCD_dark = onDark['LumT'].values
	LumCD_light = onLight['LumM_end'].values
	
	def linearfit(iL, mL):
		mpl, bpl = np.polyfit(iL, mL, 1)
		fit = map(lambda x:x * mpl +bpl, iL)
		return fit
	# GENERATE TARGET-MATCH LOG FOR ALL EXPT
	lendata = len(LumS_light)
	data = np.zeros((lendata*2,3))
	for i in range(lendata*2):
		if i < lendata:
			data[i,:] = np.array([LumType_dark[i], LumS_dark[i], LumCD_dark[i]])
		else:
			data[i,:] = np.array([LumType_light[i-lendata], LumS_light[i-lendata], LumCD_light[i-lendata]])

	df = pd.DataFrame(data, columns=['target_type', 'LumS', 'LumCD'])
	print df

	
	#df.to_csv('../results/base_inc_dec_match_' + sbj + '.csv', sep = " ", index_label='trl')


### Run Main ###

if __name__ == '__main__':
	initials = raw_input("initals :  ")
	main(str(initials))
