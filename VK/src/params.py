from pathlib import Path

country_dict = {'Ukraine': 2, 'Poland': 160, 'Russia': 1, 'Belarus': 3, 'Romania': 165, 'Slovakia': 184, 'Hungry': 50,
                'Moldova': 15}

city_dict = {'Ukraine': {'Kyiv': 314,
                         'Dnipro': 650,
                         'Donetsk': 223,
                         'Zaporizhia': 628,
                         'Kryvyi Rih': 916,
                         'Lviv': 1057,
                         'Luhansk': 552,
                         'Mariupol': 455,
                         'Mykolaiv': 377,
                         'Odessa': 292,
                         'Sevastopol': 185,
                         'Simferopol': 627,
                         'Kharkiv': 280,
                         'Vinnytsia': 761,
                         'Chernihiv': 444},
             'Hungry':  # only 23000 audience at country level
                 {'Miskolc': 1067,
                  'Kecskemét': 9733,
                  'Szolnok': 14745,
                  'Pécs': 20022,
                  'Debrecen': 21233,
                  'Szeged': 1704962,
                  'Gyor': 1707464,
                  'Szombathely': 1708002,
                  'Budapest': 1905655,
                  'Székesfehérvár': 1976180,
                  'Nyíregyháza': 2209344},
             'Slovakia':  # only 25000
                 {'Banská Bystrica': 6267,
                  'Bratislava': 1908070,
                  'Kosice': 1707309,
                  'Martin': 5944,
                  'Nitra': 20044,
                  'Presov': 19307,
                  'Trencin': 10501,
                  'Trnava': 16422,
                  'Zilina': 21008},
             'Romania':  # 39000
                 {'Braila': 1713324,
                  'Brasov': 1706305,
                  'Bucharest': 1913559,
                  'Cluj-Napoca': 13479,
                  'Constanta': 1707831,
                  'Craiova': 5404,
                  'Galati': 2002069,
                  'Iasi': 1970052,
                  'Oradea': 3232612,
                  'Ploiesti': 1516406,
                  'Timisoara': 14945},
             'Poland':  # 209000
                 {'Białystok': 1936080,
                  'Bydgoszcz': 8505,
                  'Gdansk': 21280,
                  'Gdynia': 1517185,
                  'Katowice': 1929447,
                  'Kraków': 2202278,
                  'Łódź': 6823,
                  'Lublin': 6949,
                  'Poznan': 20436,
                  'Szczecin': 1962158,
                  'Warsaw': 1922897,
                  'Wroclaw': 1515655},
             'Russia':  # 3 816 000
                 {'Moscow': 1,
                  'Saint Petersburg': 2,
                  'Volgograd': 10,
                  'Vladivostok': 37,
                  'Voronezh': 42,
                  'Yekaterinburg': 49,
                  'Kazan': 60,
                  'Kaliningrad': 61,
                  'Krasnodar': 72,
                  'Krasnoyarsk': 73,
                  'Nizhny Novgorod': 95,
                  'Novosibirsk': 99,
                  'Rostov-on-Don': 119,
                  'Samara': 123,
                  'Ufa': 151,
                  'Khabarovsk': 153,
                  'Omsk': 104,
                  'Perm': 110,
                  'Chelyabinsk': 158,
                  'Sevastopol': 185,
                  'Simferopol': 627},
             'Belarus':  # 3 818 000
                 {'Vitebsk': 244,
                  'Brest': 281,
                  'Minsk': 282,
                  'Mazyr': 375,
                  'Gomel': 392,
                  'Mahilyow': 467,
                  'Baranovichi': 538,
                  'Pinsk': 610,
                  'Grodno': 649,
                  'Bobruisk': 1107,
                  'Novopolatsk': 1299,
                  'Horki': 2179},
             'Moldova':  # 432000
                 {'Tiraspol': 374,
                  'Orhei': 741,
                  'Balti': 953,
                  'Bender': 1223,
                  'Dubasari': 3902,
                  'Comrat': 3985,
                  'Cahul': 8384,
                  'Chisinau': 1710959,
                  'Soroca': 1801266}}

