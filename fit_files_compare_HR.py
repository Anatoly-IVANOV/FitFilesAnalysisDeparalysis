"""
********************************************************************************
*
* Project      : FIT files analysis tools
*
* Filename     : fit_files_compare_HR.py
*
* File purpose : Used to show heart-rate curve plot(s) of 1 to 5 simultaneous
*                activities contained in 1 to 5 FIT files dropped into
*                the /fit_files_compare_HR/ directory
*
*                example: compare the accuracy of various smartwatches,
*                         or the HR of several runners :P
*
* History      : 2024-08-05 - ANATOLY IVANOV .COM - Genesis
*                2024-08-08 - ANATOLY IVANOV .COM - Expand to just 1 FIT file
*
* Requires     : matplotlib, FitFile
*
* Notes        : Export a FIT file from any tracking app like Strava,
*                WorkOutdoors... Place up to 5 FIT files into the folder:
*
*                 /fit_files_compare_HR/
*
*                Call the fit_files_compare_HR.py through the Python interpreter
*                (or first cd into the project folder if not using absolute
*                 paths):
*
*                > cd project_folder
*                > python fit_files_compare_HR.py
*
********************************************************************************
"""



"""
********************************************************************************
*
*   IMPORT MODULES -- GLOBAL
*
********************************************************************************
"""

# Basic OS manipulation module
import os

# matplotlib.pyplot is a state-based interface to matplotlib module that
# provides an implicit, MATLAB-like plotting. It opens figures on the screen,
# and acts as the figure GUI manager.
import matplotlib.pyplot as plot

# Provides date methods for the plots
import matplotlib.dates as mdates

# Import only the FitFile from the FIT file parser
from fitparse import FitFile

# Custom plot ticker for dynamic axes’ ticks (getting more precise as we zoom in)
from matplotlib.ticker import MaxNLocator




"""
********************************************************************************
*
*   PARAMS
*
********************************************************************************
"""

# Set default MATLAB-like plotting GUI `save` button format to 'pdf' or 'svg'
plot.rcParams['savefig.format'] = 'pdf'  # Use 'svg' for SVG format

# Set whether we want to save a PDF of the plot (in addition to showing it,
# saved into the folder from where the script is run; a home folder, for example)
bool_PlotSavePDF = True

# Set whether we want to save an SVG of the plot (in addition to showing it,
# saved into the folder from where the script is run; a home folder, for example)
bool_PlotSaveSVG = False

# Directory containing FIT files (relative to the script location)
str_ScriptDirectory = os.path.dirname(os.path.abspath(__file__))
str_FitFilesDirectory = os.path.join(str_ScriptDirectory, 'fit_files_compare_HR')

# Maximum number of files to compare (avoiding visual overload)
int_FitFilesMax = 5




"""
********************************************************************************
*
*   FUNCTIONS
*
********************************************************************************
"""


def fit_files_from_directory_load_and_read(str_Directory: str, int_FitFilesMax: int):
  '''

  Function to load FIT files from a directory, read-parse the binary data
  and return the files’ path on disk, plus FitFile plain-text class instances
  containing the exercise data

  @param str_Directory -- FIT file(s) path (absolute, self-assembled)
  @param int_FitFilesMax -- Max files to process (avoiding visual overload)
  @return arr_FitFilesPaths -- Paths to the FIT files
  @return arr_FitFileClassInsts -- Decoded, non-binary FitFile class instances
  '''

  # Init empty arrays for the FIT file paths and their contents
  # (FitFile class instances)
  arr_FitFilesPaths = []
  arr_FitFileClassInsts = []

  # Open the FIT files’ directory and get an array (list) of filenames
  for arr_FileNames in os.listdir(str_Directory):

    # If the file name being iterated has a .fit extension
    # and the length of the array is less than the max set in the params
    if arr_FileNames.endswith('.fit') and len(arr_FitFilesPaths) < int_FitFilesMax:

      # Add the file path to arr_FitFilesPaths
      arr_FitFilesPaths.append(arr_FileNames)

      # Open the FIT file, convert the binary exercise data into a plain-text
      # FitFile class instance (data + methods) (the only time when we use the
      # `fitparse` module), add them to the array for plotting later
      arr_FitFileClassInsts.append(FitFile(os.path.join(str_Directory, arr_FileNames)))

  # Return the tuple of
  # 1) the array of FIT files’ paths’
  # 2) the array of each corresponding FitFile class instances
  return arr_FitFilesPaths, arr_FitFileClassInsts




def fitfile_class_inst_heartrate_at_date_time_get(class_inst_FitFile: FitFile):
  '''

  Function to get the heart rate data from the FitFile class instance

  @param class_inst_FitFile -- FIT file’s exercise data + methods to work with it
  @return arr_TimeStamps -- Date-time when HR was sampled
  @return arr_HeartRate -- Heart rate at those date-time points
  '''

  # Init empty time stamps and HR arrays
  arr_TimeStamps = []
  arr_HeartRate = []

  # Iterate through the FIT file’s exercise data, calling the built-in
  # get_messages() method to locate `record` data blocks.
  #
  # Each Message object usually corresponds to a specific type of data
  # (a single heart rate reading...) Each Message object contains fields,
  # which are name-value pairs (`timestamp`, `heart_rate`...)
  for obj_Record in class_inst_FitFile.get_messages('record'):

    # Init the Date-Time object
    obj_TimeStamp = None

    # Init the HR integer
    int_HR = None


    # Iterate through each `record` object
    for obj_Data in obj_Record:

      # If the data point has a `timestamp` label
      if obj_Data.name == 'timestamp':

        # Collect the Date-Time
        obj_TimeStamp = obj_Data.value

      # Otherwise, if the data point has a `heart_rate` label
      # (other names are `record` and `device_info`)
      elif obj_Data.name == 'heart_rate':

        # Collect the HR
        int_HR = obj_Data.value

    # If both Date-Time and HR were collected, append them to the respective
    # arrays
    if obj_TimeStamp and int_HR:
      arr_TimeStamps.append(obj_TimeStamp)
      arr_HeartRate.append(int_HR)


  # Return the tuple of Date-Time and HR arrays
  return arr_TimeStamps, arr_HeartRate




