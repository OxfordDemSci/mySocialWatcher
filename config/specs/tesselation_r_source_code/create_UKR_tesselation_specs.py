import json
import os
from mysocialwatcher.collector import specs

for platform in ['facebook', 'instagram']:
    # platform= 'facebook'
    for cover_type in ['interior']:
        # cover_type = 'interior'
        ukr_tess_specs = specs.master_specs(country='ukraine_admin2_tesselation_' + cover_type,
                                            custom_tesselation='K:/DemSci/projects/2023_WHO_Ukraine_Population/data/tmp/gadm2_tessellation/wd/UKR/out/loc_queries/UKR_loc_queries_for_cover_by_custom_locations_GADM2_regions_' + cover_type + '.txt',
                                            platform=platform,
                                            location_type='recent',
                                            regions=False,
                                            cities=False
                                            )
        if platform == 'facebook':
            idx = '1'
        else:
            idx = '2'

        outdir = "C:/Users/edithd/Documents/mySocialWatcher/config/specs/examples/ukraine_admin2_tesselation_" + cover_type

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        out_file = open(outdir + "/" + idx + '_' + platform + "_all_admin2_" + cover_type + ".json", "w")
        json.dump(ukr_tess_specs['specs'], out_file)
        out_file.close()
