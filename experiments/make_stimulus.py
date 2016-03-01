
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 14:40:18 2015

@author: Administrator
"""

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pdb
import unittest
import random
import sys
import pandas as pd
import time
import os


def image_to_array(fname, in_format = 'png'):
	"""
	read specified image file (default: png), converts it to grayscale and into numpy array
	input:
	------
	fname	   - name of image file
	in_format   - extension (png default)
	output:
	-------
	numpy array
	"""
	im = Image.open('%s.%s' %(fname, in_format)).convert('L')
	im_matrix = [ im.getpixel(( y, x)) for x in range(im.size[1]) for y in range(im.size[0])]
	im_matrix = np.array(im_matrix).reshape(im.size[1], im.size[0])
	
	return im_matrix

def array_to_image(stimulus_array = None, outfile_name = None, out_format = 'bmp'):
	"""
	convert numpy array into image (default = '.bmp') in order to display it with vsg.vsgDrawImage
	input:
	------
	stimulus_array  -   numpy array
	outfile_name	-   ''
	out_format	  -   'bmp' (default) or 'png'
	output:
	-------
	image		   -   outfile_name.out_format
	"""
	im_row, im_col = stimulus_array.shape
	im_new = Image.new("L",(im_col, im_row))
	im_new.putdata(stimulus_array.flatten())
	im_new.save('%s.%s' %(outfile_name, out_format), format = out_format)

def normalize_image2(stim_in, new_min = 1, new_max = 256):
	"""
	input:
	----------
	stim_in	 - numpy array
	new_min
	new_max
	scale image range from [old_min, old_max] to [new_min=1, new_max = 256]
	"""
	stim = stim_in.copy()
	stim = stim - stim.min()
	stim = stim/float(stim.max())
	stim = stim * (new_max - new_min)
	stim = stim + new_min
	if stim.max() > 1:
		stim.round()
	return stim

def raised_cosine(radius, plateau_radius, circle = 1):
	"""
	create 2 dimensional cosine with plateau of diameter = 2 * plateau_radius
	:input:
	
	:output:
	"""
	x_size = 2 * radius * circle
	y_size = 2 * radius
	x,y  = np.meshgrid(np.linspace(-1, 1, y_size), np.linspace(-1, 1, x_size))
	# clipping of corners - outside unit circle - to 1
	dist = np.fmin(1, np.sqrt(x**2 + y**2))
	
	# set everything within plateau radius to zero
	dist = dist - dist[radius*circle, radius - plateau_radius]
	dist[dist < 0] = 0
	
	# scale image such that maximum is 1
	dist = normalize_image2(dist, 0, 1)
	
	return (np.cos(dist * np.pi) + 1) / 2
def ellipse(radius, circle=1):
	"""
	radius:
	circle: circle==1, ellipse AR < 1: H>V, AR > 1: V>H
	output:
	---------
	np.array consisting of [1, 0]
	"""
	y_size = radius * 2
	x_size = y_size * circle
	x = np.linspace(-1, 1, y_size)
	y = np.linspace(-1, 1, x_size)
	dist = np.fmin(1, np.sqrt(x[np.newaxis, :] ** 2 + y[:, np.newaxis] ** 2))
	d = dist<1
	return d.astype('int')



def make_ellipse(radius):
	"""
	create ellipse of width = 2*radius and height = radius
	output:
	---------
	np.array consisting of [1, 0]
	"""
	x,y = np.meshgrid(np.linspace(-radius*0.5, radius*0.5, 2 * radius), np.linspace(-radius, radius, 2 * radius))
	d = np.sqrt(x**2 + y**2)
	d = d<=0.5*radius
	return d.astype('int')


def make_gauss_ellipse(radius):
	"""
	create ellipse with gaussian border profile of width = 2*radius and height = radius
	output:
	---------
	np.array of floats between [0,1]
	! as of June, 13, 2012 with adelson_double experiment - gaussian ellipse has double intensity in order to equate summed intensity over ellipse area
	"""
	x,y  = np.meshgrid(np.arange(-radius, radius), np.arange(-radius, radius))
	blob = 2 * np.exp(- ((( 0.5 * x )**2 + y**2)/(2.0 * radius) ))
	return blob

def add_increment(stimulus=None, increment=None, position=None):
	"""
	:Input:
	----------
	stimulus	- numpy array of original stimulus
	increment   - numpy array of to be added increment
	position	- tuple of center coordinates within stimulus where increment should be placed
	:Output:
	----------
	"""
	inc_y, inc_x  = increment.shape
	pos_y, pos_x  = position
	
	x1 = pos_x - int(inc_x/2.0)
	x2 = pos_x + int(inc_x/2.0)
	y1 = pos_y - int(inc_y/2.0)
	y2 = pos_y + int(inc_y/2.0)
	
	for k, c in enumerate(range(x1, x2)):
		for l, r in enumerate(range(y1, y2)):
			if increment[l,k] != 0:
				stimulus[r, c] = increment[l, k]
	return stimulus
	
def normalize_image(stim_in, new_min = 1, new_max = 256):
	"""
	scale image range from [old_min, old_max] to [new_min=1, new_max = 256]
	"""
	stim = stim_in.copy()
	stim = stim - stim.min()
	stim = stim/float(stim.max())
	stim = stim * (new_max - new_min)
	stim = stim + new_min
	return stim.round()

def norm_image(fname, bg=120):
	"""
	read image, normalize to range [min, max] and set background
	input
	=====
	fname - adelson checkerboard
	background
	
	output
	======
	image numpy array
	"""
	stim_in = image_to_array(fname)
	stim	= normalize_image(stim_in, 1,256)
	stim[stim == 128] = bg
	return stim

def resize_array(arr, factor):
	"""
	from Torsten Betz' utils.py
	Return a copy of an array, resized by the given factor. Every value is
	repeated factor[d] times along dimension d.

	Parameters
	----------
	arr : 2D array
		  the array to be resized
	factor : tupel of 2 ints
			 the resize factor in the y and x dimensions

	Returns
	-------
	An array of shape (arr.shape[0] * factor[0], arr.shape[1] * factor[1])
	"""
	x_idx = np.arange(0, arr.shape[1], 1. / factor[1]).astype(int)
	y_idx = np.arange(0, arr.shape[0], 1. / factor[0]).astype(int)
	return arr[:, x_idx][y_idx, :]


########################
# [plainview] make local luminance uniform
##########################

def unify_localLum(a):
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

	
	# 0 for dark comparison, 1 for light comarison
	if a == 1:
		mask32_fname = '../stimuli/mask_ShLi_32' # block1 reference light: within shadow, light check
		mask32 = image_to_array(mask32_fname)
		templateImg_mat[mask32 != 0] = templateImg_mat[428,585]
	if a == 0:
		mask24_fname = '../stimuli/mask_PlDa_24' # block2 reference dark: outside shadow, dark check (near the shadow)
		mask24 = image_to_array(mask24_fname)
		templateImg_mat[mask24 != 0] = templateImg_mat[428,585]
		#~ mask26_fname = '../mask_PlDa_26' # block2 reference dark: outside shadow, dark check (by the upper edge)
		#~ mask26 = image_to_array(mask26_fname)
		#~ templateImg_mat[mask26 != 0] = templateImg_mat[148,151]

	# save the rendered image
	array_to_image(templateImg_mat,'../stimuli/renTemplate','png')


#############################################
# Generate stimulus with ellipses !!!
#############################################

def make_stimulus(a, img, elipse, lumS, lumCD, lumCL, sbj):

	# S, check 43 : position=(428,585) 
	# CD, check 35 : position=(337,442)
	# CL, check 32 : position=(477,435)
	# CDD, check 26 : position= (294,306)
	# CDD, check 24 : position= (383,295)
	
	#check 43, S
	add_increment(stimulus=img, increment=elipse*lumS, position=(428, 585))
	#check 35, CD
	add_increment(stimulus=img, increment=elipse*lumCD, position=(337, 442))
	if a == 1:
		#check 32, CL
		add_increment(stimulus=img, increment=elipse*lumCL, position=(477, 435))
	if a == 0:
		#check 24, CDD
		add_increment(stimulus=img, increment=elipse*lumCL, position=(383, 295))
	
	if not os.path.exists('../stimuli/'+ sbj):
		os.makedirs('../stimuli/'+ sbj)
		
	if a == 1:
		outfile_name = '../stimuli/'+ sbj +'/lS' + str(int(lumS)) + '_CD' + str(int(lumCD)) + '_CL' + str(int(lumCL))
	if a == 0:
		outfile_name = '../stimuli/'+ sbj +'/dS' + str(int(lumS)) + '_CD' + str(int(lumCD)) + '_CDD' + str(int(lumCL))
	
	array_to_image(img, outfile_name, 'png')

	image = Image.open(outfile_name + '.png')
	image.save(outfile_name+'.png', quality=100)

def main (scd, a, radius=25):
	unify_localLum(a) # make the luminance of the checks containing the ellipses uniform  
	template = '../stimuli/renTemplate' # set the template image file
	templateImg = image_to_array(template)
	
	## import the 6 S-CD luminance pairs from the base experiments
	scd_pairs = pd.read_csv('../results/base_inc_dec_avg_' + scd + '.csv', sep=" ", index_col=0)
	LumS = scd_pairs['LumS'].values[[0,1,6,7]]
	LumCD = scd_pairs['LumCD'].values[[0,1,6,7]]
	#~ LumS = scd_pairs['LumS'].values[[2,3,4,5]]
	#~ LumCD = scd_pairs['LumCD'].values[[2,3,4,5]]
	LumCL = np.array([0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2])
	
	ellipse = make_ellipse(radius)
	
	if a == 1:
		for i in range(len(LumS)):
			for j in range(len(LumCL)):
		#~ for i in range(1):
			#~ for j in range(1):	
				starttime = time.time()
				print "generating the image #", len(LumCL)*i+j+1
				make_stimulus(a=a, img=templateImg, elipse=ellipse, lumS=LumS[i], lumCD=LumCD[i], lumCL=LumS[i]*LumCL[j], sbj=scd)
				print time.time()-starttime, "sec", ((len(LumCL)*i+j+1)/(len(LumCL)*len(LumS)))*100, "% done"
	if a == 0:
		for i in range(len(LumS)):
			for j in range(len(LumCL)):
		#~ for i in range(1):
			#~ for j in range(1):	
				starttime = time.time()
				print "generating the image #", len(LumCL)*i+j+1
				make_stimulus(a=a,img=templateImg, elipse=ellipse, lumS=LumS[i], lumCD=LumCD[i], lumCL=LumCD[i]*LumCL[j], sbj=scd)
				print time.time()-starttime, "sec", ((len(LumCL)*i+j+1)/(len(LumCL)*len(LumCD)))*100, "% done"
  
### Run Main ###
# argv1 = subject initials
# argv2 = dark or light

if __name__ == '__main__':
	SCD = str(sys.argv[1])
	DorL = int(sys.argv[2])
	main(scd=SCD, a=DorL)
