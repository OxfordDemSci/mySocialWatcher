import os
import shutil
import pandas as pd
import numpy as np
import json

# virtual machine and collection
vm = "serenity"
collection = "migration_asia_pacific"


if __name__ == "__main__":

    # ---- paths ---- #
    master_credentials_path = os.path.join(
        "config", "private", "credentials_master.csv"
    )
    specs_template_path = os.path.join(
        "config", "specs", "examples", "global_migration"
    )

    out_dir = os.path.join("docker", "collectors", vm, collection)
    os.makedirs(out_dir, exist_ok=True)
    yagmail_path = os.path.join("config", "private", "yagmail.csv")

    # ---- credentials ---- #

    # path for output credentials.csv
    credentials_path = os.path.join(out_dir, "credentials.csv")

    # load master credentials
    master_credentials = pd.read_csv(master_credentials_path)

    # filter vm and collection
    credentials = master_credentials.loc[
        (master_credentials.vm == vm) & (master_credentials.collection == collection)
    ]

    # convert app to int
    credentials = credentials.copy()
    credentials["app"] = credentials["app"].astype(np.int64)

    # save to csv
    credentials.to_csv(
        credentials_path, columns=["token", "app"], header=False, index=False
    )

    # ---- yagmail credential ---- #
    if os.path.exists(yagmail_path):
        shutil.copy2(yagmail_path, os.path.join(out_dir, "yagmail.csv"))

    # ---- collection specs ---- #

    # output directory
    specs_dir = os.path.join(out_dir, "specs")
    os.makedirs(specs_dir, exist_ok=True)

    # cleanup old specs
    for f in os.listdir(specs_dir):
        os.remove(os.path.join(specs_dir, f))

    # template json
    specs_file = os.path.join(specs_template_path, "global_migration_core.json")

    with open(specs_file) as f:
        specs = json.load(f)

    specs["name"] = collection

    # countries
    countries = [
        "AF",
        "AM",
        "AU",
        "AZ",
        "BD",
        "BT",
        "BN",
        "KH",
        "CN",
        "KP",
        "FJ",
        "FR",
        "GE",
        "IN",
        "ID",
        "IR",
        "JP",
        "KZ",
        "KI",
        "KG",
        "LA",
        "MY",
        "MV",
        "MH",
        "FM",
        "MN",
        "MM",
        "NR",
        "NP",
        "NL",
        "NZ",
        "PK",
        "PW",
        "PG",
        "PH",
        "KR",
        "RU",
        "WS",
        "SG",
        "SB",
        "LK",
        "TJ",
        "TH",
        "TL",
        "TO",
        "TR",
        "TM",
        "TV",
        "GB",
        "US",
        "UZ",
        "VU",
        "VN",
        "AS",
        "CK",
        "PF",
        "GU",
        "HK",
        "MO",
        "NC",
        "NU",
        "MP",
    ]
    countries.sort()

    drop_countries = ["JP", "KH", "KI", "KP", "KR", "NU", "RU"]
    drop_countries = drop_countries + ["CU", "SD", "IR", "SY", "RU"]
    countries = [i for i in countries if i not in drop_countries]

    # ages
    specs["ages_ranges"] = [
        {"min": 13},
        {"min": 18},
        {"min": 50},
        {"min": 60},
        {"min": 65},
        {"min": 13, "max": 17},
        {"min": 13, "max": 19},
        {"min": 15, "max": 49},
        {"min": 18, "max": 64},
        {"min": 20, "max": 29},
        {"min": 30, "max": 39},
        {"min": 40, "max": 49},
        {"min": 50, "max": 59},
        {"min": 60, "max": 64},
    ]

    platforms = ["facebook", "instagram"]

    for platform in platforms:

        # platform
        specs["publisher_platforms"] = [platform]

        for country in countries:
            
            # geo_location
            specs["geo_locations"] = [{"name": "countries", "values": [country]}]

            # save specs
            file_out = os.path.join(
                specs_dir, "migration_asia_pacific_" + platform + "_" + country + ".json"
            )
            with open(file_out, "w") as f:
                f.write(json.dumps(specs))
