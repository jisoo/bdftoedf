#!/usr/bin/env python3

import os
import mne
import pyedflib
from pyedflib import FILETYPE_BDF, FILETYPE_BDFPLUS, FILETYPE_EDF, FILETYPE_EDFPLUS
from concurrent.futures import ThreadPoolExecutor

input_path='~/Box/Blinded_aiTBS'

# DO NOT EDIT BELOW
futures = []
def main():
	e = ThreadPoolExecutor(max_workers=2)
	
	directory = os.path.expanduser(input_path)
	for root, dirs, files in os.walk(directory):
		for f in files:
			if not f.endswith('.bdf'): continue
			futures.append(e.submit(process, root, f))

	for idx, future in enumerate(concurrent.futures.as_completed(futures, timeout=180.0)):
		future.result()
		break
		
def process(root, f):
	try:
		# Get BDF
		filepath = os.path.join(root, f)
		raw = mne.io.read_raw_bdf(filepath)

		# Get Info
		sfreq = raw.info['sfreq']
		date = raw.info['meas_date']
		data = raw.get_data()
		channels = len(data)
		info = get_channel_info(data, raw, channels, sfreq)

		# Convert
		edf_filename = os.path.expanduser(get_edf_filename(filepath))
		f = pyedflib.EdfWriter(edf_filename, n_channels=channels, file_type=FILETYPE_EDFPLUS)
		
		f.setPatientCode(raw._raw_extras[0]['subject_info']['id'])
		f.setPatientName(raw._raw_extras[0]['subject_info']['name'])
		f.setSignalHeaders(info)
		f.setStartdatetime(date)
		f.writeSamples(data)
	except Exception as e:
		print(e)

def get_channel_info(data, raw, n, sfreq):
	arr = []

	dmin, dmax = -32768, 32767
	keys = list(raw._orig_units.keys())
	for i in range(n):
		try:
			d = {
			'label': raw.ch_names[i], 
			'dimension': raw._orig_units[keys[i]], 
			'sample_rate': raw._raw_extras[0]['n_samps'][i], 
			'physical_min': raw._raw_extras[0]['physical_min'][i], 
			'physical_max': raw._raw_extras[0]['physical_max'][i], 
			'digital_min':	raw._raw_extras[0]['digital_min'][i], 
			'digital_max':	raw._raw_extras[0]['digital_max'][i], 
			'transducer': '', 
			'prefilter': ''}
		except:
			d = {
			'label': raw.ch_names[i], 
			'dimension': raw._orig_units[keys[i]], 
			'sample_rate': sfreq, 
			'physical_min': data.min(), 
			'physical_max': data.max(), 
			'digital_min':	dmin, 
			'digital_max':	dmax, 
			'transducer': '', 
			'prefilter': ''}
		arr.append(d)

	return arr

def get_edf_filename(filepath):
	return filepath[:-4] + '.edf'

if __name__ == "__main__":
	main()
