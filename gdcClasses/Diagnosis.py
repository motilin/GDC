import constants as c


class Diagnosis:

    def __init__(self, diagnosis_document, remote=False):
        self.primary_diagnosis = None
        self.tumor_grade = None
        self.tumor_stage = None
        self.biopsy_site = None
        self.prior_malignancy = None
        if remote:
            self.load_remote(diagnosis_document)
        else:
            self.deserialize(diagnosis_document)

    def get_value(self, term, diagnosis_document):
        if term in diagnosis_document.keys() and diagnosis_document[term] not in c.nullDiagnosis:
            return diagnosis_document[term]
        else:
            return None

    def load_remote(self, diagnosis_document):
        self.primary_diagnosis = self.get_value("primary_diagnosis", diagnosis_document)
        self.tumor_grade = self.get_value("tumor_grade", diagnosis_document)
        self.tumor_stage = self.get_value("tumor_stage", diagnosis_document)
        self.biopsy_site = self.get_value("site_of_resection_or_biopsy", diagnosis_document)
        self.prior_malignancy = self.get_value("prior_malignancy", diagnosis_document)

    def serialize(self):
        return self.__dict__

    def deserialize(self, diagnosis_document):
        self.primary_diagnosis = diagnosis_document["primary_diagnosis"]
        self.tumor_grade = diagnosis_document["tumor_grade"]
        self.tumor_stage = diagnosis_document["tumor_stage"]
        self.biopsy_site = diagnosis_document["biopsy_site"]
        self.prior_malignancy = diagnosis_document["prior_malignancy"]
