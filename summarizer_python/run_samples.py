from pathlib import Path
from lib.galaxy_api_client import GalaxyApi
import os


def organise_illumina_samples(samples:list[str]) -> dict:

    samples_organized = {}
    for sample in samples:
        tmp = sample.rsplit('_', 1)
        if tmp[0] not in samples_organized.keys():
            samples_organized[tmp[0]] = []

        samples_organized[tmp[0]].append(sample)

    return samples_organized

if __name__ == '__main__':

    apikey = 'GET YOUR APIKEY HERE'
    galaxy_server = 'https://galaxy.sciensano.be'
    path_samples_directory = Path('PATH/TO/DATA')

    organized_samples = organise_illumina_samples(os.listdir(path_samples_directory))

    galaxy_instance = GalaxyApi(url=galaxy_server,
                                api_key=apikey)

    for sample_name, sample_list in organized_samples.items():
        sample_paths = []

        for sample in sample_list:
            sample_paths.append(path_samples_directory / sample)

        galaxy_instance.run_sample(sample_name=sample_name,
                                   sample_paths=sample_paths)

        exit()