import csv
import os.path
import pandas as pd
import requests
from concurrent.futures import ProcessPoolExecutor
import json


class CSVHandler:
    @staticmethod
    def load_csv_to_dataframe(FilePath):
        df = pd.read_csv(FilePath)
        return df
    @staticmethod
    def save_list_as_csv(data_list, file_name, writemode='w'):
        with open(file_name, writemode, newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(data_list)

    @staticmethod
    def save_results_to_csv(filename, data):
        with open(filename, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)

    @staticmethod
    def load_csv_as_list(file_path):
        data_list = []
        with open(file_path, 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                data_list.extend(row)
        return data_list


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
class JSONHandler:
    @staticmethod
    def load_json(path_to_file):
        with open(path_to_file) as file:
            data = json.load(file)
        return data

    @staticmethod
    def saveJSON(dict, filename):
        with open(filename, 'w', encoding="utf-8") as out_file:
            json.dump(dict, out_file)

    @staticmethod
    def save_filtered_json_data(json_data, output_directory, list_data, file_name, vector_key):
        os.makedirs(output_directory, exist_ok=True)

        filtered_data = {key: value for key, value in json_data.items() if
                         ast.literal_eval(value[vector_key]) in list_data}
        output_path = os.path.join(output_directory, file_name + '.json')
        JSONHandler.saveJSON(filtered_data, output_path)