gender_dict = {'male': 2, 'female': 1, 'all': 0}


# city keys in facebook, city name is from vk
# city_region_key = {'Kyiv': 4290, 'Dnipro': 3781, 'Donetsk': 3782, 'Zaporizhia': 3803, 'Kryvyi Rih': 3781, 'Lviv': 3792, 'Luhansk': 3791, 'Mariupol': 3782, 'Mykolaiv': 3793, 'Odessa': 3794, 'Sevastopol': 3124, 'Simferopol': None, 'Kharkiv': 3784, 'Vinnytsia': 3800, 'Chernihiv': 3779, 'Miskolc': 1624, 'Kecskemét': None, 'Szolnok': 1640, 'Pécs': None, 'Debrecen': 1630, 'Szeged': 1626, 'Gyor': 1629, 'Szombathely': 1642, 'Budapest': 1625, 'Székesfehérvár': None, 'Nyíregyháza': None, 'Banská Bystrica': None, 'Bratislava': 3422, 'Kosice': 3423, 'Martin': 3428, 'Nitra': 3424, 'Presov': 3425, 'Trencin': 3426, 'Trnava': 3427, 'Zilina': 3428, 'Braila': 3065, 'Brasov': 3066, 'Bucharest': 3067, 'Cluj-Napoca': 3070, 'Constanta': 3071, 'Craiova': 3074, 'Galati': 3075, 'Iasi': 3080, 'Oradea': 3062, 'Ploiesti': 3086, 'Timisoara': 3092, 'Białystok': 3002, 'Bydgoszcz': 2994, 'Gdansk': 3003, 'Gdynia': 3003, 'Katowice': 3004, 'Kraków': 2998, 'Łódź': 2995, 'Lublin': 2996, 'Poznan': 3007, 'Szczecin': 3008, 'Warsaw': 4135, 'Wroclaw': 2993, 'Moscow': 3138, 'Saint Petersburg': 3165, 'Volgograd': 3183, 'Vladivostok': 3158, 'Voronezh': 3185, 'Yekaterinburg': 3170, 'Kazan': 3172, 'Kaliningrad': 3122, 'Krasnodar': 3137, 'Krasnoyarsk': 3138, 'Nizhny Novgorod': 3150, 'Novosibirsk': 3152, 'Rostov-on-Don': 3160, 'Samara': 3116, 'Ufa': 3107, 'Khabarovsk': 3129, 'Omsk': 3153, 'Perm': 4165, 'Chelyabinsk': 3112, 'Vitebsk': 520, 'Brest': 514, 'Minsk': 517, 'Mazyr': 515, 'Gomel': 515, 'Mahilyow': None, 'Baranovichi': 514, 'Pinsk': 514, 'Grodno': 516, 'Bobruisk': None, 'Novopolatsk': None, 'Horki': 519, 'Tiraspol': 2245, 'Orhei': 2249, 'Balti': 2242, 'Bender': 4695, 'Dubasari': 2245, 'Comrat': 2247, 'Cahul': 2243, 'Chisinau': 2244, 'Soroca': 2250}
# regon name and region_id
region_dict = {517: 'Minsk', 1625: 'Budapest', 1630: 'Hajdú-Bihar County', 2245: 'Transnistria', 2998: 'Lesser Poland Voivodeship', 2993: 'Lower Silesian Voivodeship', 4135: 'Masovian Voivodeship', 3067: 'Bucharest', 3070: 'Cluj County', 3138: 'Krasnoyarsk Krai', 3116: 'Dagestan', 3132: 'Kirov Oblast', 3137: 'Krasnodar Krai', 3146: 'Moscow', 3150: 'Nizhny Novgorod Oblast', 4165: 'Perm Krai', 3160: 'Rostov Oblast', 3165: 'Saint Petersburg', 3164: 'Samara Oblast', 3166: 'Saratov Oblast', 3172: 'Tatarstan', 3183: 'Volgograd Oblast', 3185: 'Voronezh Oblast', 3422: 'Bratislava Region', 3423: 'Košice Region', 3779: 'Chernihiv Oblast', 3781: 'Dnipropetrovsk Oblast', 3782: 'Donetsk Oblast', 3784: 'Kharkiv Oblast', 3790: 'Kiev Oblast', 4290: 'Kyiv', 3791: 'Luhansk Oblast', 3792: 'Lviv Oblast', 3793: 'Mykolaiv Oblast', 3794: 'Odessa Oblast', 3798: 'Sumy Oblast', 3800: 'Vinnytsia Oblast', 3802: 'Zakarpattia Oblast', 3803: 'Zaporizhia Oblast', 514: 'Brest Region', 515: 'Gomel Region', 516: 'Grodno Region', 4455: 'Minsk Region', 519: 'Mogilev Region', 520: 'Vitebsk Region', 1621: 'Bács-Kiskun County', 1622: 'Baranya County', 1623: 'Békés County', 1624: 'Borsod-Abaúj-Zemplén County', 1626: 'Csongrád County', 1628: 'Fejér County', 1629: 'Győr-Moson-Sopron County', 1631: 'Heves County', 1640: 'Jász-Nagykun-Szolnok County', 1632: 'Komárom-Esztergom County', 1634: 'Nógrád County', 1636: 'Pest County', 1637: 'Somogy County', 1638: 'Szabolcs-Szatmár-Bereg County', 1641: 'Tolna County', 1642: 'Vas County', 1643: 'Veszprém County', 1644: 'Zala County', 4612: 'Anenii Noi District', 2242: 'Bălți', 4611: 'Basarabeasca District', 4695: 'Bender', 4613: 'Briceni District', 2243: 'Cahul District', 4614: 'Călărași District', 4616: 'Cantemir District', 4615: 'Căușeni District', 2244: 'Chișinău', 4617: 'Cimișlia District', 4618: 'Criuleni District', 4648: 'Dondușeni District', 4620: 'Drochia District', 4619: 'Dubăsari District', 2246: 'Edineț District', 4622: 'Fălești District', 4624: 'Florești District', 2247: 'Gagauzia', 4621: 'Glodeni District', 4623: 'Hîncești District', 4626: 'Ialoveni District', 4625: 'Leova District', 4627: 'Nisporeni District', 4628: 'Ocnița District', 2249: 'Orhei District', 4629: 'Rezina District', 4630: 'Rîșcani District', 4631: 'Sîngerei District', 4632: 'Șoldănești District', 2250: 'Soroca District', 4634: 'Ștefan Vodă District', 4633: 'Strășeni District', 4636: 'Taraclia District', 4635: 'Telenești District', 2252: 'Ungheni District', 3007: 'Greater Poland Voivodeship', 2994: 'Kuyavian-Pomeranian Voivodeship', 2995: 'Łódź Voivodeship', 2996: 'Lublin Voivodeship', 2997: 'Lubusz Voivodeship', 3000: 'Opole Voivodeship', 3001: 'Podkarpackie Voivodeship', 3002: 'Podlaskie Voivodeship', 3003: 'Pomeranian Voivodeship', 3004: 'Silesian Voivodeship', 3005: 'Świętokrzyskie Voivodeship', 3006: 'Warmian-Masurian Voivodeship', 3008: 'West Pomeranian Voivodeship', 3058: 'Alba County', 3059: 'Arad County', 3060: 'Argeș County', 3061: 'Bacău County', 3062: 'Bihor County', 3063: 'Bistrița-Năsăud County', 3064: 'Botoșani County', 3065: 'Brăila County', 3066: 'Brașov County', 3068: 'Buzău County', 3097: 'Călărași County', 3069: 'Caraș-Severin County', 3071: 'Constanța County', 3072: 'Covasna County', 3073: 'Dâmbovița County', 3074: 'Dolj County', 3075: 'Galați County', 3098: 'Giurgiu County', 3076: 'Gorj County', 3077: 'Harghita County', 3078: 'Hunedoara County', 3079: 'Ialomița County', 3080: 'Iași County', 3099: 'Ilfov County', 3081: 'Maramureș County', 3082: 'Mehedinți County', 3083: 'Mureș County', 3084: 'Neamț County', 3085: 'Olt County', 3086: 'Prahova County', 3087: 'Sălaj County', 3088: 'Satu Mare County', 3089: 'Sibiu County', 3090: 'Suceava County', 3091: 'Teleorman County', 3092: 'Timiș County', 3093: 'Tulcea County', 3095: 'Vâlcea County', 3094: 'Vaslui County', 3096: 'Vrancea County', 3100: 'Adygea', 3103: 'Altai Krai', 4164: 'Altai Republic', 3104: 'Amur Oblast', 3105: 'Arkhangelsk Oblast', 3106: 'Astrakhan Oblast', 3107: 'Bashkortostan', 3108: 'Belgorod Oblast', 3109: 'Bryansk Oblast', 3110: 'Buryatia', 3111: 'Chechnya', 3112: 'Chelyabinsk Oblast', 3114: 'Chukotka Autonomous Okrug', 3115: 'Chuvashia', 3118: 'Ingushetia', 3119: 'Irkutsk Oblast', 3120: 'Ivanovo Oblast', 3188: 'Jewish Autonomous Oblast', 3121: 'Kabardino-Balkaria', 3122: 'Kaliningrad Oblast', 3123: 'Kalmykia', 3124: 'Kaluga Oblast', 3125: 'Kamchatka Krai', 3126: 'Karachay-Cherkessia', 3128: 'Kemerovo Oblast', 3129: 'Khabarovsk Krai', 3130: 'Khakassia', 3131: 'Khanty-Mansi Autonomous Okrug', 3133: 'Komi Republic', 3136: 'Kostroma Oblast', 3139: 'Kurgan Oblast', 3140: 'Kursk Oblast', 3141: 'Leningrad Oblast', 3142: 'Lipetsk Oblast', 3143: 'Magadan Oblast', 3144: 'Mari El', 3145: 'Mordovia', 3147: 'Moscow Oblast', 3148: 'Murmansk Oblast', 3149: 'Nenets Autonomous Okrug', 3167: 'North Ossetia–Alania', 3151: 'Novgorod Oblast', 3152: 'Novosibirsk Oblast', 3153: 'Omsk Oblast', 3154: 'Orenburg Oblast', 3155: 'Oryol Oblast', 3156: 'Penza Oblast', 3158: 'Primorsky Krai', 3159: 'Pskov Oblast', 3127: 'Republic of Karelia', 3161: 'Ryazan Oblast', 3162: 'Sakha Republic', 3163: 'Sakhalin Oblast', 3168: 'Smolensk Oblast', 3169: 'Stavropol Krai', 3170: 'Sverdlovsk Oblast', 3171: 'Tambov Oblast', 3174: 'Tomsk Oblast', 3175: 'Tula Oblast', 3178: 'Tuva', 3176: 'Tver Oblast', 3177: 'Tyumen Oblast', 3179: 'Udmurtia', 3180: 'Ulyanovsk Oblast', 3182: 'Vladimir Oblast', 3184: 'Vologda Oblast', 3186: 'Yamalo-Nenets Autonomous Okrug', 3187: 'Yaroslavl Oblast', 4163: 'Zabaykalsky Krai', 3421: 'Banská Bystrica Region', 3424: 'Nitra Region', 3425: 'Presov', 3426: 'Trenčín Region', 3427: 'Trnava Region', 3428: 'Žilina Region', 3778: 'Cherkasy Oblast', 3780: 'Chernivtsi Oblast', 3783: 'Ivano-Frankivsk Oblast', 3785: 'Kherson Oblast', 3786: 'Khmelnytskyi Oblast', 3787: 'Kirovohrad Oblast', 3795: 'Poltava Oblast', 3796: 'Rivne Oblast', 3799: 'Ternopil Oblast', 3801: 'Volyn Oblast', 3804: 'Zhytomyr Oblast'}


