import argparse
from pygbif import occurrences as occ
import json


licences = {'http://creativecommons.org/licenses/by-nc/4.0/legalcode':'CC BY-NC 4.0'}
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile")
    parser.add_argument("--download_id", type=str)
    parser.add_argument("outputfile")    

    args = parser.parse_args()

    datasette_metadata = None
    with open(args.inputfile, 'r') as f_in:
        datasette_metadata = json.load(f_in)
 
    gbif_metadata = occ.download_meta(key = args.download_id)
    licence_url = gbif_metadata['license']
    if licence_url in licences:
        datasette_metadata['licence'] = licences[licence_url]
        datasette_metadata['licence_url'] = licence_url
    datasette_metadata['source_url'] = 'https://doi.org/{}'.format(gbif_metadata['doi'])

    datasette_metadata_json = json.dumps(datasette_metadata, indent=4)
    with open(args.outputfile, 'w') as f_out:
        f_out.write(datasette_metadata_json)