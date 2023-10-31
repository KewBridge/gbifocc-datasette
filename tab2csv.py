import argparse
import pandas as pd
import bananompy
from tqdm import tqdm
tqdm.pandas()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile")
    parser.add_argument("-c","--createcols", action='store_true')
    parser.add_argument("outputfile")    
    args = parser.parse_args()

    df = pd.read_csv(args.inputfile, 
                    encoding='utf8', 
                    keep_default_na=False, 
                    on_bad_lines='skip', 
                    sep='\t')
    if args.createcols:
        # Extract unique recordedBy values
        df_rb = df[['recordedBy']].drop_duplicates()
        df_rb['recordedBy_first_familyname'] = df_rb.recordedBy.progress_apply(getFirstFamilyName)
        # Apply back to main dataframe
        df = pd.merge(left = df, right=df_rb, left_on='recordedBy', right_on='recordedBy', how='left')
        # Add column holding collector name and number
        mask = (df.recordNumber.notnull())
        df.loc[mask,'collectorNameAndNumber']=df[mask].apply(lambda row: '{} {}'.format(row['recordedBy_first_familyname'],row['recordNumber']),axis=1)
    df.to_csv(args.outputfile, index=False, sep=',')    