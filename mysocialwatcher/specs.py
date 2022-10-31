import os
import pandas as pd
from pysocialwatcher import watcherAPI
from pysocialwatcher.json_builder import JSONBuilder, AgeList, Age, Genders, LocationList, Location


def master_specs(country, regions=True, cities=False):
    """
    Master JSON for national, sub-national, and city-level demographic collections.

    args:
        country (str): IS02 country code
        regions (boolean): Toggle region collection
        cities (boolean): Toggle city collections
    returns:
        dict: specification for collections
    """

    # sex
    genderlist = Genders(True, True, True)

    # age
    ages = [[13, None], [18, None], [20, None], [60, None], [65, None],
            [13, 19], [15, 49], [15, 64], [20, 59], [18, 60],
            [20, 29], [30, 39], [40, 49], [50, 59],
            [15, 19], [20, 24], [25, 29], [30, 34], [35, 39], [40, 44], [45, 49], [50, 54], [55, 59], [60, 64]]

    agelist = AgeList()
    for i in range(len(ages)):
        agelist.add(Age(ages[i][0], ages[i][1]))

    # locations
    loclist = LocationList()

    loclist.add(Location(loc_type='countries',
                         values=[country]))

    all_regions = None
    if regions:
        all_regions = watcherAPI.get_KMLs_for_regions_in_country(country)
        if isinstance(all_regions, pd.DataFrame):
            loclist.get_location_list_from_df(all_regions)

    all_cities = None
    if cities:
        all_cities = watcherAPI.get_all_cities_given_country_code(country)
        if isinstance(all_cities, pd.DataFrame):
            loclist.get_location_list_from_df(all_cities)

    # build json
    specs = JSONBuilder(name=country,
                        age_list=agelist,
                        location_list=loclist,
                        genders=genderlist).jsonfy()

    # platform
    specs["publisher_platforms"] = ["facebook"]

    # location types
    for i in range(len(specs['geo_locations'])):
        specs['geo_locations'][i]['location_types'] = ['recent']

    # return result
    return {'specs': specs, 'regions': all_regions, 'cities': all_cities}


def multicountry_specs(name='multicountry', countries=None, ages=None, genders=[0, 1, 2]):

    if countries is None:

        countries = ['US', 'CA', 'GB', 'AR', 'AU', 'AT', 'BE', 'BR', 'CL', 'CN', 'CO', 'HR', 'DK', 'DO', 'EG', 'FI',
                     'FR', 'DE', 'GR', 'HK', 'IN', 'ID', 'IE', 'IL', 'IT', 'JP', 'JO', 'KW', 'LB', 'MY', 'MX', 'NL',
                     'NZ', 'NG', 'NO', 'PK', 'PA', 'PE', 'PH', 'PL', 'RU', 'SA', 'RS', 'SG', 'ZA', 'KR', 'ES', 'SE',
                     'CH', 'TW', 'TH', 'TR', 'AE', 'VE', 'PT', 'LU', 'BG', 'CZ', 'SI', 'IS', 'SK', 'LT', 'TT', 'BD',
                     'LK', 'KE', 'HU', 'MA', 'CY', 'JM', 'EC', 'RO', 'BO', 'GT', 'CR', 'QA', 'SV', 'HN', 'NI', 'PY',
                     'UY', 'PR', 'BA', 'PS', 'TN', 'BH', 'VN', 'GH', 'MU', 'UA', 'MT', 'BS', 'MV', 'OM', 'MK', 'LV',
                     'EE', 'IQ', 'DZ', 'AL', 'NP', 'MO', 'ME', 'SN', 'GE', 'BN', 'UG', 'GP', 'BB', 'AZ', 'TZ', 'LY',
                     'MQ', 'CM', 'BW', 'ET', 'KZ', 'MG', 'NC', 'MD', 'FJ', 'BY', 'JE', 'GU', 'YE', 'ZM', 'IM', 'HT',
                     'KH', 'AW', 'PF', 'AF', 'BM', 'GY', 'AM', 'MW', 'AG', 'RW', 'GG', 'GM', 'FO', 'LC', 'KY', 'BJ',
                     'AD', 'GD', 'VI', 'BZ', 'VC', 'MN', 'MZ', 'ML', 'AO', 'GF', 'UZ', 'DJ', 'BF', 'MC', 'TG', 'GL',
                     'GA', 'GI', 'CD', 'KG', 'PG', 'BT', 'KN', 'SZ', 'LS', 'LA', 'LI', 'MP', 'SR', 'SC', 'VG', 'TC',
                     'DM', 'MR', 'SM', 'SL', 'NE', 'CG', 'AI', 'YT', 'CV', 'GN', 'TM', 'BI', 'TJ', 'VU', 'SB', 'ER',
                     'WS', 'AS', 'FK', 'GQ', 'TO', 'KM', 'PW', 'FM', 'CF', 'SO', 'MH', 'TD', 'KI', 'ST', 'TV', 'NR',
                     'RE', 'LR', 'ZW', 'CI', 'MM', 'BQ', 'CK', 'CW', 'GW', 'XK', 'MS', 'NF', 'BL', 'SH', 'MF', 'PM',
                     'SX', 'SS', 'TL', 'WF']

    # age
    if ages is None:
        ages = [[13, None], [18, None], [20, None], [60, None], [65, None],
                [13, 19], [15, 49], [15, 64], [20, 59], [18, 60],
                [20, 29], [30, 39], [40, 49], [50, 59],
                [15, 19], [20, 24], [25, 29], [30, 34], [35, 39], [40, 44], [45, 49], [50, 54], [55, 59], [60, 64]]

    agelist = AgeList()
    for i in range(len(ages)):
        agelist.add(Age(ages[i][0], ages[i][1]))

    # genders
    genderlist = Genders(1 in genders,
                         2 in genders,
                         0 in genders)

    # locations
    loclist = LocationList()

    for country in countries:
        loclist.add(Location(loc_type='countries', values=[country]))

    # build json
    specs = JSONBuilder(name=name,
                        age_list=agelist,
                        location_list=loclist,
                        genders=genderlist).jsonfy()

    # return json
    return specs


