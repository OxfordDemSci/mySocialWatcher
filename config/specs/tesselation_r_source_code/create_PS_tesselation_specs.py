import json
import os
from mysocialwatcher.collector import specs

collection_name = 'gaza_municipality_tessellation'
geo_level = 'municipalities'
custom_tessellation_file ='./config/specs/tesselation_r_source_code/PS_loc_queries_for_cover_by_custom_locations_municipalities_exterior.txt'
for platform in ['facebook', 'instagram']:
    # platform= 'facebook'
        tess_specs = specs.master_specs(country=collection_name,
                                            custom_tesselation= custom_tessellation_file,
                                            platform=platform,
                                            location_type='recent',
                                            regions=False,
                                            cities=False
                                            )
        if platform == 'facebook':
            idx = '1'
        else:
            idx = '2'

        outdir = "./config/specs/examples/" + collection_name

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        out_file = open(outdir + "/" + idx + '_' + platform + "_" + geo_level +".json", "w")
        json.dump(tess_specs['specs'], out_file)
        out_file.close()
