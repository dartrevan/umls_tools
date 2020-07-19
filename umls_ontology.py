import pandas as pd


class UMLSOntology:

    def __init__(self, mrconso_path, mrsty_path, mrrel_path):
        self.mrconso = self.read_mrconso(mrconso_path)
        self.mrsty = self.read_mrsty(mrsty_path)
        self.mrrel = self.read_mrrel(mrrel_path)

    def read_mrconso(self, fpath):
        """
        :param fpath: path to to MRCONSO.RRF file
        :return: DataFrame containing definitions of the concepts and synonyms
        """
        columns = ['CUI', 'LAT', 'TS', 'LUI', 'STT', 'SUI', 'ISPREF', 'AUI', 'SAUI', 'SCUI', 'SDUI', 'SAB', 'TTY', 'CODE',
               'STR', 'SRL', 'SUPPRESS', 'CVF', 'NOCOL']
        return pd.read_csv(fpath, names=columns, sep='|', encoding='utf-8')

    def read_mrsty(self, fpath):
        """
        :param fpath: path to the MRSTY.RRF file
        :return: DataFrame containing semantic types of the concepts
        """
        columns = ['CUI', 'TUI', 'STN', 'STY', 'ATUI', 'CVF', 'NOCOL']
        return pd.read_csv(fpath, names=columns, sep='|', encoding='utf-8')

    def read_mrrel(self, fpath):
        """
        :param fpath: path to to  the MRREL.RRF file
        :return: DataFrame containing relations between concepts
        """
        columns = ['CUI1', 'AUI1', 'STYPE1', 'REL', 'CUI2', 'AUI2', 'STYPE2', 'RELA', 'RUI', 'SRUI', 'SAB', 'SL', 'RG',
                   'DIR', 'SUPPRESS', 'CVF', 'NOCOL']
        return pd.read_csv(fpath, names=columns, sep='|', encoding='utf-8')

    def synonyms(self, concept_id, ontology):
        """
        :param concept_id: concept_id
        :param ontology: ontology name
        :return: synonyms by concept_id in a specific ontology
        """
        if ontology == 'UMLS':
            return self.mrconso[self.mrconso.CUI == concept_id]
        return self.mrconso[(self.mrconso.CODE == concept_id) & (self.mrconso.SAB == ontology)]

    def get_parent_node(self, concept_id):
        """

        :param concept_id: CUI
        :return: all parent CUIS for the concept_id
        """
        self.mrrel[(self.mrrel.CUI1 == concept_id) & (self.mrrel.REL == 'PAR')].CUI2.tolist()

    def get_child_nodes(self, concept_id):
        """
        :param concept_id: CUI
        :return: all child CUIS for the concept_id
        """
        self.mrrel[(self.mrrel.CUI1 == concept_id) & (self.mrrel.REL == 'CHD')].CUI2.tolist()

    def extract_synsets(self):
        synonyms = self.mrrel[self.mrrel.REL == 'SY'][['CUI1', 'CUI2']].drop_duplicates()
        synonyms = synonyms.apply(restore_order, axis=1)
        synonyms = synonyms.values.tolist()
        join_to = 0
        join_with = 1
        while join_to != join_with:
            if has_intersection(synonyms[join_to], synonyms[join_with]):
                synonyms[join_to] = join(synonyms[join_to], synonyms[join_with])
                synonyms.pop(join_with)
            else:
                join_to = max(join_to + 1, len(synonyms) - 1)
                join_with = max(join_with + 1, len(synonyms) - 1)
        return synonyms


def has_intersection(a, b):
    idx_a = 0
    idx_b = 0
    while idx_a < len(a) and idx_b < len(b):
        if a[idx_a] == b[idx_b]:
            return True
        elif a[idx_a] < b[idx_b]:
            idx_a += 1
        else:
            idx_b += 1
    return False


def join(a, b):
    joined = set(a) | set(b)
    joined = sorted(joined)
    return list(joined)


def restore_order(row):
    if row['CUI1'] > row['CUI2']:
        row['CUI1'], row['CUI2'] = row['CUI2'], row['CUI1']
    return row