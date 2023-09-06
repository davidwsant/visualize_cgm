## Welcome to visualize_cgm.py

This program has been designed to create graphs from CGM data. We have been using the Dexcom G6, but the file formats
from other devices could be changed to mirror this input type. The required columns are 'Timestamp' (which has
unfortunately been changed by Excel for the ones that we obtained), 'Event Type' (only values with 'EGV' are used),
and 'Glucose Value (mg/dL)'. Example usage: ./visualize_cgm.py -i 100_1_cgm.csv

optional arguments:

  -h, --help            show this help message and exit
  
  -i INPUT_FILE, --input_file INPUT_FILE
  
                        This is the csv that visualize_cgm.py will read to create the graphs.
						
  -o OUTPUT, --output OUTPUT
  
                        This is the name of the output folder and the prefix for the png files. If no output is
                        specified, the header for the input file will be used.