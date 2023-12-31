from scipy import stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import scipy
import os

def fit_timeseries(tlist,ylist):
    slope, intercept, r_value, p_value, std_err = stats.linregress(tlist, ylist)
    velocity = round(slope,7)
    uncertainty = round(std_err,7)
    #print(f'This is the velocity and uncertainty for this timeseries: {velocity}, {uncertainty}')
    return velocity, uncertainty

def fit_velocities(filename):
    dset = pd.read_csv(filename, delim_whitespace=True)
    
    change_east = dset['__east(m)']
    change_north = dset['_north(m)']
    change_up = dset['____up(m)']
    time = dset['yyyy.yyyy']
    
    e_velocity, e_uncertainty = fit_timeseries(time, change_east)
    n_velocity, n_uncertainty = fit_timeseries(time, change_north)
    u_velocity, u_uncertainty = fit_timeseries(time, change_up)
    return e_velocity, e_uncertainty, n_velocity, n_uncertainty, u_velocity, u_uncertainty

def get_coordinates(filename):
    dset = pd.read_csv(filename, delim_whitespace=True)
    
    latlist = dset['_latitude(deg)']
    lonlist = dset['_longitude(deg)']
    heightlist = dset['__height(m)']
    
    avg_lat = np.mean(latlist)
    avg_lon = np.mean(lonlist)
    avg_height = np.mean(heightlist)
    #print(f'Avg lat: {avg_lat}; Avg lon: {avg_lon}; Avg height: {avg_height}')
    
    return avg_lat, avg_lon, avg_height

def fit_all_velocities(folder,pattern):
    results = []
    file_list = glob.glob('/Users/jasonboryszewski/Downloads/timeseries/*.tenv3')
    
    for file in file_list:
        filename = os.path.basename(file)
        sitename = filename.split('.')[0]
        coordinates = get_coordinates(file)
        velocities = fit_velocities(file)
        dset = pd.read_csv(filename, delim_whitespace=True)
        
        site_info = {
            'sitename': sitename,
            'avg_lat': coordinates[0],
            'avg_lon': coordinates[1],
            'avg_height': coordinates[2],
            'e_velocity': velocities[0],
            'e_uncertainty': velocities[1],
            'n_velocity': velocities[2],
            'n_uncertainty': velocities[3],
            'u_velocity': velocities[4],
            'u_uncertainty': velocities[5]
            }
        results.append(site_info)
    df = pd.DataFrame(results)
    print(df)
    return df

def fit_tide_gauge(time, sealevel, sealvl_file):
    dset_sealvl = pd.read_csv(sealvl_file, header=None, sep=';')

    time = dset_sealvl[0]
    sealevel = dset_sealvl[1]

    slope, intercept, r_value, p_value, std_err = stats.linregress(time, sealevel)
    
    return slope

def all_tide_changes(folder, pattern):
    tide_changes = []
    rlr_list = glob.glob(os.path.join(folder, pattern))

    for file in rlr_list:
        filename = os.path.basename(file)
        sitename = filename.split('.')[0]
        slope = fit_tide_gauge(None, None, file)  # Pass the filename to the function

        if slope is not None:
            site_info = {'sitename': sitename, 'rate_change': slope}
            tide_changes.append(site_info)

    df = pd.DataFrame(tide_changes)
    print(df)
    return df