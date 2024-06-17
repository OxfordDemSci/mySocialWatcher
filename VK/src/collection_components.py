import requests
import re
from src import params
import pandas as pd
import time
import datetime
import logging
from src import params


def update_cookie():
    headers = {'authority': 'vk.com',
               # 'sec-ch-ua': " 'Not A;Brand';v='99', 'Chromium';v='98', 'Google Chrome';v='98'",
               'content-type': 'application/x-www-form-urlencoded',
               'x-requested-with': 'XMLHttpRequest',
               'Accept-Encoding': 'gzip, deflate, br',
               'sec-ch-ua-mobile': '?0',
               'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
               'sec-ch-ua-platform': '"macOS"',
               'accept': '*/*',
               'origin': 'https://vk.com',
               'sec-fetch-site': 'same-origin',
               'sec-fetch-mode': 'cors',
               'sec-fetch-dest': 'empty',
               'referer': 'https://vk.com/adscreate?parent_id=1021323290',
               'accept-language': 'en,en-US;q=0.9,zh-CN;q=0.8,zh;q=0.7'}

    with open(params.work_path / "useful_files/test.txt", "r") as f:
        lines = f.readlines()
        f.close()
    for i in lines:
        if 'cookie' in i:
            i = i.replace("  -H 'cookie: ", "").replace("\\", '').replace("'", "").replace("\n","")
            headers['cookie'] = i
    return headers


def data_dict_country_level(age_range, country, gender):
    data_to_send = {'_price_list_allowed': '0', 'ad_id': '0', 'age_from': str(age_range[0]), 'age_restriction': '0',
                    'age_to': str(age_range[1]), 'al': '1', 'allow_format_photo_size_change': '1', 'apps': '',
                    'apps_not': '', 'audience_notify': '1', 'autoaudience': '0', 'autobidding': '0',
                    'birthday': '0', 'browsers': '', 'campaign_goal_enabled': '0', 'campaign_id': '1021323290',
                    'campaign_name': '', 'campaign_type': '0', 'category1_id': '', 'category2_id': '', 'cities': '',
                    'cities_not': '', 'client_id': '1607260977', 'cost_per_click': '1.20', 'cost_type': '1',
                    'country': str(country),
                    'criteria_preset_name': '', 'criteria_preset_name_button': '', 'criteria_presets': '',
                    'description': '', 'disclaimer_finance': '0', 'disclaimer_finance_license_no': '',
                    'disclaimer_finance_name': '', 'disclaimer_medical': '0', 'disclaimer_specialist': '0',
                    'disclaimer_supplements': '0', 'districts': '', 'events_retargeting_groups': '',
                    'format_subtype': '0', 'format_type': '1', 'geo_mask': '', 'geo_near': '', 'geo_type': '0',
                    'goal_type': '1', 'goal_type_text': 'Ad%20impressions', 'group_types': '', 'groups': '',
                    'groups_active': '', 'groups_active_formula': '', 'groups_active_recommended': '',
                    'groups_force_disabled': '0', 'groups_formula': '', 'groups_not': '', 'groups_recommended': '',
                    'interest_categories': '', 'interest_categories_formula': '', 'interests': '',
                    'is_cbo_enabled': '0',
                    'is_goal_conversion_inapp_allow': 'false', 'key_phrases': '', 'key_phrases_days': '12',
                    'link_button': '',
                    'link_complete': '1', 'link_domain': 'ox.ac.uk', 'link_domain_confirm': '0', 'link_id': '',
                    'link_owner_id': '',
                    'link_subtype': 'url', 'link_title': '', 'link_type': '5', 'link_url': 'www.ox.ac.uk',
                    'link_url_vk': '0',
                    'mobile_apps_events_formula': '', 'mobile_manufacturers': '', 'mobile_os_max_version': '0',
                    'mobile_os_min_version': '0', 'music_artists_formula': '', 'need_cities_data': 'true',
                    'operators': '',
                    'pay_info': '', 'pays_money': '0', 'photo': '', 'photo_icon': '', 'photo_link': '',
                    'pixel_conversion_event_id': '1',
                    'pixel_conversion_pixel_id': '0', 'platform': '5', 'platform_no_ad_network': '0',
                    'platform_no_wall': '0', 'positions': '',
                    'promoted_post_need_confirmation': '0', 'religions': '', 'repeat_video': 'false',
                    'retargeting_groups': '',
                    'retargeting_groups_not': '', 'school_from': '0', 'school_to': '0', 'schools': '',
                    'schools_type': '0',
                    'sex': str(gender), 'source': '', 'stations': '', 'stats_url2': '', 'stats_url': '',
                    'stats_url_long2': '', 'stats_url_long': '', 'statuses': '', 'streets': '', 'subcategory1_id': '',
                    'subcategory2_id': '', 'suggested_criteria': '', 'tags': '', 'targeting_formula_enabled': '0',
                    'title': '',
                    'travellers': '0', 'uni_from': '0', 'uni_to': '0', 'unlimited_user_ad_actions': '0',
                    'user_browsers': '',
                    'user_devices': '', 'user_goal_type': '2', 'user_operating_systems': '', 'video_hash': '',
                    'video_id': '',
                    'video_owner_id': '', 'view_retargeting_group_id': '0', 'views_limit_exact': '0',
                    'views_limit_flag': '0',
                    'views_limit_period': '0', 'weekly_schedule': '', 'wifi_only': '0'}
    return data_to_send


