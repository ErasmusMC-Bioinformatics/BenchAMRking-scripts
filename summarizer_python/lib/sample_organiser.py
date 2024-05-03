import copy

import matplotlib.pyplot as plt

from defines import DATA_DIR, OUTPUT_DIR, GENES_TO_FILER, IDENTITY_CUTOFF, QUALITY_PASSED, QUALITY_FAILED
from pathlib import Path
import pandas as pd
import seaborn as sns
import csv


class SampleOrganiser:
    def __init__(self):
        self.sample_dir = self._validate_dir(Path(DATA_DIR))
        self.samples = self._load_all_samples()
        self.sample_names = sorted(self._get_sample_names())
        self.sample_types = sorted(self._get_all_sample_types())

        self.corrected_types, self.subtypes = self._get_subtypes()
        self.sample_sub_types = self._get_subtypes()
        self.organised_samples = self._organise_samples()
        self.overview_samples = self._generate_overview()

        self.identity_cutoff = IDENTITY_CUTOFF
        self._quality_failed = QUALITY_FAILED
        self._quality_passed = QUALITY_PASSED

    def _get_subtypes(self):
        """
        corrects the found types in subtyps when needed

        :return:
        """
        corrected_types = copy.deepcopy(self.sample_types)  # makes a deep copy from the sample types attribute
        subtype_dict = {}

        for sample_type in self.sample_types:
            if "_" in sample_type:  # meaning it has a subtype?

                corrected_types.remove(sample_type)  # removing from subtype list
                corrected_type, subtype = sample_type.rsplit("_", maxsplit=1)

                if corrected_type not in subtype_dict.keys():
                    corrected_types.append(corrected_type)  # adds the correct type to the list
                    subtype_dict[corrected_type] = []  # starts creating subtype dictionary

                subtype_dict[corrected_type].append(subtype)  # adds subtype to dict

        return corrected_types, subtype_dict

    def _create_data_frame(self, filter_name):
        """
        Generates a data frame dictionary by
        - getting all genes from the samples
        - filtering all samples required.
        - add all to the dict

        :param filter_name: str: what must be in the name

        """
        genes = self._get_all_genes(filter_name)

        # generate data structure
        data = {}
        for gene in genes:
            data[gene] = {}

        for sample_name, file in self.organised_samples.items():
            for sample_type, path in file.items():
                if filter_name is None and path is not None:
                    for gene, identity in self._exstract_genes_from_file(path).items():
                        if gene not in data.keys():
                            data[gene] = {}

                        data[gene][path.name] = identity
                elif str(filter_name) in (sample_name or sample_type) and path is not None:
                    for gene, identity in self._exstract_genes_from_file(path).items():
                        if gene not in data.keys():
                            data[gene] = {}

                        data[gene][path.name] = identity

        return data

    def _identity_to_binary(self, dataframe):
        """
        changes all identity
        :param dataframe:
        :return:
        """

        def threshold_function(value, treshold=self.identity_cutoff):
            return 0 if value < treshold else 1

        # Apply the threshold function to each element in the DataFrame
        return dataframe.map(lambda x: threshold_function(x, treshold=self.identity_cutoff))

    @classmethod
    def _cluster_dataframe(cls, dataframe):
        """
        Clusters the dataframe to gain more over view

        :param dataframe: panda dataframe
        :return: panda dataframe clusterd
        """
        numeric_columns = dataframe.select_dtypes(include=['int', 'float']).columns
        clustered_heatmap = sns.clustermap(dataframe[numeric_columns],
                                           method='ward', cmap='viridis', annot=True,
                                           fmt='.1f')

        # Extract row and column order from the clustered heatmap
        row_order = clustered_heatmap.dendrogram_row.reordered_ind
        col_order = clustered_heatmap.dendrogram_col.reordered_ind

        df_clustered = dataframe.iloc[row_order].iloc[:, col_order]

        return df_clustered

    def _type_samples(self, dataframe):
        """
        adds a new row called type, based on sample name
        :param dataframe: panda dataframe
        :return:
        """
        first_row_template = dict(dataframe.iloc[0].copy())
        new_frame = {}
        for element in first_row_template:
            type = element.split("_")[2:]
            type = '_'.join(type).rsplit(".")[0]
            new_frame[element] = {"type": type}

        new_data_frame = pd.DataFrame.from_dict(new_frame)
        return pd.concat([new_data_frame, dataframe])

    def _update_row_names(self, dataframe):
        """
        updates panda data frame to remove the first (something)
        :param dataframe:
        :return:
        """
        new_index = []
        for i in dataframe.index:
            if str(i).startswith('('):
                new_index.append(str(i).split(')', maxsplit=1)[1])
            else:
                new_index.append(str(i))

        dataframe.index = new_index
        return dataframe

    def create_comparison(self, sheet_name, excel_writer, filter_name=None, binary=True, cluster=True, typing=True,
                          corr=False, remove_front_parahentis=True, sort_columns=False):

        data_dict = self._create_data_frame(filter_name=filter_name)
        try:
            del data_dict['-']
        except:
            pass

        # correct to dataframe
        df = pd.DataFrame.from_dict(data_dict).transpose()
        df = df.fillna(0)

        # converts the idenity values to binary data (true / false )
        if binary:
            df = self._identity_to_binary(dataframe=df)

        if cluster:
            df = self._cluster_dataframe(dataframe=df)

        if corr:
            df = df.corr()

        # post processing adding the sub type and types?
        if typing:
            df = self._type_samples(df)

        if remove_front_parahentis:
            df = self._update_row_names(df)

        if sort_columns:
            df = df.sort_index(axis=1)
        # write out to excel
        df.to_excel(excel_writer=excel_writer,
                    sheet_name=sheet_name,
                    index=True)

    @classmethod
    def _find_delimiter(cls, filename):
        sniffer = csv.Sniffer()
        with open(filename) as fp:
            try:
                delimiter = sniffer.sniff(fp.read(5000)).delimiter
            except:
                delimiter = "\\t"

        return delimiter

    def _exstract_genes_from_file(self, file):
        """
        Estracts the genes and identities present from a csv file
        :param file: str: path to file
        :return: dict: gene: identity
        """
        df = pd.read_csv(file,
                         on_bad_lines='skip',
                         sep=self._find_delimiter(file))

        if "Locus" in list(df.columns):
            if "% Identity" in list(df.columns):
                data = (dict(zip(list(df["Locus"]), list(df["% Identity"]))))
            elif "ID" in list(df.columns):
                data = (dict(zip(list(df["Locus"]), ([self._quality_passed] * len(list(df["Locus"]))))))
            elif "Identity" in list(df.columns):
                data = (dict(zip(list(df["Locus"]), list(df["Identity"]))))
            else:
                raise NotImplemented("identity locus not implemented")


        elif '"Locus' in list(df.columns):
            data = (dict(zip(list(df['"Locus']), ([self._quality_passed] * len(list(df['"Locus']))))))

        elif "Gene symbol" in list(df.columns):
            data = (dict(zip(list(df["Gene symbol"]), list(df["% Identity to reference sequence"]))))

        elif "Allele" in list(df.columns):
            data = (dict(zip(list(df["Allele"]), list(df["% Identity"]))))

        elif "Genotype" in list(df.columns):
            status = df["Quality Module"][0]

            data = {}
            for gene in str(df["Genotype"][0]).split(","):
                if status == "Passed":
                    data[gene] = self._quality_passed
                elif status == "Failed":
                    data[gene] = self._quality_failed
                else:
                    raise NotImplemented(status)

        elif "Best_Hit_ARO" in list(df.columns):
            data = (dict(zip(list(df["Best_Hit_ARO"]), list(df["Best_Identities"]))))

        elif "Gene" in list(df.columns):
            data = (dict(zip(list(df["Gene"]), list(df["%Identity"]))))

        else:
            raise ValueError(f"Correct column names not found in {file}"
                             f"{df.columns}")

        return data

    def _get_all_genes(self, filter_name):
        """
        Retrieves the genes from all files

        :return:
        """
        gene_list = []
        for sample_name, data in self.organised_samples.items():
            for sub_type, file in data.items():

                if filter_name is not None:
                    if filter_name not in sub_type:
                        continue

                if file is not None:
                    genes = self._exstract_genes_from_file(file)

                    gene_list.extend(genes.keys())

        # only unique values
        gene_list = list(set(gene_list))
        # filter values
        for item in GENES_TO_FILER:
            try:
                gene_list.remove(item)
            except ValueError:
                pass

        return gene_list

    def write_out_sample_overview(self):
        """
        Writes out the overview of samples to an Excel page
        :return:
        """
        file_name = Path.joinpath(OUTPUT_DIR / Path('overview_samples.xlsx'))
        self._create_directory(file_name)

        if file_name.exists():
            file_name.unlink()  # deletes file if it exists

        with pd.ExcelWriter(file_name) as excel_writer:
            self.overview_samples.to_excel(excel_writer,
                                           sheet_name="overview samples",
                                           index=True)

    @classmethod
    def _create_directory(cls, pathname):
        """
        Creates all needed directory of pathname
        :param pathname: Path object
        :return: NA
        """

        pathname.parent.mkdir(parents=True, exist_ok=True)

    def _generate_overview(self):

        df = pd.DataFrame(self.organised_samples)  # convert to data frame
        # convert to binary
        binary_dict = {col: {idx: 1 if pd.notna(value) else 0 for idx, value in df[col].items()} for col in df.columns}

        # add column of sum
        binary_dict["sum"] = {}
        for sample_type in self.sample_types:
            binary_dict["sum"][sample_type] = 0

        # adding values
        for sample, data in binary_dict.items():

            if sample == "sum":  # we do not need the sum we already calculated
                continue
            for sample_type, value in data.items():
                binary_dict["sum"][sample_type] += value

        # sorting values
        dataframe = pd.DataFrame(binary_dict)
        dataframe_sorted = dataframe.sort_values(by="sum", ascending=False)

        return dataframe_sorted

    @classmethod
    def _validate_dir(cls, path):
        """
        Validates if a path exists

        :return path: Path object
        """

        if not Path.is_dir(path):
            raise FileNotFoundError
        return path

    def _load_all_samples(self):
        """
        Retrieves all file paths and check if it is a file
        :return: list: file_path

        """
        file_filtered = []
        files = list(self.sample_dir.rglob('*'))
        for file in files:
            if file.is_file():  # we do  not need any directory's
                file_filtered.append(file)

        return file_filtered

    def _get_sample_names(self):
        sample_names = []
        for sample in self.samples:
            sample_names.append(self._extract_sample_name(sample))

        return list(set(sample_names))

    @classmethod
    def _extract_sample_name(cls, sample):
        """
        Extracts the sample name,
        Eq SRX6855211_SRR10127028

        :param sample: Path, sample
        :return:
        """
        name_parts = sample.name.split("_")
        return f"{name_parts[0]}_{name_parts[1]}"

    def _organise_samples(self):
        """
        organises the sample paths based on sample name and sample type

        :return: dict, {[sample_name][type]: path
        """

        data_dict = {}

        for sample in self.sample_names:
            data_dict[sample] = {}
            for sample_type in self.sample_types:
                data_dict[sample][sample_type] = None

        for sample in self.samples:
            sample_name = self._extract_sample_name(sample)
            sample_type = self._get_sample_type(sample.name, sample_name)

            data_dict[sample_name][sample_type] = sample

        return data_dict

    @classmethod
    def _get_sample_type(cls, sample, sample_name):
        """
        retrieves the sample type.
        uses the sample name to filter correctly
        :param sample: name of sample (path.name)
        :param sample_name: first name of the sample
        :return:
        """
        return sample.replace(sample_name, '')[1:].split(".")[0]

    def _get_all_sample_types(self):
        """
        retrieves the sample type

        :return: list, all sample types in data set
        """
        sample_types = []
        for sample in self.samples:
            sample_name = self._extract_sample_name(sample)
            sample_type = self._get_sample_type(sample.name, sample_name)
            # removing sample name and extension
            sample_types.append(sample_type)

        return list(set(sample_types))
