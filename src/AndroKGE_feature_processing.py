import os
import shutil
import AndroKGE_utils
import networkx as nx

# Configuration:
# Features to be processed from the JSON object separated into two feature groups
# Depends on the keys available in the JSON object provided by decompilation container

APK_FEATURES = ["Opcodes", "API calls", "API packages", "System commands"]      # Strings ommited - optional choice
APK_ActSerRec = ["Activities", "Services", "Receivers"]                         # Features to be processed


class FeatureProcessor:
    """
    Processes application features from JSON files to construct network graphs representing the relationships
    and dependencies among the features.

    This class supports the construction of both a comprehensive graph including all processed features
    and individual graphs for each application's features. It also handles the storage of these graphs
    and their corresponding feature lists in specified directories.

    Attributes:
        extracted_features (str): Directory where extracted features are stored.
        dataset_graph (str): Path where the full dataset graph should be saved.
        dataset_features (str): Path where the full dataset features should be saved.
        delimiter (str): Delimiter used for storing graphs in text format.
        ind_g_save_dir (str): Directory to save individual graphs.
        ind_f_save_dir (str): Directory to save individual feature lists.
        Graph (nx.Graph): NetworkX graph object to hold the comprehensive graph of all features.
        feature_list (list): List to store all feature nodes added to the Graph.

    Methods:
        prepare_directories(): Ensures that output directories are available and clean for storing graphs and features.
        add_features(): Adds a feature to the comprehensive and individual graphs and records it in the respective lists.
        crawl_and_sort_features(): Processes and categorizes features from JSON, updating graph structures.
        get_graph(): Returns the comprehensive graph constructed from all processed features.
        create_graph(): Initiates the processing of feature files to construct and save graphs and feature lists.
    """
    def __init__(self, features_directory, dataset_graph, dataset_features, graph_delimiter, ind_graphs_directory,
                 ind_features_directory):
        """
                    Initializes the feature processor with all necessary paths and configurations.

                    Args:
                        features_directory (str): Directory where extracted features are stored.
                        dataset_graph (str): Path where the full dataset graph should be saved.
                        dataset_features (str): Path where the full dataset features should be saved.
                        graph_delimiter (str): Delimiter used for storing graphs in text format.
                        ind_graphs_directory (str): Directory to save individual graphs.
                        ind_features_directory (str): Directory to save individual feature lists.
        """

        self.extracted_features = features_directory
        self.dataset_graph = dataset_graph
        self.dataset_features = dataset_features
        self.delimiter = graph_delimiter
        self.ind_g_save_dir = ind_graphs_directory
        self.ind_f_save_dir = ind_features_directory
        self.Graph = nx.Graph()
        self.feature_list = []

    def prepare_directories(self):
        """
               Prepares directories for saving individual graph and feature files, ensuring they are clean and ready for new data.
        """

        # Clear and create the directory for individual graphs
        if self.ind_g_save_dir and not os.path.exists(self.ind_g_save_dir):
            shutil.rmtree(self.ind_g_save_dir, ignore_errors=True)
            os.makedirs(self.ind_g_save_dir, exist_ok=True)

        # Clear and create the directory for individual features
        if self.ind_f_save_dir and not os.path.exists(self.ind_f_save_dir):
            shutil.rmtree(self.ind_f_save_dir, ignore_errors=True)
            os.makedirs(self.ind_f_save_dir, exist_ok=True)

    @staticmethod
    def add_features(graph, individual_graph, feature_list, individual_feat_list, root_node, value):
        """
         Adds features to both the main and individual graphs, and records them in the respective feature lists.

         Args:
             graph (nx.Graph): The main graph being constructed for all data.
             individual_graph (nx.Graph): Graph specific to the current JSON object being processed.
             feature_list (list): List of features added to the main graph.
             individual_feat_list (list): List of features specific to the individual graph.
             root_node (str): The root node identifier in the graph.
             value (str): Feature value to add to the graph and lists.

         """

        graph.add_edge(value, root_node)
        individual_graph.add_edge(value, root_node)
        feature_list.append(value)
        individual_feat_list.append(value)
        return

    def crawl_and_sort_features(self, graph, application_features, feature_list):
        """
                Processes application features from JSON and updates the graph structures accordingly.

                Args:
                    graph (nx.Graph): The main graph to which features will be added.
                    application_features (dict): Parsed JSON structure containing all the features.
                    feature_list (list): List to store all the feature nodes added to the graph.

                Returns:
                    tuple: Contains the individual graph, feature list for this graph, and root node identifier.
        """

        # variables for storing individual graph and feature list, per analysed application
        individual_graph = nx.Graph()
        individual_feat_list = []

        root_node = None

        # Process each feature category from the JSON object
        for first_level_key in application_features.keys():
            if first_level_key == "Pre_static_analysis":
                # Set the root node representing the APK to be HASH SHA256
                root_node = str(application_features[first_level_key]["sha256"])
                graph.add_node(root_node)
                individual_graph.add_node(root_node)

                # Add the SHA1 hash as a feature subnode to the root node
                sha1_hash = str(application_features[first_level_key]["sha1"])
                self.add_features(graph, individual_graph, feature_list, individual_feat_list, root_node, sha1_hash)

            else:
                if first_level_key == "Static_analysis":

                    # Package name node
                    package_name = str(application_features[first_level_key]["Package name"])
                    self.add_features(graph, individual_graph, feature_list, individual_feat_list, root_node,
                                      package_name)

                    # Main activity node stripped of package name
                    main_activity = str(application_features[first_level_key]["Main activity"]).split(".")[-1]
                    self.add_features(graph, individual_graph, feature_list, individual_feat_list, root_node,
                                      main_activity)

                    # Add permissions as edges to the root node
                    for permission in application_features[first_level_key]["Permissions"]:
                        permission = str(permission)
                        self.add_features(graph, individual_graph, feature_list, individual_feat_list, root_node,
                                          permission)

                    # Iterate over various application feature elements defined in the configuration of this file to add them into the graph as nodes.
                    for second_level_key in APK_FEATURES:
                        if second_level_key == "Strings":
                            prep = "STR-"
                        else:
                            prep = ""
                        for key in application_features[first_level_key][second_level_key].keys():
                            key = prep + str(key)
                            self.add_features(graph, individual_graph, feature_list, individual_feat_list, root_node,
                                              key)

                    # Iterate over application activities, services, and receivers to add them into the graph as nodes.
                    for second_level_key in APK_ActSerRec:
                        for third_level_key in application_features[first_level_key][second_level_key].keys():
                            if application_features[first_level_key][second_level_key][third_level_key]:
                                third_level_key = str(third_level_key)
                                self.add_features(graph, individual_graph, feature_list, individual_feat_list,
                                                  root_node, third_level_key)

        return individual_graph, individual_feat_list, root_node

    def get_graph(self):
        """
        Returns the main graph constructed from all processed features.
        """
        return self.Graph

    def create_graph(self):
        """
        Main method to process all feature files and construct graphs based on them.
        """
        #TODO: Add tests for this method?
        self.prepare_directories()

        # Initiate the processing of all feature files from the output directory of APK decompiling container
        for feature_file in os.listdir():
            file_path = os.path.join(self.extracted_features, feature_file)
            features_json = AndroKGE_utils.JSONHandler.load_json(file_path)

            ind_graph, ind_feat_list, apk_hash = self.crawl_and_sort_features(features_json)

            # Optionally save individual graph and feature list
            if self.ind_g_save_dir:
                nx.write_edgelist(ind_graph, os.path.join(self.ind_g_save_dir, f"{apk_hash}"), delimiter=self.delimiter)
            if self.ind_f_save_dir:
                AndroKGE_utils.CSVHandler.save_list_as_csv(ind_feat_list,
                                                           os.path.join(self.ind_f_save_dir, f"{apk_hash}.csv"))

        # If the paths for the Graph and Feature files are provided, save them
        if self.dataset_graph:
            nx.write_edgelist(self.Graph, self.dataset_graph, delimiter=self.delimiter)
        if self.dataset_features:
            AndroKGE_utils.CSVHandler.save_list_as_csv(self.feature_list, self.dataset_features)