def data_dict(age_range, gender, country, city, traveller):
    data_to_send = {'_price_list_allowed': '0', 'ad_id': '0',
                    'age_from': str(age_range[0]),
                    'age_restriction': '0',
                    'age_to': str(age_range[1]),
                    'country': str(country),
                    'sex': str(gender),
                    'cities': str(city),
                    'cities_not': '',
                    'al': '1', 'allow_format_photo_size_change': '1', 'apps': '', 'apps_not': '',
                    'audience_notify': '0',
                    'autoaudience': '0', 'autobidding': '0', 'birthday': '0', 'browsers': '',
                    'campaign_goal_enabled': '0',
                    'campaign_id': '1021323290', 'campaign_name': '', 'campaign_type': '0', 'category1_id': '',
                    'category2_id': '', 'client_id': '1607260977', 'cost_per_click': '6.00',
                    'cost_type': '2',
                    'criteria_preset_name': '', 'criteria_preset_name_button': '', 'criteria_presets': '',
                    'description': '',
                    'disclaimer_finance': '0', 'disclaimer_finance_license_no': '', 'disclaimer_finance_name': '',
                    'disclaimer_medical': '0', 'disclaimer_specialist': '0', 'disclaimer_supplements': '0',
                    'districts': '',
                    'events_retargeting_groups': '', 'format_subtype': '0', 'format_type': '1', 'geo_mask': '',
                    'geo_near': '',
                    'geo_type': '0', 'goal_type': '2', 'goal_type_text': 'Ad%20clicks', 'group_types': '', 'groups': '',
                    'groups_active': '', 'groups_active_formula': '', 'groups_active_recommended': '',
                    'groups_force_disabled': '0', 'groups_formula': '', 'groups_not': '', 'groups_recommended': '',
                    'interest_categories': '', 'interest_categories_formula': '', 'interests': '',
                    'is_cbo_enabled': '0',
                    'is_goal_conversion_inapp_allow': 'false', 'key_phrases': '', 'key_phrases_days': '12',
                    'link_button': '',
                    'link_complete': '1', 'link_domain': 'ox.ac.uk', 'link_domain_confirm': '0', 'link_id': '',
                    'link_owner_id': '', 'link_subtype': 'url', 'link_title': '', 'link_type': '5',
                    'link_url': 'www.ox.ac.uk',
                    'link_url_vk': '0', 'mobile_apps_events_formula': '', 'mobile_manufacturers': '',
                    'mobile_os_max_version': '0', 'mobile_os_min_version': '0', 'music_artists_formula': '',
                    'need_cities_data': 'true', 'operators': '', 'pay_info': '', 'pays_money': '0', 'photo': '',
                    'photo_icon': '', 'photo_link': '', 'pixel_conversion_event_id': '1',
                    'pixel_conversion_pixel_id': '0',
                    'platform': '1', 'platform_no_ad_network': '0', 'platform_no_wall': '0', 'positions': '',
                    'promoted_post_need_confirmation': '0', 'religions': '', 'repeat_video': 'false',
                    'retargeting_groups': '',
                    'retargeting_groups_not': '', 'school_from': '0', 'school_to': '0', 'schools': '',
                    'schools_type': '0',
                    'source': '', 'stations': '', 'stats_url2': '', 'stats_url': '', 'stats_url_long2': '',
                    'stats_url_long': '', 'statuses': '', 'streets': '', 'subcategory1_id': '', 'subcategory2_id': '',
                    'suggested_criteria': '', 'tags': '', 'targeting_formula_enabled': '0', 'title': '',
                    'travellers': str(traveller),
                    'uni_from': '0', 'uni_to': '0', 'unlimited_user_ad_actions': '0', 'user_browsers': '',
                    'user_devices': '',
                    'user_goal_type': '3', 'user_operating_systems': '', 'video_hash': '', 'video_id': '',
                    'video_owner_id': '',
                    'view_retargeting_group_id': '0', 'views_limit_exact': '0', 'views_limit_flag': '0',
                    'views_limit_period': '0', 'weekly_schedule': '', 'wifi_only': '0'}
    return data_to_send



url = 'https://vk.com/adsedit?act=get_target_params'






#data = collection_components.data_dict_country_level(age_range=[18,25],gender=0,country=200)
