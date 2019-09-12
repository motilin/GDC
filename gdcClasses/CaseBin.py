from gdcClasses.Case import Case
import numpy as np
import pandas as pd
import helpergdc as hg


class CaseBin:

    def __init__(self, connection):
        self.cases = []
        self.caseCollection = connection.get().local
        self.case_ids = self.get_ids()

    def get_ids(self, query={}):
        ids = set()
        for caseDocument in self.caseCollection.find(query):
            ids.add(caseDocument["_id"])
        return ids

    def update(self, ids):
        self.case_ids = self.case_ids.intersection(set(ids))

    def case_list(self, case_list):
        self.update(case_list)
        return self

    def shape(self):
        return len(self.case_ids)

    def drug(self, drug_name):
        query = dict()
        query["drugs.name"] = drug_name
        self.update(self.get_ids(query))
        return self

    def drugs(self, drug_names):
        query = dict()
        query["drugs.name"] = dict()
        query["drugs.name"]["$in"] = drug_names
        self.update(self.get_ids(query))
        return self

    def response(self, numeric_response):
        query = dict()
        query["drugs"] = dict()
        query["drugs"]["$elemMatch"] = self.query_response(numeric_response)
        self.update(self.get_ids(query))
        return self

    def drug_and_response(self, drug_name, numeric_response):
        cond1 = dict()
        cond1["name"] = drug_name
        cond2 = self.query_response(numeric_response)

        query = dict()
        query["drugs"] = dict()
        query["drugs"]["$elemMatch"] = dict()
        query["drugs"]["$elemMatch"]["$and"] = [cond1, cond2]

        self.update(self.get_ids(query))
        return self

    def drugs_with_response(self, drug_names):
        cond1 = dict()
        cond1["name"] = dict()
        cond1["name"]["$in"] = drug_names
        cond2 = dict()
        cond2["numeric_response"] = dict()
        cond2["numeric_response"]["$ne"] = 0

        query = dict()
        query["drugs"] = dict()
        query["drugs"]["$elemMatch"] = dict()
        query["drugs"]["$elemMatch"]["$and"] = [cond1, cond2]

        self.update(self.get_ids(query))
        return self

    def data_type(self, data_type):
        query = dict()
        query["files.data_type"] = data_type
        self.update(self.get_ids(query))
        return self

    @staticmethod
    def query_response(numeric_response):
        cond = dict()
        if numeric_response == 0:
            cond["numeric_response"] = 0
        elif numeric_response <= 4:
            nr = np.floor(numeric_response)
            cond["$and"] = [{"numeric_response": {"$gt": nr}}, {"numeric_response": {"$lte": nr + 1}}]
        else:
            raise ValueError("numeric response should be in the range of 0 to 4")
        return cond

    def get(self):
        query = dict()
        query["_id"] = dict()
        query["_id"]["$in"] = list(self.case_ids)
        cur = self.caseCollection.find(query)
        self.cases = []
        for caseDocument in cur:
            self.cases.append(Case(caseDocument))
        return self

    def get_file_frequency_table(self, drug_list, data_type):
        table = pd.DataFrame(0, index=drug_list, columns=list(range(5)))
        for case in self.cases:
            registered = False
            for file in case.files:
                if not registered and file.data_type == data_type:
                    for drug in case.drugs:
                        if drug.name in drug_list:
                            table.loc[drug.name, hg.roundResponse(drug.numeric_response)] += 1
                    registered = True
        return table
