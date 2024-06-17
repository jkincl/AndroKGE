import os
import shutil

import APK_utils
import networkx as nx





def process_features(directory_path, pth_to_edgelist="", pth_to_feat_list="", delimiter="~_~_~", ind_g_save_dir="", ind_f_save_dir=""):
    """
       Generate a graph from features stored in JSON files within the specified directory or directories,
       and extract and store the features as CSV files.

       Parameters:
           directory_path (str or list):
               Path to the directory or a list of directories containing the JSON files.
           pth_to_edgelist (str):
               Optional. Path to save the generated graph as an edgelist file.
           pth_to_feat_list (str):
               Optional. Path to save the generated feature list as a CSV file.
           delimiter (str):
               Optional. Delimiter to use when saving the graph as an edgelist file.
           ind_g_save_dir (str):
               Optional. Path to the directory where individual app graphs will be saved as edgelist files.
           ind_f_save_dir (str):
               Optional. Path to the directory where individual feature lists will be saved as CSV files.

       Returns:
           networkx.Graph:
               The generated graph.

       Note:
           - If `pth_to_edgelist` is provided, the graph will be saved as an edgelist file at the specified path
             using the specified delimiter.
           - If `pth_to_feat_list` is provided, the feature list will be saved as a CSV file at the specified path.
           - If `ind_g_save_dir` is provided, individual app graphs will be saved as edgelist files in the specified directory.
           - If `ind_f_save_dir` is provided, individual feature lists will be saved as CSV files in the specified directory.
       """

    # ==============local function declaration==================
    def crawl_and_sort_features(graph, feature_list, json):
        """
            Extract and process features from a JSON object and add them to a given graph.

            Parameters:
                graph (networkx.Graph):
                    The graph to which the features will be added.
                feature_list (list):
                    The list to which the features will be appended.
                json (dict):
                    The JSON object containing the features.

            Returns:
                tuple:
                    A tuple containing the updated graph, the updated feature list, the individual app graph with the added features,
                    the individual feature list, and the root node value.
                    - The first graph contains all the features from processed applications.
                    - The feature list contains all the features appended during processing.
                    - The second graph represents the features of the individual app extracted from the JSON object.
                    - The individual feature list contains the features extracted from the JSON object.
                    - The root node of the individual app graph is provided in the tuple for future reference.
            """

        # Create a new graph to store individual JSON values and an individual list
        individual_graph = nx.Graph()
        individual_feat_list = []

        for fl_key in json.keys():
            if fl_key == "Pre_static_analysis":
                # Set the root node representing the APK to be HASH SHA256
                root_node = str(json[fl_key]["sha256"])

                graph.add_node(root_node)
                individual_graph.add_node(root_node)
                # ROOT node values are IGNORED as features for feature lists

                # Add the SHA1 hash as a feature subnode to the root node
                sha1_hash = str(json[fl_key]["sha1"])

                graph.add_edge(sha1_hash, root_node)
                individual_graph.add_edge(sha1_hash, root_node)

                feature_list.append(sha1_hash)
                individual_feat_list.append(sha1_hash)

            else:
                if fl_key == "Static_analysis":
                    # Package name node
                    package_name = str(json[fl_key]["Package name"])

                    graph.add_edge(package_name, root_node)
                    individual_graph.add_edge(package_name, root_node)

                    feature_list.append(package_name)
                    individual_feat_list.append(package_name)

                    # Main activity node stripped of package name
                    main_activity = str(json[fl_key]["Main activity"]).split(".")[-1]

                    graph.add_edge(main_activity, root_node)
                    individual_graph.add_edge(main_activity, root_node)

                    feature_list.append(main_activity)
                    individual_feat_list.append(main_activity)

                    # Add permissions as edges to the root node
                    for permission in json[fl_key]["Permissions"]:
                        permission = str(permission)

                        graph.add_edge(permission, root_node)
                        individual_graph.add_edge(permission, root_node)

                        feature_list.append(permission)
                        individual_feat_list.append(permission)

                    # Iterate over various keys for different features
                        #Strings REMOVED - optional choice
                    for sl_key in ["Opcodes", "API calls", "API packages", "System commands"]:
                        if sl_key == "Strings":
                            prep = "STR-"
                        else:
                            prep = ""
                        for key in json[fl_key][sl_key].keys():
                            key = prep + str(key)

                            graph.add_edge(key, root_node)
                            individual_graph.add_edge(key, root_node)

                            feature_list.append(key)
                            individual_feat_list.append(key)

                    # Add activities, services, and receivers as edges to the root node
                    for sl_key in ["Activities", "Services", "Receivers"]:
                        for tl_key in json[fl_key][sl_key].keys():
                            if json[fl_key][sl_key][tl_key] != []:
                                tl_key = str(tl_key)

                                graph.add_edge(tl_key, root_node)
                                individual_graph.add_edge(tl_key, root_node)

                                feature_list.append(tl_key)
                                individual_feat_list.append(tl_key)

                                # Add intents as edges to their corresponding activities, services, and receivers
                                for value in json[fl_key][sl_key][tl_key]:
                                    if "android.intent.action.MAIN" not in value:
                                        value = str(value)

                                        graph.add_edge(value, tl_key)
                                        individual_graph.add_edge(value, tl_key)

                                        feature_list.append(value)
                                        individual_feat_list.append(value)

        return graph, feature_list, individual_graph, individual_feat_list, root_node
    # ==============end of local function declaration==================

    # ==============function source code==============

    # Check if directory_path is a string or a list
    if isinstance(directory_path, str):
        directory_path = [directory_path]

    elif isinstance(directory_path, list):
        for i in directory_path:
            if not isinstance(i, str):
                print("Unknown parameter type. The parameter must be a string or a list of strings.")
                return
    elif not isinstance(directory_path, list):
        print("Unknown parameter type. The parameter must be a string or a list of strings.")
        return

    # Create an empty graph and empty feature list
    G = nx.Graph()
    feature_list = []

    # Remove previous content from specified directories!
    if ind_g_save_dir != "":
        if os.path.exists(ind_g_save_dir):
            shutil.rmtree(ind_g_save_dir)
        os.mkdir(ind_g_save_dir)
    if ind_f_save_dir != "":
        if os.path.exists(ind_f_save_dir):
            shutil.rmtree(ind_f_save_dir)
        os.mkdir(ind_f_save_dir)

    # Traverse through each directory and file to process the JSON files
    for directory in directory_path:
        for file in os.listdir(directory):
            processed_json = APK_utils.load_json(directory + "/" + file)
            G, feature_list, ind_graph, ind_feat_list, HASH = crawl_and_sort_features(G,feature_list, processed_json)

            # Save individual app graphs if ind_save_dir is provided
            if ind_g_save_dir != "":
                nx.write_edgelist(ind_graph, ind_g_save_dir + "/" + HASH, delimiter=delimiter)
            if ind_f_save_dir != "":
                ind_feat_list= APK_utils.get_unique_sorted_list(ind_feat_list)
                APK_utils.save_list_as_csv(ind_feat_list,ind_f_save_dir + "/" + HASH + ".csv")

    # Save the main graph as an edgelist file if pth_to_edgelist is provided
    if pth_to_edgelist != "":
        nx.write_edgelist(G, pth_to_edgelist, delimiter=delimiter)
    if pth_to_feat_list != "":
        feature_list = APK_utils.get_unique_sorted_list(feature_list)
        APK_utils.save_list_as_csv(feature_list, pth_to_feat_list)
    else:
        # Return the generated graph
        return G
