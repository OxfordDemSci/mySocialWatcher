import re
import os
from pathlib import Path



f=open(os.path.join(Path.cwd().parent,"useful_files/test.txt"),"r")
curls = f.read()
f.close()

country_code = int(re.findall('country=(\d*)',curls)[0])
city = int(re.findall('cities=(\d*)&',curls)[0])
city_ex = int(re.findall('cities_not=(\d*)&',curls)[0])
city_name = input("the city name is :")
city_ex_name = input('The name of excluding city is :')
print("'country code' : {} \n'{}':{},'{}':{},".format(country_code,city_name,city,city_ex_name,city_ex))


