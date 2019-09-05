import helpergdc as hg
from gdcClasses.Connection import Connection
from gdcClasses.Case import Case

GDC_DB = Connection()

# casesCollection = hg.getCasesCollection(GDC_DB)  # download cases data
casesCollection = hg.readCasesCollection(GDC_DB)  # read cases data from local db

# clinicalDrugTable = hg.getClinicalDrugTable(casesCollection)  # download clinical_drug table
clinicalDrugTable = hg.readClinicalDrugTable() # read clinical drug table from local disk

caseDocument = casesCollection.find_one({"case_id":"d2df20d4-6704-41e6-b33d-616225bd737c"})
case = Case(caseDocument, remote=True)
case.addClinicalDrugData(clinicalDrugTable)

serializedCase = case.serialize()
caseCopy = Case(serializedCase)

# casesCollection = hg.serializeCases(filesCollection, clinicalDrugTable) # store files and clinical_drug data

# filesCollection = hg.getFilesCollection(GDC_DB)  # download file data
# filesCollection = hg.readFilesCollection(GDC_DB)   # read stored file data

# retrieve data from the GDC :
# drugTable = hg.getTable("clinical", "drug")
# drugTable.to_csv("./drugTable.csv")
# patientTable = hg.getTable("clinical", "patient")
# patientTable.to_csv("./patientTable.csv")

# drugTable = pd.read_csv("./drugTable.csv", index_col=0)

# drugTable["bcr_patient_uuid"] = drugTable["bcr_patient_uuid"].str.lower()
# drugTable["drug_name"] = drugTable["drug_name"].str.lower()
# drugTable["measure_of_response"] = drugTable["measure_of_response"].str.lower()
# drugs = hg.getDrugs("./drugs.json")
# drugTable["drug_name"] = drugTable["drug_name"].map(lambda x: drugs[x] if x in drugs.keys() else x)

'''

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

fileTypes = filesCollection.distinct("data_type")
# for fileType in fileTypes:
#     hg.plotDrugSummaryWithDataType(tableDrugResponse, fileType, 10, fileData)

'''
