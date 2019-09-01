import pandas as pd
import helpergdc as hg

# drugTable = hg.getTable("clinical", "drug")
drugTable = pd.read_csv("./drugTable.csv", index_col=0)
# fileData = hg.getFileData()
fileData = hg.readJson("./fileData.json")
# patientTable = hg.getTable("clinical", "patient")

drugTable["bcr_patient_uuid"] = drugTable["bcr_patient_uuid"].str.lower()
drugTable["drug_name"] = drugTable["drug_name"].str.lower()
drugTable["measure_of_response"] = drugTable["measure_of_response"].str.lower()
drugs = hg.getDrugs("./drugs.json")
drugTable["drug_name"] = drugTable["drug_name"].map(lambda x: drugs[x] if x in drugs.keys() else x)
monoDrugTable = hg.getMonoTable(drugTable)

##

tableDrugResponse = hg.summarizeResponse(hg.getResponse(drugTable))
tableDrugSummary = hg.tablizeResponseSummaryAll(tableDrugResponse)

print("\ndrug table:")
print("number of patients: " + str(drugTable["bcr_patient_uuid"].unique().shape[0]))
print("number of drugs: " + str(drugTable["drug_name"].unique().shape[0]))

monoTableDrugResponse = hg.summarizeResponse(hg.getResponse(monoDrugTable))
monoTableDrugSummary = hg.tablizeResponseSummaryAll(monoTableDrugResponse)

print("\nmono therapy table:")
print("number of patients: " + str(monoDrugTable["bcr_patient_uuid"].unique().shape[0]))
print("number of drugs: " + str(monoDrugTable["drug_name"].unique().shape[0]))

fileTypes = set([file["data_type"] for case in fileData for file in fileData[case]])
for fileType in fileTypes:
    hg.plotDrugSummaryWithDataType(tableDrugResponse, fileType, 10, fileData)
