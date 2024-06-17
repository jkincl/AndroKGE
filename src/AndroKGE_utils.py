import csv
import os.path
import pandas as pd
import requests
from concurrent.futures import ProcessPoolExecutor


class CSVHandler:
    @staticmethod
    def load_csv_to_dataframe(FilePath):
        df = pd.read_csv(FilePath)
        return df


class AndoZooDownloader:
    @staticmethod
    def parse_urls(APIkey, ApkDataframe):
        urls = []
        for row in ApkDataframe.itertuples():
            urls.append([row.sha256, "https://androzoo.uni.lu/api/download?apikey=" + APIkey + "&sha256=" + row.sha256, 0 if row.vt_detection == "0" else 1])
        return urls


    @staticmethod
    def file_download(url):
        try:
            response = requests.get(url[1], stream=True)
            response.raise_for_status()
            directory = "../data/benign/" if url[2] == 0 else "../data/malware/"
            os.makedirs(directory, exist_ok=True)

            filename = os.path.join(directory, url[0], ".apk" )
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded '{filename}' from '{url[1]}'")
            return
        except requests.RequestException as e:
            print(f"Failed to download '{url[1]}': {str(e)}")
            return

    @staticmethod
    def download_files(APIkey, nWorkers, ApkDataframe):
        with ProcessPoolExecutor(nWorkers) as executor:
            [executor.submit(AndoZooDownloader.file_download, url) for url in AndoZooDownloader.parse_urls(APIkey, ApkDataframe)]

class APIKeyLoader:
    @staticmethod
    def load_api_key(FilePath):
        with open(FilePath, 'r') as f:
            return f.read().strip()
