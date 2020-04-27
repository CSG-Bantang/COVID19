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
datafile = '../dat/smart/up_OD_table_202002.csv'
#date to be extracted
date = '2020-04-01' #check format of the original csv file.
#province to be investigated
province = 'NCR'

'''
Main scripting part
'''

#############################################
print('#Reading from data file: ', datafile, '...' )
s = pd.read_csv(datafile,header=0)
print( '..total number of records read: {:,d}'.format(len(s)) )


#############################################
def generate( date, province ):
    print('##############################################' )
    print('##############################################' )

    print('#Showing the first elements for the following.' )
    print('..date = ', date )
    print('..area = ', province )
    s01 = s.loc[ (s['Date']==date)&(s['O_P']==province) ]
    print('..done. Showing data head()..' )
    print(s01.head(3) )

    #############################################
    print('#Analyzing data from blanks (null)..' )
    s01['O_ID'].isnull().describe()
    print('..There are {:,} entries without O_ID.'.format(
        len( s01[s01['O_ID'].isnull()] ) ) )
    print('....and there are {:,} entries both without O_ID and D_ID.'.format(
        len( s01[ s01['O_ID'].isnull() & s01['D_ID'].isnull() ] ) ) )


    #############################################
    print('#Cleaning data, removing the null OID and DID..' )
    s01clean = s01[ s01['O_ID'].notnull() & s01['D_ID'].notnull() ]
    print('..We have {:,} rows with complete entries.'.format( len(s01clean) ))
    print('....The min (max) O_ID is %d (%d).'% ( min(s01clean['O_ID'].unique())
                                         , max(s01clean['O_ID'].unique()) ) )
    print('....The min (max) D_ID is %d (%d).'% ( min(s01clean['D_ID'].unique())
                                         , max(s01clean['D_ID'].unique()) ) )

    #############################################
    print('#Generating unique indices..' )
    oidChoices = s01clean['O_ID']
    didChoices = s01clean['D_ID']
    n_oid = len(oidChoices.unique())
    n_did = len(didChoices.unique())
    print('..There are %d unique oidChoices.'% n_oid )
    print('..There are %d unique didChoices.'% n_did )

    print('..Computing unique indices as intersection..' )
    xID = pd.Series( list( set(oidChoices.unique()).intersection( set(didChoices.unique()) ) ) )
    print('....We will use %d same entries as index pool.'% len(xID) )

    #############################################
    print('Testing for a random O_ID and D_ID pair..' )

    oid = np.random.choice(xID)
    did = np.random.choice(xID)
    print( '..Now we search for (O_ID,D_ID) = (%d,%d)..'% ( oid,did ) )

    cnt = 0
    for row in s01clean.itertuples():
        if (int(row.O_ID)==oid) and (int(row.D_ID)==did):
            print(int(row.O_ID), int(row.D_ID), row.Value)
            cnt+= 1

    print('..There is(are) ',cnt, ' entry(/ies)!')

    #############################################
    print('Generating sorted indices..' )
    xID = np.sort(xID)
    print('..sorting done.' )

    #############################################
    print('Generating a dictionary of all IDs..' )

    b_dict = {} #initially empty

    iID = xID.astype(int)
    cnt = 0
    for x in iID:
        b_dict[x]=cnt
        cnt+=1
    
    print('..done generating dictionary of length ', cnt,'.' )

    print('Testing the dictionary..' )
    for x in np.random.choice(iID,size=3):
        print('..This number ',x, ' is ', (x in b_dict) and ('in') or ('NOT in') , ' the Dictionary!' )
        print( '..', x, '->', b_dict[x] )
    
    print('..test Done.' )
    
    
    #############################################
    print('Preparing the matrix..' )

    m = len(iID)
    matrix_od = np.zeros( (m,m) ).astype(int)
    print(matrix_od)

    print('element (1,2)', matrix_od[1,2] )
    print('..now we have a ', matrix_od.shape, ' matrix!' )
    
    
    #############################################
    print('Populating the matrix..' )
    print('..looping over the sample file..' )
    cnt = 0
    for row in s01clean.itertuples():
        #print('....trying [', int(row.O_ID),',', int(row.D_ID),']','=', row.Value)

        if (row.O_ID in b_dict) and (row.D_ID in b_dict):
            matrix_od[ b_dict[row.D_ID], b_dict[row.O_ID] ] += row.Value
            cnt+= 1
    #    else:
    #        print('....one entry cannot be added: [', row.O_ID, row.D_ID, ']!' )

    print('..done with {:,}'.format(cnt), ' entries TOTAL!' )
    print('..here\'s the matrix contents:' )
    print(matrix_od )
    print('..root-scaled matrix (power = 1/16):' )
    print(np.power(matrix_od,0.0625) )
    
    

    #############################################
    print('Saving into different files..' )
    print('##')
    foutd = '../out/smart/'
    fbase = 's-od'
    fname = foutd+fbase+'-b2m-'+date+'.npy'
    print('..Saving barangay dictionary bID->mNdx: ',fname  )
    np.save(fname, np.array( list( b_dict.items() ) ) )
    print('....to readback:' )
    print('....bIDtomNdx = dict( list( np.load( FILENAME ) ) )' )    
    print('##')
    print('..Saving matrix_od into .npy file..' )
    fname = foutd+fbase+'-odm-'+date+'.npy'
    np.save(fname, matrix_od )
    print('..matrix_od saved to file: ',fname, '..' )
    print('##')
    print('..Generating the image..' )
    fname = foutd+fbase+'-img-'+date+'.png'
    print('....image will be saved at : ', foutd,'.' )
    fig=plt.figure()
    plt.axis('off')
    p=plt.imshow( np.power(matrix_od,0.0625),interpolation='none',vmin=0,vmax=2,cmap='gnuplot2' )
    #plt.colorbar(p)
    plt.imsave(fname, np.power(matrix_od,0.0625),vmin=0,vmax=2,cmap='gnuplot2' )
    print('..Done. Image output: ', fname)
    print('..Clearing figure objects..' )
    plt.close('all') #closing all figures
    print('..done.')
    print('DONE.')
    
    
   
###########possible script for running#######
#for dd in np.arange(1,32):
#    dt = '2020-03-%02d'%dd
#    generate( province='NCR', date=dt )





