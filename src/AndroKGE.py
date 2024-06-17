import AndroKGE_utils
import AndroKGE_APK_processing
import logging

#configuration


APK_DIRECTORY = "../data/apks2"         # Path to the directory where APK files are stored
N_WORKERS = 8                           # Number of worker processes for feature extraction
API_KEY = "../Azoo.key"                 # API key for AndroZoo

def main():

    # STEP 01 - loading APK list - loading the list should go into downloader class to not pollute the main code
    # apk_dataframe = AndroKGE_utils.CSVHandler.load_csv_to_dataframe("../data/apk_list_10k.csv")
    # AndroKGE_utils.AndoZooDownloader().download_files(AndroKGE_utils.APIKeyLoader.load_api_key(API_KEY),1, apk_dataframe)
        # Maybe a "official" downloader tool can be used and its pip package listed in requirements.txt

    # STEP 02a - APK in the processed directory should be sorted - renamed to recalculated hashes values -> create a list of APKs and merge it with the original downloaded csv list - restructure into json file
    # step a) - sort_apk, step b) - create apk list - should have class APK_prepper with methods sort_apk and create_apk_list


    # STEP 02 - extract FEATURES using ANDROPYTOOL - fully relying on ProcessPoolExecutor - changes done only by changing number of workers


    extractor = AndroKGE_APK_processing.FeatureExtractor(APK_DIRECTORY, N_WORKERS)
    extractor.extract_features()

    # STEP 03 - will be taken from older project - APK_feature_processing.py - will be used to create the graph structures - should receive configuration on the top level, so it can be easily changed

    # STEP 04 - embedding training - again configuration should be unified and results stored in Json structure. Configuration at the top level, so users can change it.

    # STEP 05 - feature vectors + PCA - taken from previous project - and it should be easily configurable

    # STEP 06 - Data classification from previous project - but - multiclass outcome, configurable list of classifiers - the json with the samples should be Hash: emb, pca, label, binary if malware or not
        # general file will have hash: features, download file will have hash and features from the original csv.

    # STEP 07 - CLI interface for configuring which steps to run, and capture possible errors in the process - like docker not running will not kill the application, but more like wait for the user to start again





if __name__ == '__main__':
    main()
