import os
import json
from mysocialwatcher.collector.specs import master_specs
from pysocialwatcher import watcherAPI


if __name__ == '__main__':

    # root directory
    output_dir = os.path.join('config', 'specs', 'templates')

    # initialize
    watcher = watcherAPI(api_version='15.0')
    watcher.load_credentials_file(os.path.join('docker', 'collectors', 'jubal', 'baseline', 'credentials.csv'))

    # all countries
    countries = ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AR', 'AS', 'AT', 'AU', 'AW', 'AZ', 'BA', 'BB', 'BD',
                 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ',
                 'CA', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CW', 'CY', 'CZ', 'DE',
                 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR',
                 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GT', 'GU', 'GW',
                 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IQ', 'IS', 'IT', 'JE', 'JM', 'JO',
                 'KG', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME',
                 'MF', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX',
                 'MY', 'MZ', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG',
                 'PH', 'PK', 'PL', 'PM', 'PR', 'PS', 'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB',
                 'SC', 'SD', 'SE', 'SG', 'SH', 'SI', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SY', 'SZ', 'TC',
                 'TD', 'TG', 'TH', 'TJ', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY',
                 'UZ', 'VC', 'VE', 'VG', 'VI', 'VN', 'VU', 'WF', 'WS', 'XK', 'YE', 'YT', 'ZA', 'ZM', 'ZW']

    countries_city = ['BY', 'GB', 'HU', 'MD', 'PL', 'RO', 'RU', 'SK', 'UA']

    # ---- region specs ---- #
    for country in countries:
        # country = countries[0]

        print('Processing ' + country + ' regions...')

        json_filename = os.path.join(output_dir, country + '_regions.json')
        region_filename = os.path.join(output_dir, country + '_regions.csv')

        json_exists = os.path.exists(json_filename)
        region_exists = os.path.exists(region_filename)

        if not json_exists or not region_exists:

            try:
                # initialize specs
                result = master_specs(country=country,
                                      regions=True,
                                      cities=False)

                # write json to file
                if not json_exists:
                    with open(json_filename, "w") as f:
                        f.write(json.dumps(result.get('specs')))

                # write regions to csv
                if not region_exists:
                    result.get('regions').to_csv(region_filename)

            except Exception as e:
                print(e)


    # ---- city specs ----#
    for country in countries_city:
        # country = countries_city[0]

        print('Processing ' + country + ' cities...')

        json_filename = os.path.join(output_dir, country + '_cities.json')
        city_filename = os.path.join(output_dir, country + '_cities.csv')

        json_exists = os.path.exists(json_filename)
        city_exists = os.path.exists(city_filename)

        if not json_exists or not city_exists:

            try:

                # initialize specs
                result = master_specs(country=country,
                                      regions=False,
                                      cities=True)

                # write json to file
                if not json_exists:
                    with open(json_filename, "w") as f:
                        f.write(json.dumps(result.get('specs')))

                # write cities to csv
                if not city_exists:
                    result.get('cities').to_csv(city_filename)

            except Exception as e:
                print(e)