"""
********************************************************************************
*
*   MAIN LOGIC
*
********************************************************************************
"""

# Load all FIT files from the directory
arr_FitFilesPaths, arr_FitFileClassInsts = fit_files_from_directory_load_and_read(str_FitFilesDirectory, int_FitFilesMax)

# Ensure we have at least one FIT file to plot
if len(arr_FitFileClassInsts) < 1:
  raise ValueError('The directory should contain at least 1 FIT file for plotting. Exiting...')

# Init an empty HR array
arr_HeartrateData = []

# Iterate through the array of FitFile data+methods’ class instances
for class_inst_FitFile in arr_FitFileClassInsts:

  # Get the Time-Date + HR arrays from each FitFile class instance
  arr_TimeStamps, arr_HeartRate = fitfile_class_inst_heartrate_at_date_time_get(class_inst_FitFile)
  arr_HeartrateData.append((arr_TimeStamps, arr_HeartRate))




"""
********************************************************************************
*
*   PLOTTING
*
********************************************************************************
"""

# Configure the proportions of the plot: 12x6 inches approx, to fit on A4
# (Matplotlib thinks in inches, points and DPI)
plot.figure(figsize=(11.69, 8.27))

# Plot the data
for int_EnumerateIndex, (arr_TimeStamps, arr_HeartRate) in enumerate(arr_HeartrateData):

  # For the label, use the file names without extension
  str_Label = os.path.splitext(arr_FitFilesPaths[int_EnumerateIndex])[0]

  # Plot the iteration, use the pre-assembled label (for each file)
  plot.plot(arr_TimeStamps, arr_HeartRate, label=str_Label)

# Add the axes’ labels with some padding to improve readability (measured in points)
plot.xlabel('Time', labelpad=15)
plot.ylabel('Heart Rate (bpm)', labelpad=15)

# Add the title (adjusting based on whether we're plotting just 1 file
# or comparing several)
plot.title('Heart Rate Comparison' if len(arr_FitFileClassInsts) > 1 else 'Heart Rate Plot')
plot.legend()

# Enable grid with both major and minor ticks,
# using a dashed line style for clarity and a thickness in points
plot.grid(True, which='both', linestyle='--', linewidth=0.5)

# Set up dynamic date formatting based on zoom level for the X-axis
# AutoDateLocator will automatically choose the best tick positions depending
# on the current zoom level
locator_x = mdates.AutoDateLocator()

# ConciseDateFormatter provides a concise representation of dates.
# To obtain an ISO date show at all zoom levels, we have to overload all 6 zoom
# levels. Otherwise, Matplotlib will display 2024-Aug-12 or something else
formatter_x = mdates.ConciseDateFormatter(
  locator_x,
  offset_formats=[
    '%Y',        # format for years
    '%Y-%m',     # format for months
    '%Y-%m-%d',  # format for days
    '%Y-%m-%d',  # format for hours
    '%Y-%m-%d',  # format for minutes
    '%Y-%m-%d'   # format for seconds/microseconds
  ]
)

# Apply the custom locator and formatter to the X-axis
plot.gca().xaxis.set_major_locator(locator_x)
plot.gca().xaxis.set_major_formatter(formatter_x)


# Custom Y-axis locator to dynamically adjust tick spacing as the plot is zoomed
# MaxNLocator is used to ensure a maximum of N ticks are used at any zoom level
class DynamicYLocator(MaxNLocator):

  # NB: Python uses * to omit specifying certain arguments
  def __init__(self, *args, **kwargs):

    # Calls the parent class's constructor with all the positional and keyword
    # arguments that were passed to the child class
    super().__init__(*args, **kwargs)


  def view_limits(self, flt_VisibleMin: float, flt_VisibleMax: float):

    # Retain the original view limits; no changes made here
    return (flt_VisibleMin, flt_VisibleMax)


  def tick_values(self, flt_VisibleMin: float, flt_VisibleMax: float):

    # Dynamically adjust tick values based on the current zoom level
    tick_values = super().tick_values(flt_VisibleMin, flt_VisibleMax)

    # If the range is small, ensure integer tick values are used for clarity
    if flt_VisibleMax - flt_VisibleMin < 10:
      self._integer = True
      self.set_params(integer=True)
      tick_values = super().tick_values(flt_VisibleMin, flt_VisibleMax)
    return tick_values


# Apply the custom dynamic Y-axis locator
plot.gca().yaxis.set_major_locator(DynamicYLocator())




# Save the plot as a vector graphic (PDF) if set to `true`` in params
if bool_PlotSavePDF:
  plot.savefig('heart_rate_comparison.pdf', format='pdf')

# Save the plot as a vector graphic (SVG) if set to `true`` in params
if bool_PlotSaveSVG:
  plot.savefig('heart_rate_comparison.svg', format='svg')




# Show the plot in a GUI : nice to zoom in, pan and save out a pdf or svg
# (set in the params above)
plot.show()
