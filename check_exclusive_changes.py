from collections import Counter
from datetime import datetime
import pandas as pd

fmt = "%H:%M:%S.%f"

def check_correctness(start_time,end_time):
	start_time = datetime.strptime(start_time,fmt)
	end_time = datetime.strptime(end_time,fmt)
	assert start_time<end_time

def is_time_overlapping(start_time,end_time,global_start_time,global_end_time):
	#print(start_time+"&"+end_time+"in"+global_start_time+"to"+global_end_time)
	start_time = datetime.strptime(start_time,fmt)
	end_time = datetime.strptime(end_time,fmt)
	global_start_time = datetime.strptime(global_start_time,fmt)
	global_end_time = datetime.strptime(global_end_time,fmt)
	assert end_time>start_time
	assert global_end_time>global_start_time
	if((start_time>global_start_time and end_time<global_end_time)):
	#if((start_time>global_start_time and start_time<global_end_time) or (end_time>global_start_time and end_time<global_end_time)):	
		#print(True)
		return True
	else:
		return False

def read_change_files(filename,if_audio=False):
	change_list = []
	in_file = pd.read_csv(filename)
	if(if_audio):
		split_list = []
		for i in range(len(in_file['start-time'])):
			data = []
			data.append(in_file['start-time'][i])
			data.append(in_file['end-time'][i])
			check_correctness(in_file['start-time'][i],in_file['end-time'][i])
			split_list.append(in_file['splitid'][i])
			change_list.append(data)
		return change_list,split_list
	else:
		for i in range(len(in_file['start-time'])):
			data = []
			data.append(in_file['start-time'][i])
			data.append(in_file['end-time'][i])
			check_correctness(in_file['start-time'][i],in_file['end-time'][i])
			change_list.append(data)
		return change_list

def check_exclusive_changes(u1_changes,u2_changes,global_audio_change,split_id):
	u1_exclusive_changes = []
	u2_exlcusive_changes = []
	
	for i in range(len(global_audio_change)):
		is_exclusive = False
		exclusive_user = -1
		print(split_id[i])
		for j in range(len(u1_changes)):
			if(is_time_overlapping(u1_changes[j][0],u1_changes[j][1],global_audio_change[i][0],global_audio_change[i][1])):
				print("U1")
				is_exclusive = True
				exclusive_user = 0
				break
		for k in range(len(u2_changes)):
			if(is_time_overlapping(u2_changes[k][0],u2_changes[k][1],global_audio_change[i][0],global_audio_change[i][1])):
				print("U2")
				if(is_exclusive):
					is_exclusive = False
					exclusive_user = -1
				else:
					is_exclusive = True
					exclusive_user = 1
				break

		if(is_exclusive):
			assert exclusive_user > -1
			if(exclusive_user==0):
				u1_exclusive_changes.append(split_id[i])
			else:
				u2_exlcusive_changes.append(split_id[i])
	
	# assert len(u1_exclusive_changes) > 0
	# assert len(u2_exlcusive_changes) > 0
	return u1_exclusive_changes,u2_exlcusive_changes

def checking_activity(exclusive_splits,user,directory):
	activity_list = []
	audio_act = pd.read_csv(directory+"audio_activity_log.csv")
	for splitid in exclusive_splits:
		for i in range(len(audio_act['splitid'])):
			if(splitid==audio_act['splitid'][i]):
				activity_list.append(audio_act['activity'][i])
	print("For user "+user+" the activity is "+str(Counter(activity_list))+" decision made from "+str(len(exclusive_splits))+" splits.")

	majority = Counter(activity_list)
	if(len(activity_list)<=0):
		print("Null")
		return None
	if(len(majority)==1):
		print("Single Majority")
		return majority.most_common()[0][0]
	else:
		#print(majority.most_common()[0][1])
		#Tie
		if(majority.most_common()[0][1] == majority.most_common()[1][1]):
			print("No Conclusion")
			return None
		else:
			majority_activity = majority.most_common()[0][0]
			return majority_activity

def main():
	main_directory = "sample_data/"
	dataset_directory = main_directory
	u1_file = dataset_directory + "u1_ewatch_change_scores_actual_changes.csv"
	u1_changes = read_change_files(u1_file)#returns list of lists with 0th col start time and 1st col end time
	#print(u1_changes)
	u2_file = dataset_directory + "u2_ewatch_change_scores_actual_changes.csv"
	u2_changes = read_change_files(u2_file)
	#print(u2_changes)
	global_audio_change,split_list = read_change_files(dataset_directory+"split_info.csv",if_audio=True)
	#print(global_audio_change)
	u1_exclusive_changes,u2_exclusive_changes = check_exclusive_changes(u1_changes,u2_changes,global_audio_change,split_list)
	print(u1_exclusive_changes)
	print(u2_exclusive_changes)

	assert len(set(u1_exclusive_changes).intersection(set(u2_exclusive_changes))) == 0

	u1_act = checking_activity(u2_exclusive_changes,"U1",dataset_directory) #U2 exclusive means U2 has changed (or stopped) thus chances for detecting U1
	u2_act = checking_activity(u1_exclusive_changes,"U2",dataset_directory) #U1 exclusive means U1 has changed (or stopped) thus chances for detecting U2
	out_file = open(dataset_directory+"activity2user.csv","w+")
	if(u1_act==u2_act):
		print("Conflict")
		out_file.write("u1,act1,u2,act2\n")
		#If U1 has more exclusive changes it means it has probably stopped more thus U1 is opportunistic
		if(len(u1_exclusive_changes)>len(u2_exclusive_changes)):
			print("Opportunistic User: U1")
			print("Using Majority Rule: U2 Activity: "+ u2_act)
			out_file.write("u1,"+str(None)+",u2,"+str(u2_act))
		else:
			print("Opportunistic User: U2")
			print("Using Majority Rule: U1 Activity: "+ u1_act)
			out_file.write("u1,"+str(u1_act)+",u2,"+str(None))
		out_file.flush()
		out_file.close()

	else:
		out_file.write("u1,act1,u2,act2\n")
		print("U1 Activity: "+str(u1_act)+" U2 Activity: "+str(u2_act))
		out_file.write("u1,"+str(u1_act)+",u2,"+str(u2_act))
		out_file.flush()
		out_file.close()

if __name__ == '__main__':
	main()