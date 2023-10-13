import json
from typing import Union
import math


def get_predefined_behavior(option):
    if option == "connectivity":
        bgrp = BehaviorGroup("access_device")

        b_2g = BehaviorList(list_name="2G", operator="or")
        b_2g.add(Behavior(6017253486583))
        b_3g = BehaviorList(list_name="3G", operator="or")
        b_3g.add(Behavior(6017253511583))
        b_4g = BehaviorList(list_name="4G", operator="or")
        b_4g.add(Behavior(6017253531383))
        b_wifi = BehaviorList(list_name="Wifi", operator="or")
        b_wifi.add(Behavior(6015235495383))

        bgrp.add(b_2g)
        bgrp.add(b_3g)
        bgrp.add(b_4g)
        bgrp.add(b_wifi)
        bgrp.add(None)

        bgrps = BehaviorGroups()
        bgrps.add(bgrp)
        return bgrps

    elif option in ["phone", "ios"]:
        bgrp = BehaviorGroup("access_device")

        b_ios = BehaviorList(list_name="iOS", operator="or")
        b_ios.add(Behavior(6004384041172))

        b_android = BehaviorList(list_name="Android", operator="or")
        b_android.add(Behavior(6004386044572))

        b_other = BehaviorList(list_name="Other", operator="not")
        b_other.add(Behavior(6004384041172))
        b_other.add(Behavior(6004386044572))

        bgrp.add(b_ios)
        bgrp.add(b_android)
        bgrp.add(b_other)
        bgrp.add(None)

        bgrps = BehaviorGroups()
        bgrps.add(bgrp)
        return bgrps

    else:
        print("Option %s is not recognized." % option)

    return None


class Behavior(object):

    def __init__(self, behavior_id):
        self.behavior_id = behavior_id

    def jsonfy(self):
        return self.behavior_id


class BehaviorList(object):

    def __init__(self, list_name: str, operator: str):
        self.name = list_name
        self.behavior_list = []
        self.operator = operator
        assert self.operator in ["or", "and", "not", "and_ors"]

    def add(self, behavior: Behavior):
        self.behavior_list.append(behavior)

    def jsonfy(self):
        return {"name": self.name, self.operator: [b.jsonfy() for b in self.behavior_list]}


class BehaviorGroup(object):

    def __init__(self, group_name: str):
        self.group_name = group_name
        self.behavior_lists = []

    def add(self, behavior_list: BehaviorList):
        # Check if behavior is already included in the list
        for bl in self.behavior_lists:
            if (behavior_list is None and bl is None):
                print("Behavior List None is already included in the list.")
                return
            elif (behavior_list is not None and bl is not None and behavior_list.name == bl.name):
                print("Behavior List named %s is already included in the list." % bl.name)
                return

        self.behavior_lists.append(behavior_list)


class BehaviorGroups(object):

    def __init__(self):
        self.behavior_groups = []

    def add(self, behavior_group: BehaviorGroup):
        self.behavior_groups.append(behavior_group)

    def merge(self, another_behavior_groups):
        for grp_another in another_behavior_groups.behavior_groups:
            for grp_me in self.behavior_groups:
                # same group, just add it
                if grp_another.group_name == grp_me.group_name:
                    for blist in grp_another.behavior_lists:
                        grp_me.add(blist)
                else:
                    self.add(grp_another)

    def jsonfy(self):
        return dict(
            [(grp.group_name, [b.jsonfy() if b else None for b in grp.behavior_lists]) for grp in self.behavior_groups]
        )


