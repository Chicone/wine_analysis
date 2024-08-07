import os.path
import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler


class DataLoader:
    def __init__(self, file_path, normalize=True):
        self.file_path = file_path
        self.data, self.df = self.load_data()
        if normalize:
            # Normalise dictionary values
            self.normalize_dict(scaler='minmax')  # standard minmax robust
            self.df = pd.DataFrame(self.data).T

    def load_data(self):
        print('Loading data...')
        if self.file_path.endswith('.npy'):
            data = np.load(self.file_path, allow_pickle=True).item()
            df = pd.DataFrame(data).T
        elif self.file_path.endswith('.xlsx'):
            df = pd.read_excel(self.file_path)
            data = self.process_xlsx(df, self.file_path)
            df = pd.DataFrame(data).T
        else:
            raise ValueError("Unsupported file format")
        return data, df

    def get_standardized_data(self):
        scaler = StandardScaler()
        return scaler.fit_transform(self.df)

    def normalize_dict(self, scaler='standard'):
        # Normalise dictionary values
        keys = list(self.data.keys())
        values = np.array(list(self.data.values()))
        values_scaled = None
        if scaler == 'standard':
            scaler = StandardScaler()
            values_scaled = scaler.fit_transform(values)
        elif scaler == 'minmax':
            scaler = MinMaxScaler()
            values_scaled = scaler.fit_transform(values)
        elif scaler == 'robust':
            scaler = RobustScaler()
            values_scaled = scaler.fit_transform(values)
        self.data = {key: values_scaled[idx, :].tolist() for idx, key in enumerate(keys)}


    def process_xlsx(self, df, file_path):
        """Implements the logic to appropriately process each dataset based on its file name"""

        files = ['2018 7 chateaux Ester Old vintages Masse 5.xlsx',                 #  0
                 '2018 7 chateaux Oak Old vintages Masse 5.xlsx',                   #  1
                 '2018 7 chateaux Off Old vintages Masse 5.xlsx',                   #  2
                 '2022 01 11 chateaux Oak All vintages Masse 5 NORMALIZED SM.xlsx', #  3
                 '2022 4 new bordeaux Oak Masse 5 NORMALIZED 052022 SM2 .xlsx',     #  4
                 '2022 01 7 chateaux Oak All vintages Masse 5 NORMALIZED SM.xlsx',  #  5
                 '2022 01 7 chateaux Oak Old vintages Masse 5 NORMALIZED SM.xlsx',  #  6
                 ]
        file_name = os.path.basename(file_path)

        if file_name in files[0:3]:
            # Remove first few rows with text
            for i in range(len(df)):
                if df.iloc[i].count() > 1:
                    df = pd.read_excel(self.file_path, skiprows=i)
                    break
            # Remove the last row to avoid nan
            df = df.iloc[:-1]

            data = {}
            for col in df.columns:
                label = df[col][0]  # detect the header
                if not isinstance(label, str):
                    continue
                if "Ab" in label:
                    pattern = r'Ab \S*[_ ]?([A-Z][ _]?\d{4})'
                    key = label.replace('\n', '')
                    key = re.sub(pattern, r'\1', key)  # use re.sub to remove the matching prefix
                    data[key] = [float(value) for value in df[col].tolist()[1:]]

        if file_name in [files[3], files[5], files[6]]:
            # Remove first row (contains text) and last one (for nan)
            df = df.iloc[1:]
            df = df.iloc[:-1]
            df.columns = df.iloc[0]

            data = {}
            for col in df.columns:
                if not isinstance(col, str):
                    continue
                key = col  # detect the header
                data[key] = [float(value) for value in df[col].tolist()[2:]]

        if file_name in files[4]:
            # Remove last 15 rows (zero value)
            df = df.iloc[:-15]

            data = {}
            for col in df.columns:
                if "Unnamed" in col:
                    continue
                key = col  # detect the header
                data[key] =[float(value) for value in df[col].tolist()[1:]]


        return data





