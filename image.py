# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""label_image for tflite."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

import numpy as np

from PIL import Image

import tensorflow as tf # TF2
from time import sleep
from math import isnan
import time
import sys
import datetime
import subprocess
import sys
import os
import datetime
import traceback
import math
import base64
import json
from time import gmtime, strftime
import random, string
import psutil
import base64
import uuid
import socket 

external_IP_and_port = ('198.41.0.4', 53)  # a.root-servers.net
socket_family = socket.AF_INET

def load_labels(filename):
  with open(filename, 'r') as f:
    return [line.strip() for line in f.readlines()]

def IP_address():
        try:
            s = socket.socket(socket_family, socket.SOCK_DGRAM)
            s.connect(external_IP_and_port)
            answer = s.getsockname()
            s.close()
            return answer[0] if answer else None
        except socket.error:
            return None

# Get MAC address of a local interfaces
def psutil_iface(iface):
    # type: (str) -> Optional[str]
    import psutil
    nics = psutil.net_if_addrs()
    if iface in nics:
        nic = nics[iface]
        for i in nic:
            if i.family == psutil.AF_LINK:
                return i.address
# Random Word
def randomword(length):
 return ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()) for i in range(length))

# Fixed
packet_size=3000
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
ipaddress = IP_address()

imagename = sys.argv[1]
label_file = '/opt/demo/models/labels.txt'
model_file = '/opt/demo/models/mobilenet_v1_1.0_224_quant.tflite'
input_mean = 127.5
input_std = 127.5

start = time.time()
uniqueid = 'tensorflow_uuid_{0}_{1}'.format(randomword(3),strftime("%Y%m%d%H%M%S",gmtime()))
uuid2 = '{0}_{1}'.format(strftime("%Y%m%d%H%M%S",gmtime()),uuid.uuid4())

# tensorflow lite
interpreter = tf.lite.Interpreter(model_path=model_file)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# check the type of the input tensor
floating_model = input_details[0]['dtype'] == np.float32

# NxHxWxC, H:1, W:2
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
img = Image.open(imagename).resize((width, height))

# add N dim
input_data = np.expand_dims(img, axis=0)

if floating_model:
  input_data = (np.float32(input_data) - args.input_mean) / args.input_std

interpreter.set_tensor(input_details[0]['index'], input_data)

interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])
results = np.squeeze(output_data)

top_k = results.argsort()[-5:][::-1]
labels = load_labels(label_file)
end = time.time()
row = { }

counter = 0

for node_id in top_k:
    row['node_id_{0}'.format(str(counter))] = '{0}'.format(str(node_id))

    if floating_model:
      row['label_{0}'.format(str(counter))] = '{}'.format(str(labels[node_id].split(':',1)[1]))
      row['result_{0}'.format(str(counter))] = '{:08.6f}'.format(float(results[node_id]))
    else:
      row['label_{0}'.format(str(counter))] = '{}'.format(str(labels[node_id].split(':',1)[1]))
      row['result_{0}'.format(str(counter))] = '{:08.6f}'.format(float(results[node_id]  / 255.0 ))
    
    counter = counter + 1

row['uuid'] =  uniqueid
row['ipaddress']=ipaddress
row['runtime'] = str(round(end - start))  
row['host'] = os.uname()[1]
row['host_name'] = host_name
row['macaddress'] = psutil_iface('wlan0')
row['end'] = '{0}'.format( str(end ))
row['te'] = '{0}'.format(str(end-start))
row['systemtime'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
row['cpu'] = psutil.cpu_percent(interval=1)
usage = psutil.disk_usage("/")
row['diskusage'] = "{:.1f} MB".format(float(usage.free) / 1024 / 1024)
row['memory'] = psutil.virtual_memory().percent


row['id'] = str(uuid2)
json_string = json.dumps(row)
print(json_string)
