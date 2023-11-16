import argparse
import pandas as pd
import requests
from pygbif import occurrences as occ
from tqdm import tqdm
tqdm.pandas()
import os.path

def getFirstFamilyName(recordedBy):
    firstFamilyName = None
    parsed = bananompy.parse(recordedBy)
    try:
        firstFamilyName = parsed[0]['parsed'][0]['family']
    except:
        pass
    return firstFamilyName

def getFirstFamilyNames(recordedBy_l):
    # post to bionomia
    bionomia_parse_endpoint_url = "https://api.bionomia.net/parse.json"
    data = dict()
    data['names'] = '\r\n'.join(recordedBy_l)
    r = requests.post(bionomia_parse_endpoint_url, data=data)
    parsed_results = r.json()
    results = dict()
    for parsed_result in parsed_results:
        try:
            results[parsed_result['original']] = parsed_result['parsed'][0]['family']
        except:
            results[parsed_result['original']] = None
    return results

def getFirstFamilyNameBulk(df, 
                            recordedByColName="recordedBy", 
                            firstFamilyNameColName="recordedBy_first_familyname",
                            batchsize=500):
    results = dict()
    recordedBy_l = []
    for s in tqdm(df[recordedByColName].values):
        if len(recordedBy_l) == batchsize:
            # send it
            results.update(getFirstFamilyNames(recordedBy_l))
            # clear for next iteration
            recordedBy_l = []
        recordedBy_l.append(s)
    if len(recordedBy_l) > 0:
        results.update(getFirstFamilyNames(recordedBy_l))
    df[firstFamilyNameColName] = df[recordedByColName].map(results)
    return df

GBIF_DOWNLOAD_DESCRIBE_URL_SIMPLE_CSV = 'https://api.gbif.org/v1/occurrence/download/describe/simpleCsv'
GBIF_DOWNLOAD_DESCRIBE_URL_DWCA = 'https://api.gbif.org/v1/occurrence/download/describe/dwca'

def getGbifDownloadColumnNames(download_format):
    column_names = None
    if download_format == 'SIMPLE_CSV':
        r = requests.get(GBIF_DOWNLOAD_DESCRIBE_URL_SIMPLE_CSV)
        columns_metadata = r.json()
        column_names = [column_metadata['name'] for column_metadata in columns_metadata['fields']]
    elif download_format == 'DWCA':
        r = requests.get(GBIF_DOWNLOAD_DESCRIBE_URL_DWCA)
        columns_metadata = r.json()
        column_names = [column_metadata['name'] for column_metadata in columns_metadata['verbatim']['fields']]
    return column_names


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("download_id")
    parser.add_argument("-c","--createcols", action='store_true')
    parser.add_argument("-l","--limit", type=int)
    parser.add_argument("outputfile")    
    args = parser.parse_args()

    # Determine format of datafile by accessing download metadata from GBIF API
    gbif_metadata = occ.download_meta(key = args.download_id)
    download_format = gbif_metadata['request']['format']
    inputfile = None
    column_names_simple_csv = getGbifDownloadColumnNames('SIMPLE_CSV')
    column_names = None
    if download_format == 'SIMPLE_CSV':
        inputfile = '{}.csv'.format(args.download_id)
        column_names = column_names_simple_csv
    elif download_format == 'DWCA':
        inputfile = 'occurrence.txt'
        column_names_dwca = getGbifDownloadColumnNames('DWCA')
        column_names = [column_name for column_name in column_names_dwca if column_name in column_names_simple_csv]
        
    df = pd.read_csv(os.path.join('data',inputfile), 
                    encoding='utf8', 
                    keep_default_na=False, 
                    on_bad_lines='skip', 
                    sep='\t',
                    usecols=column_names,
                    nrows=args.limit)
    if args.createcols:
        # Extract unique recordedBy values
        df_rb = df[['recordedBy']].drop_duplicates()
        df_rb = getFirstFamilyNameBulk(df_rb)
        #df_rb['recordedBy_first_familyname'] = df_rb.recordedBy.progress_apply(getFirstFamilyName)
        # Apply back to main dataframe
        df = pd.merge(left = df, right=df_rb, left_on='recordedBy', right_on='recordedBy', how='left')
        # Add column holding collector name and number
        mask = (df.recordNumber.notnull())
        df.loc[mask,'collectorNameAndNumber']=df[mask].apply(lambda row: '{} {}'.format(row['recordedBy_first_familyname'],row['recordNumber']),axis=1)
    df.to_csv(args.outputfile, index=False, sep=',')    