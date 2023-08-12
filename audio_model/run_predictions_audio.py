from vggish_input import waveform_to_examples, wavfile_to_examples
import math
import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from tensorflow.keras.models import load_model
import vggish_params
from pathlib import Path
import ubicoustics
import wget
import glob
from natsort import natsorted

print("Code Running")
###########################
# Download model, if it doesn't exist
###########################
MODEL_URL = "https://www.dropbox.com/s/cq1d7uqg0l28211/example_model.hdf5?dl=1"
MODEL_PATH = "models/example_model.hdf5"
print("=====")
print("Checking model... ")
print("=====")
model_filename = "models/example_model.hdf5"
ubicoustics_model = Path(model_filename)
if (not ubicoustics_model.is_file()):
	print("Downloading example_model.hdf5 [867MB]: ")
	wget.download(MODEL_URL,MODEL_PATH)

###########################
# Load Model
###########################
#context = ubicoustics.workshop
context_mapping = ubicoustics.context_mapping
trained_model = model_filename
other = True
selected_context = 'workshop' #change this for another context

print("Using deep learning model: %s" % (trained_model))
model = load_model(trained_model)
context = context_mapping[selected_context]
graph = tf.get_default_graph()

print(context)
label = dict()
for k in range(len(context)):
	for key in ubicoustics.labels.keys():
		if(key==context[k]):
			label[ubicoustics.labels[key]] = context[k]
			
print(label)
###########################
# Read Wavfile and Make Predictions
###########################
directory = "../sample_data/"
out_file = open(directory+"audio_activity_log.csv","w+")
out_file.write("splitid,activity,confidence\n")

split_dir = directory+"cpsd_splits/"
filelist = natsorted(glob.glob(split_dir+"split_*.wav"))

for selected_file in filelist:
	print(selected_file)
	x = wavfile_to_examples(selected_file)
	with graph.as_default():
		
		x = x.reshape(len(x), 96, 64, 1)
		predictions = model.predict(x)

		#print(predictions)
		string=""
		max_confidence = -math.inf
		for k in range(len(predictions)):
			prediction = predictions[k]
			#print(prediction)
			m = np.argmax(prediction)
			#print(m)
			if(m in label.keys()):
				print("Prediction: %s (%0.2f)" % (ubicoustics.to_human_labels[label[m]], prediction[m]))
				if(prediction[m]>max_confidence):
					max_confidence = prediction[m]		
					string=ubicoustics.to_human_labels[label[m]]+","+str(prediction[m])
		if(string!=""):
			out_file.write(selected_file.split("/")[-1].split(".")[0]+","+string+"\n")

out_file.flush()
out_file.close()