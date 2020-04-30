#!/usr/bin/python
"""
This extracts the OD matrix from the OD listing provided
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

__author__ = "Johnrob Y Bantang, Reinier Xander Ramos, Cephas Olivier V Cabatit"
__copyright__ = "College of Science, University of the Philippines"
__credits__ = ["Giovanni Tapang"]
__license__ = "CC BY-SA"
__version__ = "3.0"
#__maintainer__ = "Who"
__email__ = "jybantang@up.edu.ph"
__status__ = "Production"

#datafile
datafile = '../dat/smart/up_OD_table_202004.csv'
#date to be extracted
date = '2020-04-01' #check format of the original csv file.
#province to be investigated
province = 'NCR'

'''
Main scripting part
'''
print('#Reading from data file: ', datafile, '...' )
s = pd.read_csv(datafile,header=0)
print( '..total number of records read: {:,d}'.format(len(s)) )

print('#Showing the first elements for the following.' )
print('..date = ', date )
print('..area = ', province )
s01 = s.loc[ (s['Date']==date)&(s['O_P']==province) ]
print('..done. Showing data head()..' )
s01.head(3)

print('#Analyzing data from blanks (null)..' )
s01['O_ID'].isnull().describe()
print('..There are {:,} entries without O_ID.'.format(
    len( s01[s01['O_ID'].isnull()] ) ) )
print('....and there are {:,} entries both without O_ID and D_ID.'.format(
    len( s01[ s01['O_ID'].isnull() & s01['D_ID'].isnull() ] ) ) )


s01clean = s01[ s01['O_ID'].notnull() & s01['D_ID'].notnull() ]
print('..We have {:,} rows with complete entries.'.format( len(s01clean) ))
print('....The min (max) O_ID is %d (%d).'% ( min(s01clean['O_ID'].unique())
                                         , max(s01clean['O_ID'].unique()) ) )
print('....The min (max) D_ID is %d (%d).'% ( min(s01clean['D_ID'].unique())
                                         , max(s01clean['D_ID'].unique()) ) )

