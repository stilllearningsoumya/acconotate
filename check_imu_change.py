from collections import Counter
from densratio import densratio
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

import time

np.random.seed(42)

def detect_outliers(data):
	# calculate summary statistics
	data_mean, data_std = np.mean(data), np.std(data)
	# identify outliers
	cut_off = data_std * 2
	lower, upper = data_mean - cut_off, data_mean + cut_off

	# identify outliers in the upper quartile
	outliers = [x for x in data if x > upper]
	print(outliers)

	# remove outliers
	outliers_removed = [x for x in data if x > lower and x < upper]

	return outliers,outliers_removed

def cluster_data(data,k=2):
	kmeans = KMeans(n_clusters=k, random_state=0).fit(data)
	print(kmeans.cluster_centers_)
	print(Counter(kmeans.labels_))

	pos = -1
	if(kmeans.cluster_centers_[0]>kmeans.cluster_centers_[1]):
		pos = 0
	else:
		pos = 1

	chosen_indices = []
	for i in range(len(kmeans.labels_)):
		if(kmeans.labels_[i]==pos):
			chosen_indices.append(i)
	return chosen_indices

def get_change_points(dir):
	score_files = glob.glob(dir+"*_change_scores.csv")
	k = 1
	for files in score_files:
		print(files)
		in_file = pd.read_csv(files)
		upper_outliers, data = detect_outliers(np.asarray(in_file['score']))
		chosen_indices =  cluster_data(np.asarray(data).reshape(-1,1))
		print(chosen_indices)
		out_file = open(dir+files.split("/")[-1].split(".")[0]+"_actual_changes.csv","w+")
		out_file.write("start-time,end-time\n")
		start_pos = str(in_file['start-time'][0])
		end_pos = -1
		changed_scores = []
		for index in chosen_indices:
			changed_scores.append(data[index])
		print(changed_scores)
		for i in range(len(in_file['score'])):
			if((in_file['score'][i] in changed_scores) or (in_file['score'][i] in upper_outliers)):
				end_pos = str(in_file['boundary-time'][i])
				out_file.write(start_pos+","+end_pos+"\n")
				start_pos = end_pos
		end_pos = str(in_file['end-time'][len(in_file['score'])-1])
		out_file.write(start_pos+","+end_pos+"\n")
		out_file.flush()
		out_file.close()


def check_imu_changes(dir,file,window_size=25):
	in_file =  pd.read_csv(file,delimiter=",")
	out_file = open(dir+file.split("/")[-1].split(".")[0]+"_change_scores.csv","w+")
	data = np.asanyarray(in_file[['x','y','z']])
	out_file.write("start-time,boundary-time,end-time,score\n")
	for i in range(0,len(data)-2*window_size,window_size):
		#Creating samples
		x = data[i:i+window_size,:]
		print(x.shape)
		y = data[i+window_size:i+2*window_size,:]
		print(y.shape)

		alpha = 0.1 #needed for RuLSif

		#calculating x to y
		densratio_obj = densratio(x, y, alpha=alpha)
		score_x_y = float(densratio_obj.alpha_PE)

		#calculating y to x
		densratio_obj = densratio(y, x, alpha=alpha)
		score_y_x  = float(densratio_obj.alpha_PE)

		'''Total change point score = score_x_y + score_y_x -- Taking absolute'''
		out_file.write(in_file['time'][i]+","+in_file['time'][i+window_size]+","+in_file['time'][i+2*window_size]+","+str(abs(score_x_y)+abs(score_y_x))+"\n")
		out_file.flush()

	out_file.close()

def main():
	start = time.time()
	main_directory = "sample_data/"
	dataset_directory = main_directory
	imu_file = dataset_directory+"u1_ewatch.csv"
	check_imu_changes(dataset_directory,imu_file)
	imu_file = dataset_directory+"u2_ewatch.csv"
	check_imu_changes(dataset_directory,imu_file)
	get_change_points(dataset_directory)
	end = time.time()
	print(end - start)

if __name__ == '__main__':
	main()