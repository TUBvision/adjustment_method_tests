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
	df.to_csv('../results/base_inc_dec_match_' + sbj + '.csv', sep = " ", index_label='trl')
	
	
		# GENERATE AVERAGE MATCHING TABLE

	target_type = data[:,0] #onLight 1, onDark 0
	LumS = data[:,1]
	LumCD = data[:,2]
	 
	#~ targets = np.unique(Lum_target)
	#~ nTar = len(targets)

	#computing ellipse CD average luminance
	darkcheck = np.unique(LumCD[target_type == 0])  # target ellipse was on a dark check and has luminance > 58; dark check luminace 1
	lightcheck = np.unique(LumS[target_type == 1])  # target ellipse was on a dark check and has luminance < 58; light check luminance 2

	incT_avgMatch = [np.average(LumS[LumCD == darkcheck[i]]) for i in range(len(darkcheck))] # light check luminace 1
	decT_avgMatch = [np.average(LumCD[LumS == lightcheck[i]]) for i in range(len(lightcheck))] # dark check luminance 2

	matching_table =pd.DataFrame(data = np.concatenate((darkcheck, decT_avgMatch)), columns = ['LumCD'])
	matching_table['LumCD_conv'] = convert_lum(np.concatenate((darkcheck, decT_avgMatch)))
	matching_table['LumS'] = np.concatenate((incT_avgMatch, lightcheck))
	matching_table['LumS_conv'] = convert_lum(np.concatenate((incT_avgMatch, lightcheck)))
	matching_table.to_csv('../results/base_inc_dec_avg_' + sbj + '.csv', sep = ' ')
	
	
	# GENERATE SCATTERPLOT of math vs target on luminance space
	
	onD_target = df['LumCD'][:lendata]
	onD_match  = df['LumS'][:lendata]
	onL_target = df['LumS'][lendata:]
	onL_match  = df['LumCD'][lendata:]
	
	Dt = np.unique(onD_target)
	Lt = np.unique(onL_target)

	avgMatch = np.zeros((2,4))
	stds     = np.zeros((2,4))
	for i in range(len(Dt)):
		avgMatch[0][i] = np.average(convert_lum(onD_match[onD_target == Dt[i]]))
		avgMatch[1][i] = np.average(convert_lum(onL_match[onL_target == Lt[i]]))
	   
		stds[0][i] = np.std(convert_lum(onD_match[onD_target == Dt[i]]))
		stds[1][i] = np.std(convert_lum(onL_match[onL_target == Lt[i]]))

	f = plt.figure(figsize=(10,10))

	plt.scatter(convert_lum(df['LumCD'][:lendata]), convert_lum(df['LumS'][:lendata]), c='b', label='plain target')
	plt.scatter(convert_lum(df['LumS'][lendata:]), convert_lum(df['LumCD'][lendata:]), c='r', label='shadow target')

	plt.scatter(convert_lum(Dt), avgMatch[0], marker = 'x', s = 70, color = 'b')
	plt.scatter(convert_lum(Lt), avgMatch[1], marker = 'x', s = 70, color = 'r')
	plt.errorbar(convert_lum(Dt), avgMatch[0], yerr = stds[0], linestyle = 'None')
	plt.errorbar(convert_lum(Lt), avgMatch[1], yerr = stds[1], linestyle = 'None', color = 'r')

	plt.axhline(y=convert_lum(58), c ='black', ls='dashed')
	plt.axvline(x=convert_lum(58), c ='black', ls='dashed')

	plt.xlabel('target ellipse luminance', size = 20)
	plt.ylabel('match ellipse luminance', size = 20)
	plt.xticks(size = 15)
	plt.yticks(size = 15)
	plt.ylim([50,200])
	plt.xlim([50,200])

	plt.legend(loc = 'upper right', prop = {'size':20})
	plt.title('Adjustment experiment on luminance space', size = 20)
	plt.savefig('../figures/adjExpt_lum_' + sbj)
	
	# GENERATE SCATTERPLOT of match vs target on contrast space
	
	onD = df[df['target_type']==0].values
	onL = df[df['target_type']==1].values

	# michelson contrasts
	# TargetType = 0, LumS = 1, LumCD = 2 
	checklum= convert_lum(58)

	tContrast = np.zeros(100)
	mContrast = np.zeros(100)

	tContrast[:lendata] = (convert_lum(onD[:,2])-checklum)/(convert_lum(onD[:,2])+checklum)
	mContrast[:lendata]  = (convert_lum(onD[:,1])-checklum)/(convert_lum(onD[:,1])+checklum)
	tContrast[lendata:] = (convert_lum(onL[:,1])-checklum)/(convert_lum(onL[:,1])+checklum)
	mContrast[lendata:]  = (convert_lum(onL[:,2])-checklum)/(convert_lum(onL[:,2])+checklum)

	df['tContrast'] = tContrast
	df['mContrast'] = mContrast

	tD = np.unique(df['tContrast'][:lendata])  ## target ellipse was on a dark check and has luminance > 58; dark check luminace 1
	tL = np.unique(df['tContrast'][lendata:])  ## target ellipse was on a dark check and has luminance < 58; light check luminance 2

	print tD
	print tL

	onD_target = tContrast[:lendata]
	onD_match  = mContrast[:lendata]
	onL_target = tContrast[lendata:]
	onL_match  = mContrast[lendata:]

	Dt = np.unique(onD_target)
	Lt = np.unique(onL_target)

	avgMatch = np.zeros((2,4))
	stds     = np.zeros((2,4))
	for i in range(len(Dt)):
		avgMatch[0][i] = np.average(onD_match[onD_target == Dt[i]])
		avgMatch[1][i] = np.average(onL_match[onL_target == Lt[i]])
	   
		stds[0][i] = np.std(onD_match[onD_target == Dt[i]])
		stds[1][i] = np.std(onL_match[onL_target == Lt[i]])
		
	# GENERATE SCATTERPLOT of math vs target on contrast space
	plt.figure(figsize = (10,10))

	plt.scatter(tContrast[:lendata], mContrast[:lendata], label = 'plain target')
	plt.scatter(tContrast[lendata:], mContrast[lendata:], color = 'r', label = 'shadow target')

	plt.scatter(Dt, avgMatch[0], marker = 'x', s = 70, color = 'b')
	plt.scatter(Lt, avgMatch[1], marker = 'x', s = 70, color = 'r')
	plt.errorbar(Dt, avgMatch[0], yerr = stds[0], linestyle = 'None')
	plt.errorbar(Lt, avgMatch[1], yerr = stds[1], linestyle = 'None', color = 'r')

	plt.axhline(y=0, c ='black', ls='dashed')
	plt.axvline(x=0, c ='black', ls='dashed')
	plt.xlabel('michelson contrast values of target ellipse luminance', size = 15)
	plt.ylabel('michelson contrast values of match ellipse luminance', size = 15)
	plt.xticks(size = 15)
	plt.yticks(size = 15)
	plt.xlim([-0.4, 0.25])
	plt.ylim([-0.4, 0.25])
	plt.legend(loc = 'upper right', prop = {'size':15})
	plt.title('adjustment experiment on contrast space', size = 20)
	plt.savefig('../figures/adjExpt_mc' + sbj)

### Run Main ###

if __name__ == '__main__':
	initials = raw_input("initals :  ")
	main(str(initials))
