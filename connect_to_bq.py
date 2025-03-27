import os
import pandas as pd
from pandas.io import gbq
from google.cloud import bigquery
from google.oauth2 import service_account


def insert_data_with_gbq(project, dataset, output_folder):
    key_path = "C:/Users/rrichardson/Downloads/Randolph Richardson/resortpass-95e58f22fb8d.json"
    credentials = service_account.Credentials.from_service_account_file(key_path)
    
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    os.makedirs(output_folder, exist_ok=True)

    dataset_id = f"{project}.{dataset}"
    dataset_ref = bigquery.DatasetReference.from_string(dataset_id)

    tables = client.list_tables(dataset_ref)

    print("Tables in the dataset:")
    for table in tables:
        print(f"- {table.table_id}")
        
        query = f"SELECT * FROM `{dataset_id}.{table.table_id}`"
        df = gbq.read_gbq(query, project_id=project, credentials=credentials)
        
        output_path = os.path.join(output_folder, f"{table.table_id}.csv")
        df.to_csv(output_path, index=False)

        print(f"Downloaded: {table.table_id} → {output_path}")

insert_data_with_gbq('resortpass', 'raw', 'uploaded_data')