# {city: {fb_key,region_id,vk_key}}, generated in schedule_generator.py
keys = {'Kyiv': {'fb_key': 2373594, 'region_id': 4290, 'vk_key': 314}, 'Dnipro': {'fb_key': 2367397, 'region_id': 3781, 'vk_key': 650}, 'Donetsk': {'fb_key': 2367700, 'region_id': 3782, 'vk_key': 223}, 'Zaporizhia': {'fb_key': 2400115, 'region_id': 3803, 'vk_key': 628}, 'Kryvyi Rih': {'fb_key': 2376357, 'region_id': 3781, 'vk_key': 916}, 'Lviv': {'fb_key': 2378495, 'region_id': 3792, 'vk_key': 1057}, 'Luhansk': {'fb_key': 2378330, 'region_id': 3791, 'vk_key': 552}, 'Mariupol': {'fb_key': 2400701, 'region_id': 3782, 'vk_key': 455}, 'Mykolaiv': {'fb_key': 2381338, 'region_id': 3793, 'vk_key': 377}, 'Odessa': {'fb_key': 2384095, 'region_id': 3794, 'vk_key': 292}, 'Sevastopol': {'fb_key': 2061384, 'region_id': 3124, 'vk_key': 185}, 'Simferopol': {'fb_key': None, 'region_id': None, 'vk_key': 627}, 'Kharkiv': {'fb_key': 2372604, 'region_id': 3784, 'vk_key': 280}, 'Vinnytsia': {'fb_key': 2397330, 'region_id': 3800, 'vk_key': 761}, 'Chernihiv': {'fb_key': 2366037, 'region_id': 3779, 'vk_key': 444}, 'Miskolc': {'fb_key': 939976, 'region_id': 1624, 'vk_key': 1067}, 'Kecskemét': {'fb_key': 936641, 'region_id': 1621, 'vk_key': 9733}, 'Szolnok': {'fb_key': 944744, 'region_id': 1640, 'vk_key': 14745}, 'Pécs': {'fb_key': 941877, 'region_id': 1622, 'vk_key': 20022}, 'Debrecen': {'fb_key': 932131, 'region_id': 1630, 'vk_key': 21233}, 'Szeged': {'fb_key': 944126, 'region_id': 1626, 'vk_key': 1704962}, 'Gyor': {'fb_key': 934570, 'region_id': 1629, 'vk_key': 1707464}, 'Szombathely': {'fb_key': 944768, 'region_id': 1642, 'vk_key': 1708002}, 'Budapest': {'fb_key': 931021, 'region_id': 1625, 'vk_key': 1905655}, 'Székesfehérvár': {'fb_key': 944163, 'region_id': 1628, 'vk_key': 1976180}, 'Nyíregyháza': {'fb_key': 941005, 'region_id': 1638, 'vk_key': 2209344}, 'Banská Bystrica': {'fb_key': 2166148, 'region_id': 3421, 'vk_key': 6267}, 'Bratislava': {'fb_key': 2166427, 'region_id': 3422, 'vk_key': 1908070}, 'Kosice': {'fb_key': 2168814, 'region_id': 3423, 'vk_key': 1707309}, 'Martin': {'fb_key': 2169565, 'region_id': 3428, 'vk_key': 5944}, 'Nitra': {'fb_key': 2169969, 'region_id': 3424, 'vk_key': 20044}, 'Presov': {'fb_key': 2170685, 'region_id': 3425, 'vk_key': 19307}, 'Trencin': {'fb_key': 2171869, 'region_id': 3426, 'vk_key': 10501}, 'Trnava': {'fb_key': 2171887, 'region_id': 3427, 'vk_key': 16422}, 'Zilina': {'fb_key': 2172724, 'region_id': 3428, 'vk_key': 21008}, 'Braila': {'fb_key': 1910075, 'region_id': 3065, 'vk_key': 1713324}, 'Brasov': {'fb_key': 1910129, 'region_id': 3066, 'vk_key': 1706305}, 'Bucharest': {'fb_key': 1910415, 'region_id': 3067, 'vk_key': 1913559}, 'Cluj-Napoca': {'fb_key': 1913066, 'region_id': 3070, 'vk_key': 13479}, 'Constanta': {'fb_key': 1913456, 'region_id': 3071, 'vk_key': 1707831}, 'Craiova': {'fb_key': 1914125, 'region_id': 3074, 'vk_key': 5404}, 'Galati': {'fb_key': 1917146, 'region_id': 3075, 'vk_key': 2002069}, 'Iasi': {'fb_key': 1919419, 'region_id': 3080, 'vk_key': 1970052}, 'Oradea': {'fb_key': 1924307, 'region_id': 3062, 'vk_key': 3232612}, 'Ploiesti': {'fb_key': 1925836, 'region_id': 3086, 'vk_key': 1516406}, 'Timisoara': {'fb_key': 1932115, 'region_id': 3092, 'vk_key': 14945}, 'Białystok': {'fb_key': 1838158, 'region_id': 3002, 'vk_key': 1936080}, 'Bydgoszcz': {'fb_key': 1841104, 'region_id': 2994, 'vk_key': 8505}, 'Gdansk': {'fb_key': 1846646, 'region_id': 3003, 'vk_key': 21280}, 'Gdynia': {'fb_key': 1846652, 'region_id': 3003, 'vk_key': 1517185}, 'Katowice': {'fb_key': 1853017, 'region_id': 3004, 'vk_key': 1929447}, 'Kraków': {'fb_key': 1842528, 'region_id': 2998, 'vk_key': 2202278}, 'Łódź': {'fb_key': 2674141, 'region_id': 2995, 'vk_key': 6823}, 'Lublin': {'fb_key': 1860279, 'region_id': 2996, 'vk_key': 6949}, 'Poznan': {'fb_key': 1869871, 'region_id': 3007, 'vk_key': 20436}, 'Szczecin': {'fb_key': 1878965, 'region_id': 3008, 'vk_key': 1962158}, 'Warsaw': {'fb_key': 1881861, 'region_id': 4135, 'vk_key': 1922897}, 'Wroclaw': {'fb_key': 2673802, 'region_id': 2993, 'vk_key': 1515655}, 'Moscow': {'fb_key': 2681947, 'region_id': 3138, 'vk_key': 1}, 'Saint Petersburg': {'fb_key': 2057269, 'region_id': 3165, 'vk_key': 2}, 'Volgograd': {'fb_key': 2097289, 'region_id': 3183, 'vk_key': 10}, 'Vladivostok': {'fb_key': 2096827, 'region_id': 3158, 'vk_key': 37}, 'Voronezh': {'fb_key': 2098072, 'region_id': 3185, 'vk_key': 42}, 'Yekaterinburg': {'fb_key': 2102961, 'region_id': 3170, 'vk_key': 49}, 'Kazan': {'fb_key': 1983489, 'region_id': 3172, 'vk_key': 60}, 'Kaliningrad': {'fb_key': 1979344, 'region_id': 3122, 'vk_key': 61}, 'Krasnodar': {'fb_key': 1997234, 'region_id': 3137, 'vk_key': 72}, 'Krasnoyarsk': {'fb_key': 1997692, 'region_id': 3138, 'vk_key': 73}, 'Nizhny Novgorod': {'fb_key': 2026949, 'region_id': 3150, 'vk_key': 95}, 'Novosibirsk': {'fb_key': 2031888, 'region_id': 3152, 'vk_key': 99}, 'Rostov-on-Don': {'fb_key': 2054807, 'region_id': 3160, 'vk_key': 119}, 'Samara': {'fb_key': 2682534, 'region_id': 3116, 'vk_key': 123}, 'Ufa': {'fb_key': 2086657, 'region_id': 3138, 'vk_key': 151}, 'Khabarovsk': {'fb_key': 1984342, 'region_id': 3129, 'vk_key': 153}, 'Omsk': {'fb_key': 2036122, 'region_id': 3153, 'vk_key': 104}, 'Perm': {'fb_key': 2041494, 'region_id': 4165, 'vk_key': 110}, 'Chelyabinsk': {'fb_key': 1957651, 'region_id': 3112, 'vk_key': 158}, 'Vitebsk': {'fb_key': 289528, 'region_id': 520, 'vk_key': 244}, 'Brest': {'fb_key': 277251, 'region_id': 514, 'vk_key': 281}, 'Minsk': {'fb_key': 283241, 'region_id': 517, 'vk_key': 282}, 'Mazyr': {'fb_key': 283566, 'region_id': 515, 'vk_key': 375}, 'Gomel': {'fb_key': 279027, 'region_id': 515, 'vk_key': 392}, 'Mahilyow': {'fb_key': 282540, 'region_id': 519, 'vk_key': 467}, 'Baranovichi': {'fb_key': 276325, 'region_id': 514, 'vk_key': 538}, 'Pinsk': {'fb_key': 285185, 'region_id': 514, 'vk_key': 610}, 'Grodno': {'fb_key': 279298, 'region_id': 516, 'vk_key': 649}, 'Bobruisk': {'fb_key': 276781, 'region_id': 519, 'vk_key': 1107}, 'Novopolatsk': {'fb_key': 284071, 'region_id': 520, 'vk_key': 1299}, 'Horki': {'fb_key': 279497, 'region_id': 519, 'vk_key': 2179}, 'Tiraspol': {'fb_key': 1418693, 'region_id': 2245, 'vk_key': 374}, 'Orhei': {'fb_key': 1417254, 'region_id': 2249, 'vk_key': 741}, 'Balti': {'fb_key': 1413731, 'region_id': 2242, 'vk_key': 953}, 'Bender': {'fb_key': 1413804, 'region_id': 4695, 'vk_key': 1223}, 'Dubasari': {'fb_key': 1414905, 'region_id': 2245, 'vk_key': 3902}, 'Comrat': {'fb_key': 1414597, 'region_id': 2247, 'vk_key': 3985}, 'Cahul': {'fb_key': 1414213, 'region_id': 2243, 'vk_key': 8384}, 'Chisinau': {'fb_key': 1414422, 'region_id': 2244, 'vk_key': 1710959}, 'Soroca': {'fb_key': 1418303, 'region_id': 2250, 'vk_key': 1801266}}

# age_lst = [[18, 0], [18, 40], [40, 64], [65, 0]]
age_lst =\
[{"min": 16, "max": 0},
{"min": 18, "max": 0},
{"min": 16, "max": 19},
{"min": 20, "max": 29},
{"min": 30, "max": 39},
{"min": 40, "max": 49},
{"min": 50, "max": 59},
{"min": 60, "max": 0},
{"min": 16, "max": 49},
{"min": 18, "max": 60}]
# for the curls


# Paths
data_path = Path.cwd() / 'collected_data'
work_path = Path.cwd()
specify_path = Path.cwd()/'collection_specify'

schedule_filename = 'schedule.csv'


