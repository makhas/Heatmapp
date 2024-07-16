import pandas as pd
import numpy as np
import requests
import folium                           # Mapping application
from folium import plugins              # Used to plot routes on a map
from folium.plugins import HeatMap
import pickle
import os
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import psycopg2 as pg
 # load in db credentials from .env. Ask teammate for this file and place in same dir
#import
import argparse
parser= argparse.ArgumentParser(description="load all locations for drives starting in a given state")
parser.add_argument("--state", help="Generate drive data of state", required=True)


def downsample_loc_gps(df, did, d=.1):
    #each minute of a drive has its own row in dataframe, giving 61 or 122 locations (1-2 Hz)
    #to save memory, we can plot each minute sparsely.
    #set d=0 to sample the first point of each minute
    #set d to an integer greater than 1 to sample the first point of every d'th minute.
    data=pd.DataFrame({'lat': [], 
                    'long': [], })
    #Count the minutes of drive. 
    k = len(df) #n minutes
    #for each minute, apply density d. d \in [0,1], and d*len(min) means we will only save the proportion d in memory to plot
    if d>1 and int(d)==d:
        n = np.linspace(0, k-1, int(k//d))
        
        d = 0
    elif d>1:
        raise ValueError("If the density is >1, please select an integer to unambiguously sample drives. An integer density d>1 means every d'th minute of the drive is sampled")
    else:
        n = range(k)
    for i in n:
        dmin = (df.iloc[i]['values'])
        if not bool(dmin):
            pass
        else:
            m=(len(dmin))
            dmin = pd.Series(dmin)
            if d == 0:
                lat = dmin[0]['lat']
                long = dmin[0]['long']
                data=data.append({'lat':lat,
                                  'long': long}, ignore_index=True)
            else:
                sparsem = [int(x) for x in np.linspace(0, m-1, int(m*d))]
                sparsed=dmin[sparsem]
                for j in sparsem:
                    lat = sparsed[j]['lat']
                    long=sparsed[j]['long']
                    data=data.append({'lat':lat,
                                      'long': long}, ignore_index=True)

    return data
##state, date, timeOfDay [0,23]
def read_state_loc(state='CO'):
    load_dotenv()
    connect_str = "dbname='{dbname}' user='{username}' host='{host}' port='{port}' password='{password}'".format(
    dbname=os.environ.get('DB_NAME'),
    username=os.environ.get('DB_USERNAME'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT'),
    password=os.environ.get('DB_PASSWORD')
    )   
    engine = pg.connect(connect_str)
    print('connected to DB')
    drives_sql = f"""
        select distinct
            d.id as drive_id, -- drive ID
            d.user_id, 
            d.start_date,
            d.start_area
        from drives d
        where start_country = 'US'
            AND start_area= '{state}'
            AND (CAST(d.duration AS FLOAT)/60) > 2 -- > 2 minutes
            AND d.start_date_timestamp::DATE > now()::DATE - INTERVAL '1 YEAR'
            AND d.distance >= 1000  -- > 1km
        GROUP BY d.id
    """
    df = pd.read_sql(drives_sql, con=engine)    
    filepath=f"Shubham/state_locations/{state}routes.csv"
    driveIdtuple = tuple(df['drive_id'].values)
    print(f'queried {len(driveIdtuple)} {state} drives')
    n = len(driveIdtuple)
    batch_size=50
    num_batches = n//batch_size
    
    print(num_batches,"batches")
    print(f"{n} drives in {state}")
    heatdata=pd.DataFrame({'lat': [], 
                           'long': [], })
    for b in tqdm(range((num_batches))):
        #print(b,'b')
        batch=driveIdtuple[b*batch_size:(b+1)*batch_size]
        
        query = f'''
            select
                drive_id,
                values
            from
                locations WHERE drive_id in {batch}'''
        batch_df=pd.read_sql(query, con=engine)
        ids=pd.unique(batch_df['drive_id'])
        for did in (ids):
            drive=batch_df[batch_df['drive_id']==did]
            datad=downsample_loc_gps(drive, did, d=0)
            heatdata=heatdata.append(datad)
            #print(np.shape(heatdata))
    heatdata.to_csv(filepath)
    print(f"saved route data for {state}")
    print(np.shape(heatdata))
    return heatdata

def generate_map(state='CO', heatdata=None):
    if heatdata is None:
        filepath=f"Shubham/state_locations/{state}routes.csv"
        df = pd.read_csv(filepath)
        heatdata = df.drop('Unnamed: 0', axis=1)
    mapit = None
    mapit = folium.Map( location=[heatdata.iloc[0]['lat'], heatdata.iloc[0]['long']], zoom_start=6 ) #[44.425213353096744, -103.83130157118033]

    

    HeatMap(heatdata).add_to(mapit)
    #state = states[j]
    mapit.save( f'Shubham/templates/heatmap{state}.html')


if __name__ == "__main__":
    args = parser.parse_args()
    state=args.state
    print('args read')
    heatdata =None
    heatdata = read_state_loc(state=state)
    generate_map(state=state, heatdata=heatdata)
