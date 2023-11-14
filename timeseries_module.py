from scipy import stats
import glob
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import pygmt

def fit_timeseries(tlist,ylist):
    slope, intercept, r_value, p_value, std_err = stats.linregress(tlist, ylist)
    velocity = round(slope,7)
    uncertainty = round(std_err,7)
    #print(f'This is the velocity and uncertainty for this timeseries: {velocity}, {uncertainty}')
    return velocity, uncertainty

def fit_velocities(filename):
    dset = pd.read_csv(filename, sep='\s+')
    
    change_east = dset['__east(m)']
    change_north = dset['_north(m)']
    change_up = dset['____up(m)']
    time = dset['yyyy.yyyy']
    
    e_velocity, e_uncertainty = fit_timeseries(time, change_east)
    n_velocity, n_uncertainty = fit_timeseries(time, change_north)
    u_velocity, u_uncertainty = fit_timeseries(time, change_up)
    return e_velocity, e_uncertainty, n_velocity, n_uncertainty, u_velocity, u_uncertainty

def get_coordinates(filename):
    dset = pd.read_csv(filename, sep='\s+')
    
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
    local_file_list = glob.glob(folder + '/' + pattern)

    for file in local_file_list:
        filename = os.path.basename(file)
        sitename = filename.split('.')[0]
        coordinates = get_coordinates(file)
        velocities = fit_velocities(file)
        dset = pd.read_csv(file, delim_whitespace=True) # Python path cannot find file on its own, but can when given full directory
                                                        # Therefore, we need to feed it FILE, the whole file path, instead of just the file name
        
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
    return df

def get_margin_from_bounds(bounds,margin=0.1): # Imported from geothomaslee/Mapping_Resources/scripts/general_mapping.py
    """
    Parameters
    ----------
    bounds : list of ints or floats
        Region to search for stations, in order [minlon, maxlon, minlat, maxlat]
    margin : int or float, optional
        Margin size, multiplied by the length of the bounds. 0.1 = 10% margin. 
        The default is 0.1.

    Returns
    -------
    marginal_bounds : list of ints or floats
        New bounds with added margin, same format as input bounds.

    """
    lons = [bounds[0],bounds[1]]
    lats = [bounds[2],bounds[3]]
            
    min_lon = min(lons) - (margin * abs(max(lons) - min(lons)))
    min_lat = min(lats) - (margin * abs(max(lats) - min(lats)))
    max_lon = max(lons) + (margin * abs(max(lons) - min(lons)))
    max_lat = max(lats) + (margin * abs(max(lats) - min(lats)))
    
    # These check if lats and lons are in bound, but shouldn't matter for this quick dataset for Lab 7 in EPS522_03
    #min_lon = check_lon(min_lon)
    #min_lat = check_lat(min_lat)
    #max_lon = check_lon(max_lon)
    #max_lat = check_lat(max_lat)
    
    marginal_bounds = [min_lon, max_lon, min_lat, max_lat]
    
    return marginal_bounds

def plot_velocities(df,margin=0.1,figure_name='Lab 5 GPS data!'):
    lats = df['avg_lat'].tolist()
    lons = df['avg_lon'].tolist()
    e_vel = df['e_velocity'].tolist()
    n_vel = df['n_velocity'].tolist()
    u_vel = df['u_velocity'].tolist()
    
    print(e_vel)
    print(n_vel)
    print(u_vel)
    
    angles = []
    magnitudes = []
    for i, east in enumerate(e_vel):
        north = n_vel[i]
        
        angle = np.arctan2(north, east) * (180 / np.pi)
        angles.append(angle)
        
        magnitude = (((north **2) + (east **2)) ** 0.5 ) * 600
        magnitudes.append(magnitude)
    
    region = [-110, -106, 34, 39]
    
    bounds = get_margin_from_bounds(region,margin=margin)
    
    grid = pygmt.datasets.load_earth_relief(resolution='15s', region=bounds)
    
    cmap = os.path.expanduser('~/Documents/GitHub/EPS522_03/colombia.cpt')
    
    projection="Q15c+du"
    
    fig = pygmt.Figure()
    fig.basemap(region=bounds,
                projection=projection,
                frame=True)
    fig.grdimage(grid=grid,
                 projection=projection,
                 frame=["a",f'+t{figure_name}'],
                 cmap=cmap)
    fig.coast(shorelines="4/0.5p,black",
              projection=projection,
              borders="a/1.2p,black",
              water="skyblue",
              resolution="f")
    fig.plot(x=lons,
             y=lats,
             style = "v0.4c+bc+ea+a30",
             pen='1p',
             direction=[angles,magnitudes])
    pygmt.makecpt(cmap="viridis",series=[min(u_vel),max(u_vel)])             
    fig.plot(x=lons,
             y=lats,
             style='c0.2c',
             pen='0.1p',
             cmap=True,
             fill=u_vel)
    fig.colorbar(frame="af+lUpward Velocity (m/yr)")
            
   
    
    fig.show()

    
    

    
    
    