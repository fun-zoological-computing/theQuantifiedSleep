
import pandas as pd
import numpy as np  
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt  
#import matplotlib.pyplot as plt  
from datetime import datetime                          
import streamlit as st
try: 
    json_normalize = pd.json_normalize
except:
    from pandas.io.json import json_normalize

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

from tqdm.auto import tqdm

class tqdm:
    def __init__(self, iterable, title=None):
        if title:
            st.write(title)
        self.prog_bar = st.progress(0)
        self.iterable = iterable
        self.length = len(iterable)
        self.i = 0

    def __iter__(self):
        for obj in self.iterable:
            yield obj
            self.i += 1
            current_prog = self.i / self.length
            self.prog_bar.progress(current_prog)

#@st.cache(allow_output_mutation=True)            
def process_fitbit_sleep_data(fileList):
    full_sleep_df = None
    cnt = 0
    #tqdm(follow_links,title='Scrape in Progress. Please Wait.')
    for input_file in tqdm(fileList,title='Loading in fitbit data'):
        input_df = pd.read_json(input_file)
        detail_df = json_normalize(input_df['levels'])
        sleep_df = pd.concat([input_df, detail_df], axis =1)
        full_sleep_df = pd.concat([full_sleep_df, sleep_df], sort=True)
        
        progress_bar.progress(cnt/len(fileList))
        status_text.text("Data Reading %i%% Complete" % float(cnt/len(fileList)))    
        cnt+=1

    full_sleep_df['dateOfSleep']= pd.to_datetime(full_sleep_df['dateOfSleep'])
    full_sleep_df['dayOfWeek'] = full_sleep_df['dateOfSleep'].dt.day_name()
    full_sleep_df = full_sleep_df.set_index('dateOfSleep')
    full_sleep_df.sort_index(inplace=True)

    full_sleep_df['duration'] = full_sleep_df['duration']/(1000*60) # convert duration to minutes

    for col in ['rem','deep','wake','light']:
        full_sleep_df[col + '.%'] = 100*full_sleep_df['summary.' + col + '.minutes']/full_sleep_df['duration']

    full_sleep_df['startMin'] = pd.to_datetime(full_sleep_df['startTime']).dt.minute + 60 * pd.to_datetime(full_sleep_df['startTime']).dt.hour

    full_sleep_df['startMin'] = np.where(full_sleep_df['startMin'] < 240, full_sleep_df['startMin'] + 1440, full_sleep_df['startMin']) # handle v late nights

    full_sleep_df['endMin'] = pd.to_datetime(full_sleep_df['endTime']).dt.minute + 60 * pd.to_datetime(full_sleep_df['endTime']).dt.hour

    #remove rows which are not mainSleep == True (these are naps not sleeps)
    full_sleep_df = full_sleep_df[full_sleep_df.mainSleep != False]

    #remove column which are not needed/useful
    full_sleep_df.drop(['logId', 'data', 'shortData', 'infoCode', 'levels'], axis=1, inplace=True)

    return full_sleep_df

def process_fitbit_every_data(fileList):
    df = None
    cnt = 0
    for input_file in tqdm(fileList,title='Loading in fitbit data'):
        input_df = pd.read_json(input_file)

        if cnt>0:
            df = pd.concat([df, input_df], axis =1)
        else:
            df = input_df
        #print(df.shape)
        progress_bar.progress(cnt/len(fileList))
        status_text.text("Data Reading %i%% Complete" % float(cnt/len(fileList)))    
        cnt+=1

    if df is not None:
        df.sort_index(inplace=True)
    try:
        df['dateOfSleep']= pd.to_datetime(df['dateOfSleep'])
        df['dayOfWeek'] = df['dateOfSleep'].dt.day_name()
        df = df.set_index('dateOfSleep')
        df.sort_index(inplace=True)

        df['duration'] = df['duration']/(1000*60) # convert duration to minutes

        for col in ['rem','deep','wake','light']:
            df[col + '.%'] = 100*df['summary.' + col + '.minutes']/df['duration']

        df['startMin'] = pd.to_datetime(df['startTime']).dt.minute + 60 * pd.to_datetime(df['startTime']).dt.hour

        df['startMin'] = np.where(df['startMin'] < 240, full_sleep_df['startMin'] + 1440, df['startMin']) # handle v late nights

        df['endMin'] = pd.to_datetime(df['endTime']).dt.minute + 60 * pd.to_datetime(df['endTime']).dt.hour

        #remove rows which are not mainSleep == True (these are naps not sleeps)
        df = df[df.mainSleep != False]
    except:
        pass
    try:
    #remove column which are not needed/useful
        df.drop(['logId', 'data', 'shortData', 'infoCode', 'levels'], axis=1, inplace=True)
    except:
        pass
    return df
