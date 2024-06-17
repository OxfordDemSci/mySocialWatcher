from src import params
from pathlib import Path
import pandas as pd
import datetime
import numpy as np
import os
import matplotlib.pyplot as plt


# at 24th March, check the data abuot Donetsk and Luhansk

def age_group_plot(df,country_name):
    age_ranges = [1600, 5059, 1860, 1800, 2029, 6000, 4049, 1649, 1619, 3039]
    i = 0
    fontsize_ticks = 20
    fontsize_labels = 21
    figure, axis = plt.subplots(5,2)
    figure.subplots_adjust(left=0.08, top=0.95, bottom=0.08,right=0.95)
    figure.set_figheight(30)
    figure.set_figwidth(12)

    for (m, n), subplot in np.ndenumerate(axis):
        age_range=age_ranges[i]
        temp = df.loc[(df['age_range']==age_range)]
        pivoted = pd.pivot_table(temp, values='audience', columns='gender', index='date')
        # Now there will be an index column for date and value columns for 0,1,2,3,4
        pivoted.plot(ax=axis[m, n])
        axis[m, n].set_title(age_range)
        i+=1
    figure.suptitle(country_name)
    plt.show()



def gender_compare_plot(df,country_name):
    fig, (ax1,ax2,ax3) = plt.subplots(1,3)
    fig.set_figheight(15)
    fig.set_figwidth(20)

    fig.suptitle(country_name)

    gender = 'female'
    temp = df.loc[(df['gender'] == gender)]
    pivoted = pd.pivot_table(temp, values='audience', columns='age_range', index='date')
    pivoted.plot(ax=ax1)
    ax1.set_title(gender)
    ax1.grid(axis='x', alpha=0.4, linestyle='dashed')


    gender = 'male'
    temp = df.loc[(df['gender'] == gender)]
    pivoted = pd.pivot_table(temp, values='audience', columns='age_range', index='date')
    pivoted.plot(ax=ax2)
    ax2.grid(axis='x', alpha=0.4, linestyle='dashed')
    ax2.set_title(gender)


    gender = 'all'
    temp = df.loc[(df['gender'] == gender)]
    pivoted = pd.pivot_table(temp, values='audience', columns='age_range', index='date')
    pivoted.plot(ax=ax3)
    ax3.grid(axis='x', alpha=0.4, linestyle='dashed')
    ax3.set_title(gender)

    plt.show()

# ----------------- ----------------- ----------------- ----------------- -----------------

files = os.listdir(params.data_path)
files.remove('.DS_Store')

columns = pd.read_csv(params.data_path/'230322.csv').columns
df = pd.DataFrame(columns=columns)
for file in files:
    temp = pd.read_csv(params.data_path/file)
    temp = temp.loc[(temp['city']=='Donetsk') | (temp['city']=='Luhansk')| (temp['city']=='Kyiv')|(temp['city']=='Mariupol')]
    df = pd.concat([df,temp],axis=0)

df['date'] = [int(x[8:10]) for x in df['time']]


Donetsk = df[df['city'] == 'Donetsk']
Luhansk = df[df['city'] == 'Luhansk']
Kyiv = df[df['city'] == 'Kyiv']
Mariupol = df[df['city'] == 'Mariupol']


age_group_plot(Donetsk, 'Donetsk')
gender_compare_plot(Donetsk, 'Donetsk')


'''
df = pd.read_csv(params.data_path/'100322.csv')

df = df[['country', 'city', 'age_min', 'age_max', 'age_range', 'gender', 'audience', 'time', 'country_level']]

country_level = df[(df['country_level']==1)&(df['age_range']==1800)&(df['gender']=='all')]

all_0s = df[df['audience']==0]  # 369 lines altogether

# 0s by country
all_0s.groupby('country').count()



Romania = df[df['country'] == 'Romania']
Romania_0s = Romania[Romania['audience'] == 0]
# Romania 0s by city, age_range and gender
Romania_0s.groupby('city').count()
Romania_0s.groupby('age_range').count()
Romania_0s.groupby('gender').count()


Slovakia = df[df['country'] == 'Slovakia']
Slovakia_0s = Slovakia[Slovakia['audience']==0]
Slovakia_0s.groupby('city').count()
Slovakia_0s.groupby('age_range').count()
Slovakia_0s.groupby('gender').count()



Hungry = df[df['country'] == 'Hungry']
Hungry_0s = Hungry[Hungry['audience']==0]
Hungry_0s.groupby('city').count()
Hungry_0s.groupby('age_range').count()
Hungry_0s.groupby('gender').count()

Poland = df[df['country'] == 'Poland']
Poland_0s = Poland[Poland['audience']==0]
Poland_0s.groupby('city').count()
Poland_0s.groupby('age_range').count()
Poland_0s.groupby('gender').count()


Moldova = df[df['country'] == 'Moldova']
Moldova_0s = Moldova[Moldova['audience']==0]
Moldova_0s.groupby('city').count()
Moldova_0s.groupby('age_range').count()
Moldova_0s.groupby('gender').count()
'''

# time = [datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f') for x in df['time']]
# type(df['time'][0])
# print('we spent {} hours to finish the process'.format((max(time)-min(time)).seconds/3600))







