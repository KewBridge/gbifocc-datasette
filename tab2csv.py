import argparse
import pandas as pd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile")
    parser.add_argument("outputfile")    
    args = parser.parse_args()

    df = pd.read_csv(args.inputfile, 
                    encoding='utf8', 
                    keep_default_na=False, 
                    on_bad_lines='skip', 
                    sep='\t')
    df.to_csv(args.outputfile, index=False, sep=',')    