class Scholarity(object):

    def __init__(self, name: str, operator: str, values: list):
        self.name = name
        self.values = values
        self.operator = operator

    def jsonfy(self):
        return {"name": self.name, self.operator: [v for v in self.values]}

    @staticmethod
    def from_pre_defined_list(name):
        if name.lower().replace("_", "").replace(" ", "") == "nodegree":
            return Scholarity("No Degree", "or", [1, 12, 13])
        elif name.lower().replace("_", "").replace(" ", "") == "highschool":
            return Scholarity("High School", "or", [2, 4, 5, 6, 10])
        elif name.lower().replace("_", "").replace(" ", "") == "graduated":
            return Scholarity("Graduated", "or", [3, 7, 8, 9, 11])
        else:
            raise ValueError("Could not find %s in the pre-defined list. "
                             "Options are: no_degree, high_school or graduated" % (name))


class ScholarityList(object):

    def __init__(self):
        self.scholarity_list = []

    def add(self, scholarity: Scholarity):
        self.scholarity_list.append(scholarity)

    def jsonfy(self):
        return [scholarity.jsonfy() if scholarity is not None else None for scholarity in self.scholarity_list]


class Genders(object):

    def __init__(self, male: bool = False, female: bool = False, combined: bool = False):
        if male is False and female is False and combined is False:
            raise ValueError("At least one of ''male'', ''female'' and ''combined'' should be True.")
        self.male = male
        self.female = female
        self.combined = combined

    def jsonfy(self):
        g = []
        if self.combined:
            g.append(0)
        if self.male:
            g.append(1)
        if self.female:
            g.append(2)
        return g


class Age(object):
    def __init__(self, min_age: int = None, max_age: int = None):
        self.min_age = min_age
        self.max_age = max_age

    def jsonfy(self):
        s = {}
        if self.min_age:
            s["min"] = self.min_age
        if self.max_age:
            s["max"] = self.max_age
        return s


class AgeList(object):
    def __init__(self):
        self.ages = []

    def add(self, age: Age):
        self.ages.append(age)

    def jsonfy(self):
        return [age_pair.jsonfy() for age_pair in self.ages]


class Location(object):
    def __init__(self, loc_type: str, values: dict, location_types: list = ["home", "recent"]):
        self.location = {"name": loc_type, "values": values, "location_types": location_types}

    def jsonfy(self):
        return self.location


class LocationList(object):
    def __init__(self):
        self.location_list = []

    def add(self, location: Union[Location, 'LocationList']):
        if isinstance(location, LocationList):
            for loc in location.location_list:
                self.add(loc)

        elif isinstance(location, Location):
            self.location_list.append(location)

        else:
            print("ERROR: Location List did not expect an input of type %s." % (type(location)))

    def split(self, n):
        """
        Split the list of locations into N pieces
        :param n:
        :return:
        """
        nlocations = len(self.location_list)
        step = math.ceil(nlocations / n)
        result = []
        for i in range(0, nlocations, step):
            ll = LocationList()
            for j in range(i, min(i + step, nlocations)):
                ll.add(self.location_list[j])
            result.append(ll)
        return result

    def get_location_list_from_df(self, df_in, city_radius=0):

        df = df_in[~df_in["key"].isnull()].copy()

        # That is a country collection. Keys are country codes and type is not available.
        if "type" in df:
            df["key"] = df["key"].astype(int)

        if "region_id" in df:
            df["region_id"] = df["region_id"].astype(int)

        for idx, row in df.iterrows():
            # TODO: include other types as zip or custom
            if "type" not in row:  # country does not have type.
                loc = Location(loc_type="countries", values=[row["key"]])

            elif row["type"] == "region":
                loc = Location(loc_type="regions",
                               values=[{"key": row["key"], "country_code": row["country_code"], "name": row["name"]}])

            elif row["type"] == "city":
                loc = Location(loc_type="cities",
                               values=[{"key": row["key"], "region": row["region"], "region_id": row["region_id"],
                                        "country_code": row["country_code"], "name": row["name"],
                                        "distance_unit": "kilometer", "radius": city_radius}]
                               )
            self.location_list.append(loc)

    def jsonfy(self):
        return [location.jsonfy() for location in self.location_list]


class Language(object):
    def __init__(self, lang_name: str, values: list):
        self.location = {"name": lang_name, "values": values}

    def jsonfy(self):
        return self.location


