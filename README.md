# CompMethods_Lab5
This readme overviews lab 5 for computational methods, fall 2023 at UNM. The timeseries_module file includes four functions
(fit_timeseries, fit_velocites, get_coordinates, and fit_all_velocities) which can be called and used to average velocities and coordinates, rates of change, uncertainties 
of linear regressions, etc. These variables are stored and returned in the functions, and can be reused. The fit_all_velocities function uses the fit_velocities and 
get_coordinates functions to estimate the velocities, coordinates and uncertainties for a list of files.

To use the module, you must download and save the module, and then import it using import timeseries_module. Then you can call the individual functions by their function 
names. Note that the fit_all_velocities function uses the fit_velocities and get_coordinates functions within it, which is something that could be improved upon as it
is rather inefficient.
