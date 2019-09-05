import constants as c
import pandas as pd
import numpy as np
from copy import deepcopy


class Drug:

    def __init__(self, clinicalDrugData, remote=False):
        self.name = None
        self.drug_ids = set()
        self.responses = []
        self.numeric_response = 0
        if remote:
            self.load_remote(clinicalDrugData)
        else:
            self.deserialize(clinicalDrugData)

    def load_remote(self, clinicalDrugTableRow):
        drug_id = clinicalDrugTableRow[1]["bcr_drug_uuid"]
        if not self.addId(drug_id):
            raise LookupError("drug_id duplication")
        name = clinicalDrugTableRow[1]["drug_name"]
        self.setName(name)
        response = clinicalDrugTableRow[1]["measure_of_response"]
        self.addResponse(response)

    def serialize(self):
        drug = deepcopy(self)
        drug.drug_ids = list(drug.drug_ids)
        return drug.__dict__

    def deserialize(self, clinicalDrugDocument):
        self.name = clinicalDrugDocument["name"]
        self.drug_ids = set(clinicalDrugDocument["drug_ids"])
        self.responses = clinicalDrugDocument["responses"]
        self.numeric_response = float(clinicalDrugDocument["numeric_response"])

    def merge(self, new_drug):
        for drug_id in new_drug.drug_ids:
            if not self.addId(drug_id):
                raise LookupError("drug_id duplication")
        for response in new_drug.responses:
            self.addResponse(response)

    def setName(self, name):
        if name in c.nullDrugs:
            self.name = None
        else:
            self.name = name

    def addId(self, drug_id):
        if drug_id in self.drug_ids:
            return False
        else:
            self.drug_ids.add(drug_id)
            return True

    def addResponse(self, response):
        self.responses.append(response)
        self.mapResponse()

    def removeResponse(self, response):
        if response in self.responses:
            self.responses.remove(response)
            self.mapResponse()
            return True
        else:
            return False

    def mapResponse(self):
        if len(self.responses) > 0:
            num_list = []
            for response in self.responses:
                if pd.isna(response):
                    num_list.append(0)
                else:
                    num_list.append(c.measureOfResponse[response])
            self.numeric_response = np.mean(num_list)
        else:
            self.numeric_response = 0