class LanguageList(object):
    def __init__(self):
        self.langs = []

    def add(self, lang: Language):
        self.langs.append(lang)

    def add_predefined(self, lang: str):
        predefined = {"english": Language("English", [1001]),
                      "spanish": Language("Spanish", [1002]),
                      "french": Language("French", [1003]),
                      "chinese": Language("Chinese", [1004]),
                      "portuguese": Language("Portuguese", [1005]),
                      "arabic": Language("Arabic", [28]),
                      "italian": Language("Italian", [10]),
                      "german": Language("German", [5]),
                      "dutch": Language("Dutch", [14]),
                      "ukrainian": Language("Ukrainian", [52]),
                      "russian": Language("Russian", [17]),
                      "arabic": Language("Arabic", [28]),
                      "turkish": Language("Turkish", [19]),
                      "hebrew": Language("Hebrew", [29])
                      }

        if lang.lower() not in predefined.keys():
            print("Language %s is not in the predefined list '%s'" % (lang, predefined.keys()))
            return

        self.add(predefined[lang.lower()])

    def jsonfy(self):
        return [lang.jsonfy() if lang is not None else None for lang in self.langs]


class JSONBuilder:

    def __init__(self, name: str, location_list: LocationList, age_list: AgeList, genders: Genders,
                 behavior_groups: BehaviorGroups = None, scholarities: ScholarityList = None,
                 languages: LanguageList = None):

        self.name = name
        self.age_list = age_list
        self.location_list = location_list
        self.genders = genders
        self.behavior_groups = behavior_groups
        self.scholarities = scholarities
        self.languages = languages

    def jsonfy(self, filename=None, split_into_n_pieces=1):
        """
        This creates as many pieces of json as possible using filenme_<piece_num> if split_into_pieces > 1.
        Each one of the n pieces will have a 1/n of the locations.

        :param filename:
        :param split_into_n_pieces:
        :return:
        """

        out = {"name": self.name,
               "geo_locations": self.location_list.jsonfy(),
               "ages_ranges": self.age_list.jsonfy(),
               "genders": self.genders.jsonfy()}

        if self.behavior_groups is not None:
            out["behavior"] = self.behavior_groups.jsonfy()

        if self.scholarities is not None:
            out["scholarities"] = self.scholarities.jsonfy()

        if self.languages is not None:
            out["languages"] = self.languages.jsonfy()

        if filename:
            if split_into_n_pieces == 1:
                if not filename.endswith(".json"):
                    filename += ".json"
                with open(filename, 'w') as outfile:
                    json.dump(out, outfile, indent=4)
                print("Created file %s." % filename)
            else:
                loclists = self.location_list.split(split_into_n_pieces)
                for i, piece in enumerate(loclists):
                    out["geo_locations"] = piece.jsonfy()
                    if filename.endswith(".json"):
                        filename = filename.rsplit(".json")[0]

                    f = filename + "_%d.json" % i
                    with open(f, 'w') as outfile:
                        json.dump(out, outfile, indent=4)
                    print("Created file %s." % f)

        return out


def get_location_list_from_df(df_in):
    loc_list = LocationList()

    df = df_in[~df_in["key"].isnull()].copy()
    df["key"] = df["key"].astype(int)
    df["region_id"] = df["region_id"].astype(int)

    for idx, row in df.iterrows():
        if row["type"] == "region":
            loc = Location(loc_type="regions",
                           values=[{"key": row["key"], "country_code": row["country_code"], "name": row["name"]}])
            loc_list.add(loc)

        elif row["type"] == "city":
            loc = Location(loc_type="cities",
                           values=[{"key": row["key"], "region": row["region"], "region_id": row["region_id"],
                                    "country_code": row["country_code"], "name": row["name"],
                                    "distance_unit": "kilometer", "radius": 0}]
                           )
            loc_list.add(loc)

    return loc_list
