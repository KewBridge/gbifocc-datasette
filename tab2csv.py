import argparse
import pandas as pd
import requests
from tqdm import tqdm
tqdm.pandas()

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile")
    parser.add_argument("-c","--createcols", action='store_true')
    parser.add_argument("-l","--limit", type=int)
    parser.add_argument("outputfile")    
    args = parser.parse_args()

    df = pd.read_csv(args.inputfile, 
                    encoding='utf8', 
                    keep_default_na=False, 
                    on_bad_lines='skip', 
                    sep='\t',
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