def dgg_specs():
    """JSON for national all countries collections for all digital gender gaps.

    args:
        filename (string): Filename to save json containing collection specifications.
    returns:
        dict: collection specification for collections"""

    # countries
    countries = ['US', 'CA', 'GB', 'AR', 'AU', 'AT', 'BE', 'BR', 'CL', 'CN', 'CO', 'HR', 'DK', 'DO', 'EG', 'FI', 'FR',
                 'DE', 'GR', 'HK', 'IN', 'ID', 'IE', 'IL', 'IT', 'JP', 'JO', 'KW', 'LB', 'MY', 'MX', 'NL', 'NZ', 'NG',
                 'NO', 'PK', 'PA', 'PE', 'PH', 'PL', 'RU', 'SA', 'RS', 'SG', 'ZA', 'KR', 'ES', 'SE', 'CH', 'TW', 'TH',
                 'TR', 'AE', 'VE', 'PT', 'LU', 'BG', 'CZ', 'SI', 'IS', 'SK', 'LT', 'TT', 'BD', 'LK', 'KE', 'HU', 'MA',
                 'CY', 'JM', 'EC', 'RO', 'BO', 'GT', 'CR', 'QA', 'SV', 'HN', 'NI', 'PY', 'UY', 'PR', 'BA', 'PS', 'TN',
                 'BH', 'VN', 'GH', 'MU', 'UA', 'MT', 'BS', 'MV', 'OM', 'MK', 'LV', 'EE', 'IQ', 'DZ', 'AL', 'NP', 'MO',
                 'ME', 'SN', 'GE', 'BN', 'UG', 'GP', 'BB', 'AZ', 'TZ', 'LY', 'MQ', 'CM', 'BW', 'ET', 'KZ', 'MG', 'NC',
                 'MD', 'FJ', 'BY', 'JE', 'GU', 'YE', 'ZM', 'IM', 'HT', 'KH', 'AW', 'PF', 'AF', 'BM', 'GY', 'AM', 'MW',
                 'AG', 'RW', 'GG', 'GM', 'FO', 'LC', 'KY', 'BJ', 'AD', 'GD', 'VI', 'BZ', 'VC', 'MN', 'MZ', 'ML', 'AO',
                 'GF', 'UZ', 'DJ', 'BF', 'MC', 'TG', 'GL', 'GA', 'GI', 'CD', 'KG', 'PG', 'BT', 'KN', 'SZ', 'LS', 'LA',
                 'LI', 'MP', 'SR', 'SC', 'VG', 'TC', 'DM', 'MR', 'SM', 'SL', 'NE', 'CG', 'AI', 'YT', 'CV', 'GN', 'TM',
                 'BI', 'TJ', 'VU', 'SB', 'ER', 'WS', 'AS', 'FK', 'GQ', 'TO', 'KM', 'PW', 'FM', 'CF', 'SO', 'MH', 'TD',
                 'KI', 'ST', 'TV', 'NR', 'RE', 'LR', 'ZW', 'CI', 'MM', 'BQ', 'CK', 'CW', 'GW', 'XK', 'MS', 'NF', 'BL',
                 'SH', 'MF', 'PM', 'SX', 'SS', 'TL', 'WF']

    # genders
    genderlist = Genders(True, True, True)

    # ages
    ages = [[18, None], [20, None], [21, None], [25, None], [50, None], [60, None], [65, None],
            [13, 14], [14, 15], [15, 16], [16, 17], [17, 18], [18, 19],
            [15, 19], [20, 24], [25, 29], [30, 34], [35, 39], [40, 44], [45, 49], [50, 54], [55, 59], [60, 64],
            [18, 23], [20, 64], [25, 49], [25, 64]]

    agelist = AgeList()
    for i in range(len(ages)):
        agelist.add(Age(ages[i][0], ages[i][1]))

    # locations
    loclist = LocationList()

    for country in countries:
        loclist.add(Location(loc_type='countries', values=[country]))

    # build json
    specs = JSONBuilder(name='dgg_national',
                        age_list=agelist,
                        location_list=loclist,
                        genders=genderlist).jsonfy()

    # return json
    return specs
