#carefull if creating files on widows or ubuntu.
#moving/creating files back and forth between different operating systems 
#results in problems. use dos2unix to fix file issues

# cp ETL_toll_data.py $AIRFLOW_HOME/dags
# airflow webserver --port 8080
# airflow scheduler

import datetime
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago


default_args = {
    'owner': 'cc',
    'start_date': days_ago(0),
    'email': ['dummye@yyy.com'],
    'email_on_failure':	True,
    'email_on_retry':	True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

path="/home/cc/IBM_AIRFLOW/finalassignment/"




  
dag=DAG(
    dag_id='ETL_toll_data',
    description='Apache Airflow Final Assignment',
    default_args = default_args,
    schedule_interval = timedelta(hours=24),
)




unzip_data = BashOperator(
    task_id='unzip_data',
    bash_command=f'tar zxvf {path}tolldata.tgz',
    dag=dag,
)



extract_data_from_csv = BashOperator(
    task_id='extract_data_from_csv',
    bash_command=f'cut -d"," -f1,2,3,4 {path}vehicle-data.csv > {path}csv_data.csv',
    dag=dag,
)



# Tab is the default delimiter for cut
# An output delimiter ',' was added between the fields to the csv output file
extract_data_from_tsv = BashOperator(
    task_id='extract_data_from_tsv',
    bash_command=f"cut --output-delimiter=',' -f5,6,7 {path}tollplaza-data.tsv  > {path}tsv_data.csv ; dos2unix {path}tsv_data.csv",
    dag=dag,
)




# An output delimiter ',' was added between the fields to the csv output file
extract_data_from_fixed_width = BashOperator(
    task_id='extract_data_from_fixed_width',
    bash_command=f"cut --output-delimiter=',' -c59-61,63- {path}payment-data.txt  > {path}fixed_width_data.csv",
    dag=dag,
)



# delimiter ',' was added
consolidate_data = BashOperator(
    task_id='consolidate_data',
    bash_command=f'paste -d"," {path}csv_data.csv {path}tsv_data.csv {path}fixed_width_data.csv > {path}extracted_data.csv',
    dag=dag,
)



# transform_data = BashOperator(
#     task_id='transform_data',
#     bash_command='tr "[a-z]" "[A-Z]" < extracted_data.csv > staging/transformed_data.csv',
#     dag=dag,
# )



# Using awk instead of the bash tr command. With awk you can select the specific field to change to capital letters. 
# Only the vehicle_type field (field 4) is going to be change into capital letters: {$4=toupper($4)} .
# (\') and double curly braquets {{ and }} are used as python escape sequences in the bash_command string. 
# The file 'transformed_data.csv' is created. This file contains all the fields and values including the transformed values.
# the final bash awk command looks like this:
# awk -F "," 'BEGIN{FS=","; OFS=","}{$4=toupper($4)}1'  file_path/extracted_data.csv > file_path/staging/transformed_data.csv
transform_data = BashOperator(
    task_id='transform_data',

    bash_command=f'awk -F "," \'BEGIN{{FS=","; OFS=","}}{{$4=toupper($4)}}1\' {path}extracted_data.csv > {path}staging/transformed_data.csv',

    dag=dag,
)




# cp ETL_toll_data.py $AIRFLOW_HOME/dags
# airflow webserver --port 8080
# airflow scheduler




unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data




# awk -F "," '{print $1,",",$2,$3,$4=toupper($4),$5,$6,$7}' extracted_data.csv
# awk -i inplace 'BEGIN{FS=","; OFS=","} {$4=toupper($4)} {print}' extracted_data.csv
# awk -F "," '{$4=toupper($4)}1' extracted_data.csv

# awk -F "," 'BEGIN{FS=","; OFS=","}{$4=toupper($4)}1' extracted_data.csv > staging/transformed_data.csv

# bash_command='awk -F "," \'BEGIN{FS=","; OFS=","}{$4=toupper($4)}1\' /home/cc/IBM_AIRFLOW/finalassignment/extracted_data.csv > /home/cc/IBM_AIRFLOW/finalassignment/staging/transformed_data.csv',








#paste -d"," tsv_data.csv  csv_data.csv fixed_width_data.csv > extracted_data.csv