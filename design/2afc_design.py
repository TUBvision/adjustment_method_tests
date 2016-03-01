import numpy as np
import pandas as pd
import random
import time
import sys
import re
import pdb


def main(sbj, a):
	"""
	input  : sbj is a csv_file containing LumS and LumCD matches 
			(pandas array with first colum = target_lum, second colum = avgMatch_lum)
	output : design matrix of all posible combinations among 6 LumS-LumCD matches and 7 LumCL (ranged in+/-20% LumS) values
			 over 20 repetitions
	"""
	#~ subject_profile = re.search('../results/(.*).csv', sbj)
	#~ subject_fname = subject_profile.group(1)
	
	sbj_pairs = pd.read_csv('../results/base_inc_dec_avg_' + sbj + '.csv', sep=" ", index_col=0)
	LumS = sbj_pairs['LumS'].values[[0,1,6,7]]
	LumCD = sbj_pairs['LumCD'].values[[0,1,6,7]]

	LumCL = np.array([0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2]) # this can be set manually

	indN = len(LumS) # indn = index for LumS and LumCD
	indM = len(LumCL) # indm = index for LumCL

	comb = np.zeros((indN*indM,3))
	#~ pdb.set_trace()	
	
	if a == 1:
		for i in range(indN):
			for j in range(indM):
				comb[i*indM+j,:] = np.array([LumS[i], LumCD[i], (LumCL[j]*LumS[i])])
	if a == 0:
		for i in range(indN):
			for j in range(indM):
				comb[i*indM+j,:] = np.array([LumS[i], LumCD[i], (LumCL[j]*LumCD[i])])
				
	#~ comb = comb.astype(int)
	
	repeatN = 20
	design_sorted = np.tile(comb,(repeatN,1))
	design_random = np.random.permutation(design_sorted)

	designMatrix = pd.DataFrame(design_random, columns=['Lum_S', 'Lum_CD', 'Lum_CL'])
	if a == 0:
		designMatrix.to_csv('2afc_design_' + sbj + '_Dark.csv', sep = ' ', index_label='trl')
	elif a == 1:
		designMatrix.to_csv('2afc_design_' + sbj + '_Light.csv', sep = ' ', index_label='trl')
	#designMatrix.to_csv('../design/' + sbj + '/expt_design_' + sbj + '_' + str(a) + '.csv', sep = ' ', index_label='trl')
	## test design for viewing all stimuli
	#~ designMatrix = pd.DataFrame(comb, columns=['Lum_S', 'Lum_CD', 'Lum_CL'])
	#~ designMatrix.to_csv('../design/' + sbj + '/test_design_' + sbj + '_' + str(a) + '.csv', sep = ' ', index_label='tr')

if __name__ == '__main__':
	sbj = raw_input("initals :  ")
	DorL = raw_input("0 : dark comparison, 1: light comparison     ")
	main(sbj=str(sbj), a = int(DorL))
