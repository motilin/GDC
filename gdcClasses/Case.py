from .Drug import Drug
from .File import File
from .Diagnosis import Diagnosis
from pymongo.errors import DuplicateKeyError
from .Connection import Connection
from .Document import Document


class Case:

    def __init__(self, case_document, remote=False):
        self._id = None
        self.diagnoses = set()
        self.files = set()
        self.drugs = set()
        self.project_code = None
        self.disease_code = None
        self.gender = None
        if remote:
            self.load_remote(case_document)
        else:
            self.deserialize(case_document)

    def load_remote(self, case_document):
        if "case_id" in case_document.keys():
            self._id = case_document["case_id"]
        else:
            raise LookupError("missing case_id")
        if "diagnoses" in case_document.keys():
            for diagnosisDocument in case_document["diagnoses"]:
                diagnosis = Diagnosis(diagnosisDocument, remote=True)
                self.add_diagnosis(diagnosis)
        if "files" in case_document.keys():
            for fileDocument in case_document["files"]:
                file = File(fileDocument, remote=True)
                if not self.add_file(file):
                    raise LookupError("file_id duplication")

    def serialize(self):
        case = dict()
        case["_id"] = self._id
        case["project_code"] = self.project_code
        case["disease_code"] = self.disease_code
        case["gender"] = self.gender
        case["diagnoses"] = [diagnosis.serialize() for diagnosis in self.diagnoses]
        case["files"] = [file.serialize() for file in self.files]
        case["drugs"] = [drug.serialize() for drug in self.drugs]
        return case

    def deserialize(self, case_document):
        doc = Document(case_document)
        self._id = doc.get("_id", str)
        self.diagnoses = set([Diagnosis(diagnosisDocument) for diagnosisDocument in doc.get("diagnoses", list)])
        self.files = set([File(fileDocument) for fileDocument in doc.get("files", list)])
        self.drugs = set([Drug(drugDocument) for drugDocument in doc.get("drugs", list)])
        self.project_code = doc.get("project_code", str)
        self.disease_code = doc.get("disease_code", str)
        self.gender = doc.get("gender", str)

    def save(self, connection):
        local_cases_collection = connection.get().local
        try:
            local_cases_collection.insert_one(self.serialize())
            print("Saving case id: " + self._id)
        except DuplicateKeyError as error:
            local_cases_collection.replace_one({'_id': self._id}, self.serialize())
            print("Replacing case id: " + self._id)

    def add_clinical_drug_data(self, clinical_drug_table):
        patient_drug_table = clinical_drug_table[clinical_drug_table["bcr_patient_uuid"] == self._id]
        for row in patient_drug_table.iterrows():
            self.add_drug(Drug(row, remote=True))

    def add_diagnosis(self, diagnosis):
        self.diagnoses.add(diagnosis)

    def add_file(self, file):
        if file.file_id in [file.file_id for file in self.files]:
            return False
        else:
            self.files.append(file)
            return True

    def get_drug(self, drug_name):
        exist_drug_names = [drug.name for drug in self.drugs]
        if drug_name in exist_drug_names:
            drug = self.drugs[exist_drug_names.index(drug_name)]
            return drug
        else:
            return None

    def add_drug(self, drug):
        self.drugs.add(drug)

    def remove_drug(self, drug):
        drug = self.get_drug(drug)
        self.drugs.remove(drug)

    def get_id(self):
        return self._id

    def set_drugs(self, drug_list):
        for drug in drug_list:
            self.drugs.add(drug)

    @staticmethod
    def get_case(connection: Connection, case_id: str):
        case_collection = connection.get().local
        case_document = case_collection.find_one(case_id)
        if case_document is None:
            raise ValueError("case id not found")
        else:
            return Case(case_document)
