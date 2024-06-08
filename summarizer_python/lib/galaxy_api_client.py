from bioblend import galaxy
from pathlib import Path
import time


class GalaxyApi():

    def __init__(self, url: str, api_key: str) -> None:
        self._galaxy_url = url
        self._api_key = api_key

        self.galaxy_instance = galaxy.GalaxyInstance(url=url,
                                                     key=api_key)

        self._history_url = None
        self._history_id = None
        self._tool_id = None
        self._tool_name = None
        self._library_url = None
        self._library_id = None
        self._dataset_ids = None

    def run_sample(self, sample_name: str, sample_paths: list[Path]):

        self._create_history(sample_name)
        self._get_stec_pipeline_tool()

        for sample_path in sample_paths:
            self._upload_dataset_to_history(sample_path=sample_path)

        self._get_dataset_ids_in_history()

        self._run_tool(sample=sample_name)

        # except:
        #     raise Exception
        #
        # finally:
        #     self._delete_history()

    def _run_tool(self, sample: str):

        # todo here goes it wrong, for some reason dataset[1] is used twice???? and not [0]
        # todo: docs https://bioblend.readthedocs.io/en/latest/api_docs/galaxy/all.html#module-bioblend.galaxy.jobs
        input = {'section_amr': {'dbs_amr': ['resfinder', 'argannot', 'card', 'ncbi-amr', 'pointfinder']},
                 'section_input': {'detection_method': 'blast', 'read_type':
                     {'__current_case__': 0,
                      'fastq_1': {'values': [{'id': self._dataset_ids[0], 'src': 'hda'}]},
                      'fastq_2': {'values': [{'id': self._dataset_ids[1], 'src': 'hda'}]},
                      'input_type_selector': 'illumina', 'library': 'NexteraPE'}, 'sample_name': sample},

                 'section_plasmid': {'dbs_plasmid': 'plasmid'}, 'section_qc': {'kraken': 'true'},
                 'section_report': {'report_include_bam': 'false', 'report_include_fastq': 'false'},
                 'section_serotype': {'serotypefinder': 'true'},
                 'section_st': {'schemes': ['mlst-pasteur', 'mlst-warwick', 'cgmlst']},
                 'section_virulence': {'dbs_viru': 'virulence'}}

        result = self.galaxy_instance.tools.run_tool(tool_id=self._tool_id,
                                                     history_id=self._history_id,
                                                     tool_inputs=input
                                                     )

        pass

    def _upload_dataset_to_history(self, sample_path: Path):

        self.galaxy_instance.tools.upload_file(path=sample_path, history_id=self._history_id)

    def _get_dataset_ids_in_history(self):

        data_set_ids = []
        result = self.galaxy_instance.datasets.get_datasets(history_id=self._history_id)
        for dataset in result:
            data_set_ids.append(dataset['id'])

        self._dataset_ids = data_set_ids

    def _wait_jobs_status(self, list_job_ids: list[str]):

        for job in list_job_ids:
            while True:
                time.sleep(10)
                job_result = self.galaxy_instance.jobs.show_job(job_id=job)
                print(job_result)
                if job_result['state'] == 'ok':
                    break

    def _get_stec_pipeline_tool(self):
        result = self.galaxy_instance.tools.show_tool(
            tool_id='pipeline_stec_1.0')

        self._tool_id = result['id']
        self._tool_name = result['name']
        self._tool_version = result['version']

    def _create_history(self, sample_name: str, ):
        result = self.galaxy_instance.histories.create_history(name=sample_name)
        self._history_url = result['url']
        self._history_id = result['id']

    def _delete_history(self):
        result = self.galaxy_instance.histories.delete_history(history_id=self._history_id,
                                                               purge=True)
