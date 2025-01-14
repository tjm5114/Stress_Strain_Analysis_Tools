import pandas as pd
import re
import matplotlib.pyplot as pyplt
import os
import numpy as np


Tensile = 'File Name \t dose \t UTS (MPa) \t Stress at Failure (MPa) \t Strain at Failure (mm/mm) \n'
'''get file locations of the raw .dat file'''
for i in range(0, 3):
    thickness = ['0.2540_', '1.27_', '3.3302_']
    file_front = 'data/' + str(thickness[i])
    # print(file_front)
    for j in range(0, 7):
        dose = ['0mgy', '0.1mgy', '0.2mgy', '0.3mgy', '0.5mgy', '0.6mgy', '1.0mgy']
        file_middle = file_front + str(dose[j]) + '_r('
        # print(file_middle)
        for replicates in range(1, 13):
            file = file_middle + str(replicates) + ').dat'
            #print(file)
            split_filename = file.split('_')
            dose = split_filename[1]
            layer = split_filename[0]
            split_layer = layer.split('/')
            layer_thickness = split_layer[1]
            #print(layer)
            #print(layer_thickness)
            #print(dose)

            # print('The '+str(specimen_type)+' cross-sectional area is', area, ' mm2')
            # print('The '+str(specimen_type)+' gage length is', g_len, ' mm')
            '''get file name to write output file'''
            file_name = os.path.splitext(file)[0]
            file_name = os.path.basename(file_name)
            # print(file_name)

            '''open file as a giant text blob'''
            if os.path.isfile(file):
                # ...
                with open(file, 'r+') as text:
                    pass
                    '''seperate blob into lines of text'''
                    lines = text.readlines()

                    '''create list object to put in only numerical data'''
                    clean_data = []

                    '''go line by line to scrub header data'''
                    for line in lines:

                        '''convert all \t to an actual tab in the data'''
                        line = line.replace('\t', ',')
                        #print(line)

                        '''strip out the \n at the end of each line'''
                        line = line.rstrip()

                        # check to see if there are any letters in the string. If there are not it must be a
                        # data line
                        if re.search('[a-zA-Z]', line) == None:

                            #if there is actually values in the line then we add it to our cleaned data list
                            # object
                            if len(line) > 4:

                                '''split the line into multiple elements using the comma as the anchor point'''
                                line = line.split(',')

                                '''add this line to the list object for ingest into Pandas'''
                                clean_data.append(line)

                    col_name = ['Displacement', 'Force', 'Time']

                    '''create pandas dataframe with the cleaned data'''
                    data = pd.DataFrame(clean_data, columns=col_name)
                    # print(data.head())

                    '''change the data from being a string to a float datatype'''
                    data = data.astype(float)
                    data['NormalForce'] = data['Force'] - data.iloc[0]['Force']

                    '''gauge length'''
                    g_len = 25  # mm
                    # select the correct cross sectional area for specimen based on thickness
                    if layer_thickness in ['3.3302']:
                        area = 6 * 3.3302  # cm^2

                    elif layer_thickness in ['1.27']:
                        area = 6 * 1.27  # cm^2
                        '''gauge length'''

                    elif layer_thickness in ['0.2540']:
                        area = 6 * 0.2540  # cm^2

                    else:
                        area = 6 * 3.3  # cm^2

                    '''Trying a guassian window for data smoothing'''
                    gaussian_func = lambda x, sigma: 1 / np.sqrt(2 * np.pi * sigma ** 2) * np.exp(
                        -(x ** 2) / (2 * sigma ** 2))
                    fig, ax = pyplt.subplots()
                    # Compute moving averages using different window sizes
                    sigma_lst = [1, 2, 3, 5, 8, 10]
                    y_gau = np.zeros((len(sigma_lst), len(data['Displacement'])))
                    for j, sigma in enumerate(sigma_lst):
                        gau_x = np.linspace(-2.7 * sigma, 2.7 * sigma, 6 * sigma)
                        gau_mask = gaussian_func(gau_x, sigma)
                        y_gau[j, :] = np.convolve(data['NormalForce'], gau_mask, 'same')
                        ax.plot(data['Displacement'], y_gau[j, :] + (j + 1) * 50,
                                label=r"$\sigma = {}$, $points = {}$".format(sigma, len(gau_x)))
                    # Add legend to plot
                    ax.legend(loc='upper left')
                    # pyplt.show()
                    #pyplt.savefig('data/processed_data_files/tensile/' + file_name + '_gau.png')
                    pyplt.close()
                    '''add a new column for the smoothed data y_avg from the window 35'''
                    data.insert(3, 'Smoothed_Force', y_gau[5])
                    print(data.head())


                    '''Stress calculation'''

                    data['Stress'] = data['Smoothed_Force'] / area

                    '''Normalize the Displacement'''
                    data['NormalDisplacement'] = data['Displacement']-data.iloc[0]['Displacement']

                    '''Strain Calculation'''
                    data['Strain'] = data['NormalDisplacement'] / g_len
                    # print(data['Strain'])
                    # print(data['Stress'])

                    '''calculating UTS, stress at break, strain at break, and strain at UTS'''
                    '''Calculate UTS'''
                    max_stress = round(data['Stress'].max(), 2)
                    #print('The UTS for ', '"', file_name, '" is ', max_stress,' MPa.')
                    '''delete all the negative values in the data for strain and stress'''
                    data['Stress_nonneg'] = data['Stress'][data['Stress'] >= 0]
                    data['Strain_nonneg'] = data['Strain'][data['Strain'] >= 0]
                    '''Drop all the NaN values'''
                    data = data.dropna(axis='rows', how='any')
                    #print(data['Stress_nonneg'])
                    '''Find the Strain at break'''
                    strain_break = round(data['Strain_nonneg'].max(), 4)
                    stress_break = round(data['Stress_nonneg'].iloc[-2], 2)

                    # print('The strain at break for "', file_name, '" is ', strain_break, ' mm/mm.')
                    '''Take the difference with each row in Stress_nonneg'''
                    # print('The stress at break for "', file_name, '" is ', stress_break, ' MPa.')
                    Tensile = Tensile + str(file_name) + '\t' + str(dose) + '\t' + str(max_stress) + '\t' + \
                        str(stress_break) + '\t' + str(strain_break) + '\n'
                    #data.to_excel('data/processed_data_files/fatigue/' + file_name + '.xlsx')
            True

print(Tensile)
#tensile_data = open('data/1.27_0MGy_meanuts_output.txt', 'r+')
#tensile_data.writelines(Tensile)
