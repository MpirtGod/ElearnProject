import pandas as pd
from datetime import datetime

pd.set_option('expand_frame_repr', False)
file = 'vacancies_by_year.csv'
df = pd.read_csv(file)
df['years'] = df['published_at'].apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z").year)
unique_years = df['years'].unique()

for year in unique_years:
    data = df[df['years']==year]
    data.drop(['years'],axis=1).to_csv(f'csv_by_years\\part_{year}.csv', index=False)