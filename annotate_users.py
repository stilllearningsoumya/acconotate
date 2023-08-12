from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

global_activity_set = set(["Hammering","Saw In-Use"])

fmt = "%H:%M:%S.%f"
def is_time_included(start_time,end_time,time):
	start_time = datetime.strptime(start_time,fmt)
	end_time = datetime.strptime(end_time,fmt)
	time = datetime.strptime(time,fmt)
	assert start_time<end_time
	if(time>=start_time and time<=end_time):
		return True
	return False

'''we first fit a nearest neighbor algorithm
with the data from the changed-windows (colwise mean)
then we query that model with the pattern observed
from the known sequence.'''
def query_similar_patterns(directory,sensor_file,user,activity,pattern,k=1):
	#read change windowed dataset for start-time end-time
	change_windows = ''
	change_windows = pd.read_csv(directory+user+"_ewatch_change_scores_actual_changes.csv")

	training_patterns = []
	for i in range(len(change_windows['start-time'])):
		data = []
		for j in range(len(sensor_file['time'])):
			temp = []
			if(is_time_included(change_windows['start-time'][i],change_windows['end-time'][i],sensor_file['time'][j])):
				temp.append(sensor_file['x'][j])
				temp.append(sensor_file['y'][j])
				temp.append(sensor_file['z'][j])
				data.append(temp)
		data = np.asanyarray(data)
		training_patterns.append(np.mean(data,axis = 0))

	assert len(training_patterns) == len(change_windows['start-time'])

	training_patterns = np.asanyarray(training_patterns)
	#print(training_patterns)

	#fitting training patterns
	#these are actually unknown patterns
	#the known pattern is the argument
	neigh = NearestNeighbors(n_neighbors=k)
	neigh.fit(training_patterns)

	#querying with the known pattern
	window_indices = neigh.kneighbors([pattern])[1][0]
	distances = neigh.kneighbors([pattern])[0][0] #plot these distances 
	print(window_indices)
	print(distances)

	out_file = ""
	out_file = open(directory+user+"_"+"distances"+"_"+str(k)+".txt","w+")

	string = ""
	for dists in distances:
		string+=str(dists)+","
	out_file.write(string[:-1])
	out_file.close()

	start_time_list = []
	end_time_list = []
	for index in window_indices:
		start_time_list.append(change_windows['start-time'][index])
		end_time_list.append(change_windows['end-time'][index])
	return start_time_list, end_time_list

def annotate_user(directory,user,activity,k=1):
	#read the audio split files to find the splits when the "activity" was detected
	splits = pd.read_csv(directory+"audio_activity_log.csv")
	#print(splits)
	split_ids = splits.loc[splits["activity"] == activity].sort_values(by=['confidence'],ascending=False)
	chosen_split = split_ids.iloc[0,0] #choose the audio split with maximum confidence
	print(chosen_split)
	
	#get timestamps for this particular split
	split_info = pd.read_csv(directory+"split_info.csv")
	#print(split_info)
	timestamps = split_info.loc[split_info["splitid"] == chosen_split]
	print(timestamps)
	start_time = timestamps.iloc[0,1]
	end_time = timestamps.iloc[0,2]
	print('{}--{}'.format(start_time, end_time))

	#get the pattern from the raw IMU signal for this timestamp
	#small change beacuse of the naming
	#if these files return not found then it means
	#there is some error
	in_file = directory+user+"_ewatch"
	in_file = pd.read_csv(in_file+".csv")
	
	pattern = []
	for i in range(len(in_file['time'])):
		temp = []
		if(is_time_included(start_time,end_time,in_file['time'][i])):
			temp.append(in_file['x'][i])
			temp.append(in_file['y'][i])
			temp.append(in_file['z'][i])
			pattern.append(temp)
	#print(pattern)
	pattern = np.asanyarray(pattern)
	pattern = np.mean(pattern, axis = 0)#colwise average
	print(pattern)
	start_time_list, end_time_list = query_similar_patterns(directory,in_file,user,activity,pattern,k)
	print(start_time_list,end_time_list)

	#create annotated data
	out_file = ""
	out_file = open(directory+user+"_"+"annotated_data"+"_"+str(k)+".csv","w+")
	out_file.write("x,y,z,time,label\n")
	for i in range(len(start_time_list)):
		for j in range(len(in_file['time'])):
			if(is_time_included(start_time_list[i],end_time_list[i],in_file['time'][j])):
				out_file.write(str(in_file['x'][j])+","+str(in_file['y'][j])+","+str(in_file['z'][j])+","+str(in_file['time'][j])+","+activity+"\n")
	out_file.close()

def main():
	main_directory = "sample_data/"
	dataset_directory = main_directory
	U1 = "u1" #Assign the user names
	U2 = "u2"
	print("U1:", U1, "U2:", U2)

	#read the activity2user mapping file
	act2user = pd.read_csv(dataset_directory+"activity2user.csv")
	act1 = str(act2user["act1"].iloc[0])
	act2 = str(act2user["act2"].iloc[0])

	#if activity for only one user can be recognised
	if(act1 == "None"):
		act1 = global_activity_set.difference(set([act2]))
		act1 = next(iter(act1))
	if(act2 == "None"):
		act2 = global_activity_set.difference(set([act1]))
		act2 = next(iter(act2))

	print("U1 Act:", act1, "U2 Act:", act2)
	
	#annotate user dataset
	for k in range(3,17,2):
		annotate_user(dataset_directory,U1,act1,k = k)
		annotate_user(dataset_directory,U2,act2,k = k)

if __name__ == '__main__':
	main()