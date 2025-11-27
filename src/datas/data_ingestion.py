# data ingestion
import numpy as np
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

import os
from sklearn.model_selection import train_test_split
import yaml

# from src.connections import s3_connection
from src.functions import load_csv, load_params, save_data
from src.logger import logger

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the data."""
    try:
        # df.drop(columns=['tweet_id'], inplace=True)
        logger.info("pre-processing...")
        final_df = df[df['sentiment'].isin(['positive', 'negative'])]
        final_df['sentiment'] = final_df['sentiment'].replace({'positive': 1, 'negative': 0})
        logger.info('Data preprocessing completed')
        return final_df
    except KeyError as e:
        logger.error('Missing column in the dataframe: %s', e)
        raise
    except Exception as e:
        logger.error('Unexpected error during preprocessing: %s', e)
        raise



def main():
    try:
        params = load_params(params_path='params.yaml')
        test_size = params['data_ingestion']['test_size']

        
        df = load_csv(data_url='https://raw.githubusercontent.com/vikashishere/Datasets/refs/heads/main/data.csv')
        # s3 = s3_connection.s3_operations("bucket-name", "accesskey", "secretkey")
        # df = s3.fetch_file_from_s3("data.csv")


        final_df = preprocess_data(df)
        train_data, test_data = train_test_split(final_df, test_size=test_size, random_state=42)
        
        # ROOT_DIR = ROOT_DIR = os.path.dirname(
        #         os.path.dirname(
        #             os.path.dirname(os.path.abspath(__file__)))
        #     )
        # data_path = os.path.join(ROOT_DIR,'data')
        
        raw_data_path = os.path.join('./data', 'raw')
        os.makedirs(raw_data_path, exist_ok=True)
        
        save_data(train_data, test_data, data_path=raw_data_path)
    except Exception as e:
        logger.error('Failed to complete the data ingestion process: %s', e)
        print(f"Error: {e}")

if __name__ == '__main__':
    main()