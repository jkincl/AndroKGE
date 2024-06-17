import os
import shutil
from concurrent.futures import ProcessPoolExecutor
import docker
from docker.errors import APIError, DockerException, ImageNotFound

# Configuration
DOCKER_IMAGE = "alexmyg/andropytool"
DOCKER_COMMAND = "-s /apks/ -f"



class FeatureExtractor:

    # Can you write class description here?
    def __init__(self, directory_path, workers_ratio):
        self.directory_path = directory_path
        self.n_workers = workers_ratio
        self.root_part = os.path.dirname(directory_path)
        self.feature_folder = os.path.join(self.root_part, "features")
        self.tmp_folder_base = os.path.join(self.root_part, "tmp")
        self.prepare_folders()

    def prepare_folders(self):
        os.makedirs(self.feature_folder, exist_ok=True)
        os.makedirs(self.tmp_folder_base, exist_ok=True)

    def ensure_docker_running(self):
        try:
            client = docker.from_env()
            return client
        except DockerException:
            print("Docker is not running. Please start Docker and try again.")
            return None

    def pull_image(self, client, image_name):
        try:
            print(f"Checking for Docker image {image_name}...")
            client.images.get(image_name)
            print("Image found locally.")
        except ImageNotFound:
            print("Image not found locally. Pulling from Docker Hub...")
            client.images.pull(image_name)
            print("Image pulled successfully.")

    def run_container(self, client, image, command, volume_mapping):
        try:
            print("Running container...")
            container = client.containers.run(
                image,
                command,
                volumes=volume_mapping,
                auto_remove=True,
                detach=True
            )
            container.wait()
            # logs = container.logs()
            # print("Container logs:\n", logs.decode())
            return True
        except APIError as e:
            print(f"API error: {e}")
            return False

    def process_apk(self, file_path, tmp_folder, output_folder):

        client = self.ensure_docker_running()

        if os.path.exists(file_path):
            shutil.copy(file_path, tmp_folder)
        else:
            return False

        tmp_folder = os.path.abspath(tmp_folder)
        volume_mapping = {tmp_folder: {'bind': '/apks/', 'mode': 'rw'}}
        success = self.run_container(client, DOCKER_IMAGE, DOCKER_COMMAND, volume_mapping)

        if success:
            analysis_file_path = os.path.join(tmp_folder, "Features_files")
            for file in os.listdir(analysis_file_path):
                if "analysis.json" in file:
                    shutil.copy(os.path.join(analysis_file_path, file), output_folder)

        shutil.rmtree(tmp_folder)
        return success

    def extract_features(self):
        num_workers = int(self.n_workers)
        client = self.ensure_docker_running()
        if client is not None:
            print("Docker is running.")
            self.pull_image(client, DOCKER_IMAGE)
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = []
                for apk_number, filename in enumerate(os.listdir(self.directory_path)):
                    file_path = os.path.join(self.directory_path, filename)
                    tmp_folder = os.path.join(self.tmp_folder_base, f"tmp{apk_number}")
                    os.makedirs(tmp_folder, exist_ok=True)
                    future = executor.submit(self.process_apk, file_path, tmp_folder, self.feature_folder)
                    futures.append(future)

                for future in futures:
                    if not future.result():
                        print("ERROR! - APK was not processed")
        shutil.rmtree(self.tmp_folder_base)
