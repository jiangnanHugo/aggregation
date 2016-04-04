#!/usr/bin/env python
from __future__ import print_function
import sqlite3 as lite
import cv2
import matplotlib.pyplot as plt
import preprocessing
import numpy as np
import math
import random
from sklearn.decomposition import PCA
import os
from tesseract_update import TesseractUpdate
__author__ = 'ggdhines'


def weighted_choice(choices):
# http://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    assert False, "Shouldn't get here"

def boltzman_sampling(confidences):
    temp = 2.5
    values = [math.exp(-c/temp) for c in confidences]

    # print(values)
    summed = sum(values)
    normalized_values = [c/float(summed) for c in values]
    return list(enumerate(normalized_values))

base = "/home/ggdhines/Databases/old_weather/aligned_images/Bear/1940/"
region_bound = (559,3282,1276,2097)

con = lite.connect('/home/ggdhines/to_upload3/active.db')

cur = con.cursor()

current_subject = None
masked_image = None

tess = TesseractUpdate()
tess.__create_blank_page__()

for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.abcdefghijkmnopqrstuvwxyz-"[:4]:

    # cur.execute("select * from characters where characters = \""+c+"\" and confidence < 80")
    # for r in cur.fetchall():
    #     subject_id,region,column,row,characters,confidence,lb_x,ub_x,lb_y,ub_y = r
    #
    #     if subject_id != current_subject:
    #         current_subject = subject_id
    #         fname = base + subject_id + ".JPG"
    #         image = cv2.imread(fname)
    #
    #         sub_image = image[region_bound[2]:region_bound[3],region_bound[0]:region_bound[1]]
    #
    #         gray = cv2.cvtColor(sub_image,cv2.COLOR_BGR2GRAY)
    #         # masked_image = preprocessing.__mask_lines__(gray)
    #
    #         height,width,_ = sub_image.shape
    #
    #     char_image = gray[lb_y:ub_y+1,lb_x:ub_x+1]
    #
    #     plt.imshow(char_image,cmap="gray")
    #     plt.title(characters + " -- " + str(confidence))
    #     plt.show()
    # continue



    # cur.execute("select * from characters where characters = \""+char+"\" and confidence < 80 and confidence > 70")
    cur.execute("select * from characters where characters = \""+char+"\" and confidence > 80")

    examples = []
    confidence_values = []
    height_values = []
    width_values = []

    for r in cur.fetchall():
        subject_id,region,column,row,characters,confidence,lb_x,ub_x,lb_y,ub_y = r
        # if subject_id != current_subject:
        #     current_subject = subject_id
        #     fname = base + subject_id + ".JPG"
        #     image = cv2.imread(fname)
        #
        #     sub_image = image[region_bound[2]:region_bound[3],region_bound[0]:region_bound[1]]
        #
        #     gray = cv2.cvtColor(sub_image,cv2.COLOR_BGR2GRAY)
        #     masked_image = preprocessing.__mask_lines__(gray)

        masked_image = cv2.imread("/home/ggdhines/to_upload3/"+subject_id+".jpg",0)
        height,width = masked_image.shape

        char_image = masked_image[lb_y:ub_y+1,lb_x:ub_x+1]

        # plt.imshow(char_image,cmap="gray")
        # plt.show()
        #
        # input_ = raw_input("is it correct?(y/n) ")
        # if input_ == "n":
        #     continue
        # assert input_ == "y"


        examples.append(char_image)
        confidence_values.append(confidence)
        chr_height = ub_y-lb_y+1
        chr_width = ub_x-lb_x+1

        height_values.append(chr_height)
        width_values.append(chr_width)

    if height_values != []:
        print("for character : " + char + " we have " + str(len(height_values)) + " samples")

        desired_height = int(np.median(height_values))
        desired_width = int(np.median(width_values))

        weights = boltzman_sampling(confidence_values)

        rescaled_examples = []
        for c in examples:
            c2 = cv2.resize(c,(desired_height,desired_width))
            # plt.imshow(c2)
            # plt.show()

            rescaled_examples.append(c2)

        for i in range(10):
            samples = [weighted_choice(weights) for i in range(40)]

            image_list = [rescaled_examples[j] for j in samples]
            s = image_list[0].shape

            flatten_list = [im.reshape((im.shape[0]*im.shape[1])) for im in image_list]
            pca = PCA(n_components=1)
            pca_images = pca.fit_transform(flatten_list)
            # print(sum(pca.explained_variance_ratio_))

            average_image = np.mean(image_list,axis=0)

            pca_average = np.median(pca_images,axis=0)
            new_average = pca.inverse_transform(pca_average)
            average_image = new_average.reshape(s)

            cv2.normalize(average_image,average_image,0,255,cv2.NORM_MINMAX)
            average_image = average_image.astype(np.uint8)
            # print(average_image)

            # ret,close = cv2.threshold(average_image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            # kernel = np.ones((10,10),np.uint8)
            # close = cv2.morphologyEx(close,cv2.MORPH_DILATE,kernel,iterations = 1)

            tess.__add_char__(char,average_image)

        # raw_input("enter something")

