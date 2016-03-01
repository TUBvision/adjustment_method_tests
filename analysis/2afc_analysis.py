import re
import pandas as pd
from make_stimulus import image_to_array, normalize_image2, array_to_image
import sys
import os
import csv
import time
import random
import numpy as np
from matplotlib import pyplot as plt
from base_saveResults import convert_lum
#~ rfl = '../results/' + sbj +'/' + sbj + '_' + str(blk) + '.csv' 

# S-CL looks more similar: 0
# S-CD looks more similar: 1
def main(sbj, blk):
	# import design matrix
	designDC = pd.read_csv('../design/2afc_design_' + sbj + '_Dark.csv', sep = " ", index_col=0) 
	designLC = pd.read_csv('../design/2afc_design_' + sbj + '_Light.csv', sep = " ", index_col=0)
	design = pd.concat((designDC, designLC))

	# import results
	resultDC = pd.read_csv('../results/2afc_results_Dark_' + sbj + '.csv', sep=" ", index_col=0)
	resultLC = pd.read_csv('../results/2afc_results_Light_' + sbj + '.csv', sep=" ", index_col=0)
	result= pd.concat((resultDC, resultLC))

	# create choice vectors for each condition (dark and light comparison)
	choiceDC = result['Choice'].values[:560]
	choiceLC = result['Choice'].values[560:]

	# create luminance vectors of target and match
	LumTarget = result['LumTarget'].values
	LumMatch = result['LumMatch'].values

	# crate two vectors of luminance ratio between target and comparison (in percentage) for each condition 
	# (target luminance - comparison luminance) / target luminance
	# by design, there are 7 values : -20, -10, -5, 0, 5, 10, 20
	pDevDC = np.round((design['Lum_CD'].values[:560] - design['Lum_CL'].values[:560])/design['Lum_CD'].values[:560],2)*100
	pDevLC = np.round((design['Lum_S'].values[560:] - design['Lum_CL'].values[560:])/design['Lum_S'].values[560:],2)*100
	pDev = np.concatenate((pDevDC, pDevLC))

	nTarget = np.unique(LumTarget)
	nMatch  = np.unique(LumMatch)
	nDev    = np.unique(pDev)

	# compute percentage of choosing the target-match (perceptually equal pair)
	# each row represents the percentage when target-match was presented against one of the seven comparisons
	# each column represents the target-match pairs tested
	pCorrectDC = np.zeros((2*len(nDev),2))
	pCorrectLC = np.zeros((2*len(nDev),2))
	for i in range(len(nDev)):
		for j in range(2):
			pCorrectDC[i,j] = np.average(choiceDC[(pDevDC == nDev[i]) & (LumTarget[:560] == nTarget[j*2])])
			pCorrectLC[i,j] = np.average(choiceLC[(pDevLC == nDev[i]) & (LumTarget[560:] == nTarget[j*2])])
			pCorrectDC[len(nDev)+i,j] = np.average(choiceDC[(pDevDC == nDev[i]) & (LumTarget[:560] == nTarget[j*2+1])])
			pCorrectLC[len(nDev)+i,j] = np.average(choiceLC[(pDevLC == nDev[i]) & (LumTarget[560:] == nTarget[j*2+1])])
			
	def convert_lum(gs_val):
		""" converts grey-scale value [0,255] to luminance in cd/m2
		"""
		lut = pd.read_csv('../stimuli/lut.csv', sep =" ")
		norm = gs_val/255.0
		a = np.interp(norm, lut['IntensityIn'], lut['Luminance'])
		return a

	# for the positive part (100% - 120% intervals)
	def sig_ab(x,alpha,beta):
		return 1/(1+np.exp(-(x- alpha)/beta))

	# for the negative part (80% - 100% intervals)
	def sig_ab2(x,alpha,beta):
		return 1/(1+np.exp((x- alpha)/beta))
		
	def bootstrap_estimate(pairN, pCorrect_array):
		""" input  : target-match ellipse luminance pair number (1-4)
			output : bootstrap inference of the data
		"""
		# negative part (80% - 100%)
		nSess         = 2
		nBlock        = len(nDev[:4])
		nTrial        = 20
		stimIntensity = nDev[:4]+100
		pCorrect1      = pCorrect_array[:4,pairN]
		pCorrect2      = pCorrect_array[len(nDev):len(nDev)+4,pairN]
		nObs          = [nTrial] * nBlock

		data1 = np.c_[np.array([80, 85, 90, 100]), pCorrect1[::-1], nObs]
		data2 = np.c_[np.array([80, 85, 90, 100]), pCorrect2[::-1], nObs]

		# positive part (100% - 120%)
		nSess         = 2
		nBlock        = len(nDev[3:])
		nTrial        = 20
		stimIntensity = nDev[3:]+100
		pCorrect3      = pCorrect_array[3:len(nDev),pairN]
		pCorrect4      = pCorrect_array[len(nDev)+3:len(nDev)*2,pairN]
		nObs          = [nTrial] * nBlock

		data3 = np.c_[stimIntensity, pCorrect3, nObs]
		data4 = np.c_[stimIntensity, pCorrect4, nObs]
		
		nafc = 1
		constraints = ('unconstrained', 'unconstrained', 'Beta(2,20)', 'Beta(2,20)')

		N_single_sessions = psi.BootstrapInference (np.r_[data1, data2], priors=constraints, nafc = nafc)
		N_single_sessions.sample()
		P_single_sessions = psi.BootstrapInference (np.r_[data3, data4], priors=constraints, nafc = nafc)
		P_single_sessions.sample()

		Na, Nb, Nl, Ng = N_single_sessions.estimate
		Pa, Pb, Pl, Pg = P_single_sessions.estimate
		
		return N_single_sessions, P_single_sessions
		
	# load bootstrap inferences for each condition (Dark Comparison and Light Comparison)
	DCestimates = []
	LCestimates = []
	for i in range(2):
		DCestimates.append(bootstrap_estimate(i, pCorrectDC))
		LCestimates.append(bootstrap_estimate(i, pCorrectLC))
		
	def savefigpmf(pairN):
		x1 = np.linspace(80,100,100)
		x2 = np.linspace(100,120,100)

		n = pairN

		a = DCestimates[n][0]
		b = DCestimates[n][1]

		c = LCestimates[n][0]
		d = LCestimates[n][1]

		NaD,NbD,NlD, NgD = DCestimates[n][0].estimate
		PaD,PbD,PlD, PgD = DCestimates[n][1].estimate

		NaL,NbL,NlL, NgL = LCestimates[n][0].estimate
		PaL,PbL,PlL, PgL = LCestimates[n][1].estimate

		titles = ['S=107&113, CD=139&137', 'S=116&121, CD=153&146']
		
		plt.figure()
		psi.psigniplot.plotHistogram(a.mcdeviance, a.deviance, "bootstrap deviance", "D")
	#     plt.savefig('../writeup/DCp'+str(pairN)+'_decHist')

		plt.figure()
		psi.psigniplot.plotHistogram(b.mcdeviance, b.deviance, "bootstrap deviance", "D")
	#     plt.savefig('../writeup/DCp'+str(pairN)+'_incHist')

		plt.figure()
		psi.psigniplot.plotHistogram(c.mcdeviance, c.deviance, "bootstrap deviance", "D")
	#     plt.savefig('../writeup/LCp'+str(pairN)+'_decHist')

		plt.figure()
		psi.psigniplot.plotHistogram(d.mcdeviance, d.deviance, "bootstrap deviance", "D")
	#     plt.savefig('../writeup/LCp'+str(pairN)+'_incHist')

		
		plt.figure()
		plt.scatter(nDev+100, pCorrectDC[:len(nDev),n]*100)
		plt.scatter(nDev+100, pCorrectDC[len(nDev):,n]*100)
		plt.plot(x1[::-1], 100*(NgD+(1-NgD-NlD)*1/(1+np.exp(-(x1- NaD)/NbD))), color = 'b')
		plt.plot(x2, 100*(PgD+(1-PgD-PlD)*1/(1+np.exp(-(x2- PaD)/PbD))), color = 'b')
		plt.axvline(x=100, c ='black', ls='dashed')
		plt.title('S=')
		plt.ylim([0, 110])
		plt.xlim([75,125])
		plt.ylabel('% choosing the target-match pair')
		plt.xlabel('luminance proportion to target ellipse luminance (%)')
		plt.title(titles[pairN])
		plt.savefig('../fig/' + sbj + 'DCp' + str(pairN))
		
		plt.figure()
		plt.scatter(nDev+100, pCorrectLC[:len(nDev),n]*100)
		plt.scatter(nDev+100, pCorrectLC[len(nDev):,n]*100)
		plt.plot(x1[::-1], 100*(NgL+(1-NgL-NlL)*1/(1+np.exp(-(x1- NaL)/NbL))), color = 'b')
		plt.plot(x2, 100*(PgL+(1-PgL-PlL)*1/(1+np.exp(-(x2- PaL)/PbL))), color = 'b')
		plt.axvline(x=100, c ='black', ls='dashed')
		plt.title('S=')
		plt.ylim([0, 110])
		plt.xlim([75,125])
		plt.ylabel('% choosing the target-match pair')
		plt.xlabel('luminance proportion to target ellipse luminance (%)')
		plt.title(titles[pairN])
		plt.savefig('../fig/' + sbj + 'LCp'+str(pairN))
		
	for i in range(2):
		savefigpmf(i)

### Run Main ###


if __name__ == '__main__':
	a = str(sys.argv[1])
	b = int(sys.argv[2])
	main(a,b)
