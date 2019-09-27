import constants as c
import pandas as pd
import numpy as np
import copy
import helpergdc as hg
from .ClinicalSupplementXML import ClinicalSupplementXML
import datetime
from .Document import Document


class Drug:

    def __init__(self):
        self.name = None
        self.id = None
        self.response = None
        self.numeric_response = 0
        self.regimen_number = None
        self.total_dose = None
        self.total_dose_units = None
        self.prescribed_dose = None
        self.prescribed_dose_units = None
        self.number_of_cycles = None
        self.days_to_drug_therapy_start = None
        self.days_to_drug_therapy_end = None
        self.regimen_indication = None
        self.regimen_indication_notes = None
        self.therapy_ongoing = None
        self.form_completion_date = None

    def __eq__(self, other):
        if not isinstance(other, Drug) or self.serialize() != other.serialize():
            return False
        else:
            return True

    @staticmethod
    def load_clinical_supplement(clinical_supplement_xml: ClinicalSupplementXML):

        if ('drug_name' in clinical_supplement_xml.values.keys()) and \
                (clinical_supplement_xml.values['drug_name'] is not None):
            drug_names = clinical_supplement_xml.values['drug_name']
            if type(drug_names) == list:
                number_of_drugs = len(clinical_supplement_xml.values['drug_name'])
            elif type(drug_names) == str:
                number_of_drugs = 1
            else:
                raise TypeError('drug names must be a string or a list')
        else:
            return None

        values = Document(clinical_supplement_xml.values)
        for i in range(number_of_drugs):
            drug = Drug()
            drug.name = values.get('drug_name', str)
            drug.id = values.get('drug_id', str)
            drug.response = values.get('measure_of_response', str)
            drug.regimen_number = values.get('regimen_number', int)
            drug.total_dose = values.get('total_dose', int)
            drug.total_dose_units = values.get('total_dose_units', str)
            drug.prescribed_dose = values.get('prescribed_dose', int)
            drug.prescribed_dose_units = values.get('prescribed_dose_units', int)
            drug.number_of_cycles = values.get('number_of_cycles', int)
            drug.days_to_drug_therapy_start = values.get('days_to_drug_therapy_start', int)
            drug.days_to_drug_therapy_end = values.get('days_to_drug_therapy_end', int)
            drug.regimen_indication = values.get('regimen_indication', str)
            drug.regimen_indication_notes = values.get('regimen_indication_notes', str)
            drug.therapy_ongoing = values.get('therapy_ongoing', str)

            try:
                drug.form_completion_date = datetime.datetime(
                    values.get('year_of_form_completion', int),
                    values.get('month_of_form_completion', int),
                    values.get('day_of_form_completion', int),
                )
            except TypeError:
                pass
            if drug.response is None:
                drug.numeric_response = 0
            else:
                drug.numeric_response = int(c.measureOfResponse[drug.response])

            yield drug

    def serialize(self):
        drug = copy.deepcopy(self)
        return drug.__dict__

    def deserialize(self, drug_document):
        doc = Document(drug_document)
        self.name = doc.get("name", str)
        self.id = doc.get("id", str)
        self.response = doc.get("response", str)
        self.numeric_response = doc.get("numeric_response", int)
        self.regimen_number = doc.get("regimen_number", int)
        self.total_dose = doc.get("total_dose", int)
        self.total_dose_units = doc.get("total_dose_units", str)
        self.prescribed_dose = doc.get("prescribed_dose", int)
        self.prescribed_dose_units = doc.get("prescribed_dose_units", str)
        self.number_of_cycles = doc.get("number_of_cycles", int)
        self.days_to_drug_therapy_start = doc.get("days_to_drug_therapy_start", int)
        self.days_to_drug_therapy_end = doc.get("days_to_drug_therapy_end", int)
        self.regimen_indication = doc.get("regimen_indication", str)
        self.regimen_indication_notes = doc.get("regimen_indication_notes", str)
        self.therapy_ongoing = doc.get("therapy_ongoing", str)
        self.form_completion_date = doc.get("form_completion_date", datetime.datetime)

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

    def getDrugsFrequencyTable(connection):
        casesCollection = hg.readCasesCollection(connection)
        responseDict = dict()
        for cur in casesCollection.find({"drugs.0": {"$exists": True}}, {"drugs.name", "drugs.numeric_response"}):
            for drug in cur["drugs"]:
                if not drug["name"] in responseDict:
                    responseDict[drug["name"]] = np.zeros(5)
                responseDict[drug["name"]][hg.roundResponse(drug["numeric_response"])] += 1
        responseDf = pd.DataFrame(responseDict).transpose()
        responseDf["sum"] = responseDf[[1, 2, 3, 4]].sum(1)
        return responseDf.sort_values("sum", ascending=False).drop("sum", 1)
