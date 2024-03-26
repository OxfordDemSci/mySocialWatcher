import json

from mysocialwatcher.collector import specs

ukr_tess_specs = specs.master_specs(country='ukraine_tesselation',
                                    regions=False,
                                    platform='facebook',
                                    location_type='recent',
                                    custom_tesselation='K:/DemSci/projects/2023_WHO_Ukraine_Population/data/tmp/gadm2_tessellation/wd/UKR/out/loc_queries/UKR_loc_queries_for_cover_by_custom_locations_GADM2_regions.txt',
                                    cities=False
                                    )

out_file = open("C:/Users/edithd/Documents/mySocialWatcher/docker/collectors/saffron/ukraine_tesselation/specs/1_facebook_all_admin2.json", "w")
json.dump(ukr_tess_specs['specs'], out_file)
out_file.close()