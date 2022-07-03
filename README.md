# Blood-Pressure-Prediction-with-Random-Forest

The purpose of this code is to predict SBP using training PPG and ABP waveforms from the MIMIC-III Waveform Database Matched Subset

convert.py is used to read MIMIC-III data and convert it into the .mat format. The data and processed data used is too large to provide here, but the original source can be found at https://physionet.org/content/mimic3wdb-matched/1.0/. The directories that the script looks for files in needs to be changed if run with different folder locations.

randomForest.py is used to read, process, and predict SBP with PPG data. There is an example for calls to each function in the file. The displayer function is used to manually view ABP and PPG waveforms, while the estimator function implements the RandomForest and plots the results
