from .Drug import Drug
from .File import File
from .Diagnosis import Diagnosis


class Case:

    def __init__(self, caseDocument, remote=False):
        self.case_id = None
        self.diagnoses = set()
        self.files = []
        self.drugs = []
        if remote:
            self.load_remote(caseDocument)
        else:
            self.deserialize(caseDocument)

    def load_remote(self, caseDocument):
        if "case_id" in caseDocument.keys():
            self.case_id = caseDocument["case_id"]
        else:
            raise LookupError("missing case_id")
        if "diagnoses" in caseDocument.keys():
            for diagnosisDocument in caseDocument["diagnoses"]:
                diagnosis = Diagnosis(diagnosisDocument, remote=True)
                self.addDiagnosis(diagnosis)
        if "files" in caseDocument.keys():
            for fileDocument in caseDocument["files"]:
                file = File(fileDocument, remote=True)
                if not self.addFile(file):
                    raise LookupError("file_id duplication")

    def serialize(self):
        case = dict()
        case["case_id"] = self.case_id
        case["diagnoses"] = [diagnosis.serialize() for diagnosis in self.diagnoses]
        case["files"] = [file.serialize() for file in self.files]
        case["drugs"] = [drug.serialize() for drug in self.drugs]
        return case

    def deserialize(self, caseDocument):
        self.case_id = caseDocument["case_id"]
        self.diagnoses = set([Diagnosis(diagnosisDocument) for diagnosisDocument in caseDocument["diagnoses"]])
        self.files = [File(fileDocument) for fileDocument in caseDocument["files"]]
        self.drugs = [Drug(drugDocument) for drugDocument in caseDocument["drugs"]]

    def save(self, connection):
        casesCollection = connection.get().local

    def addClinicalDrugData(self, clinicalDrugTable):
        patientDrugTable = clinicalDrugTable[clinicalDrugTable["bcr_patient_uuid"] == self.case_id]
        for row in patientDrugTable.iterrows():
            self.addDrug(Drug(row, remote=True))

    def addDiagnosis(self, diagnosis):
        self.diagnoses.add(diagnosis)

    def addFile(self, file):
        if file.file_id in [file.file_id for file in self.files]:
            return False
        else:
            self.files.append(file)
            return True

    def getDrug(self, drug_name):
        exist_drug_names = [drug.name for drug in self.drugs]
        if drug_name in exist_drug_names:
            drug = self.drugs[exist_drug_names.index(drug_name)]
            return drug
        else:
            return None

    def addDrug(self, drug):
        exist_drug = self.getDrug(drug.name)
        if exist_drug is None:
            self.drugs.append(drug)
        else:
            exist_drug.merge(drug)


