import sys

import requests
import json
import re
import os
import glob
import pandas as pd
import constants as c
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pymongo
from pymongo import MongoClient

SIZE = 10000
WIDTH = 0.2 ## the width of the barplot bar

def connectToDatabase():
    client = MongoClient('localhost')
    db = client.gdc
    return db

## downloads GDC data based on two search terms that appear in the file name ##
def getTable(q1, q2):

    endpt = 'https://api.gdc.cancer.gov/files'

    fields = [
            "file_name",
            "file_id",
            "cases.case_id"
            ]

    fields = ','.join(fields)

    filters = {
            "op": "and",
            "content": [
                {
                    "op": "=",
                    "content": {
                        "field": "file_name",
                        "value": "*" + q1 + "*"
                        }
                    },
                {
                    "op": "=",
                    "content": {
                        "field": "file_name",
                        "value": "*" + q2 + "*"
                        }
                    }
                ]
            }

    params = {
            "filters": json.dumps(filters),
            "fields": fields,
            "format": "JSON",
            "size": "1000"
            }

    response = requests.get(endpt, params = params)

    #print(json.dumps(response.json(), indent = 2))

    result = json.loads(response.content)["data"]["hits"]
    cases = [y["case_id"] for x in result for y in x["cases"]]
    print("\nsearch terms: " + q1 + " and " + q2)
    print("total number of cases: " + str(len(set(cases))))

    file_uuid_list = []

    for file_entry in result:
        file_uuid_list.append(file_entry["file_id"])

    endpt = 'https://api.gdc.cancer.gov/data'

    params = {
            "ids": file_uuid_list
            }

    response = requests.post(endpt, data = json.dumps(params), headers = {"Content-Type": "application/json"})

    response_head_cd = response.headers["Content-Disposition"]

    file_name = re.findall("filename=(.+)", response_head_cd)[0]

    with open(file_name, "wb") as output_file:
        output_file.write(response.content)

    dir_name = file_name.split(".")[0] + "_" + file_name.split(".")[1]

    if not os.path.isdir("./downloads"):
        os.system("mkdir downloads")

    targetDir = "./downloads/" + dir_name + "/"

    os.system("mkdir " + targetDir)
    os.system("mv ./" + file_name + " " + targetDir)

    os.system("tar xvzf " + targetDir + file_name + " -C " + targetDir)

    directories = [name for name in os.listdir(targetDir) if os.path.isdir(targetDir + name)]
    tableFiles = glob.glob(targetDir + "/*/" + "/*.txt")
    table = pd.read_csv(tableFiles[0], sep = "\t", header = 1)
    table = table.drop([0], axis = 0)

    for newTableFile in tableFiles[1:]:
        newTable = pd.read_csv(newTableFile, sep = "\t", header = 1)
        newTable = newTable.drop([0], axis = 0)
        table = pd.concat([table, newTable])

    return table

## parses a string of drug names (as appear in uptodate) into a list ##
def getDrugNames(drugNamesString):
    names = drugNamesString.split(";")
    r = re.compile("(.+) \(.*\)")
    names = [r.match(x).group(1).lower().strip() for x in names]
    return names

## returns a dictionary of someName:genericName for the drugs that appear in drugFile ##
def getDrugs(drugsFile):
    os.system("mv " + drugsFile + " " + drugsFile + ".tmp")
    os.system("tr A-Z a-z < " + drugsFile + ".tmp > " + drugsFile)

    with open(drugsFile) as d:
        drugStrings = json.load(d)

    drugLists = dict()
    for drug in drugStrings.keys():
        drugLists[drug] = getDrugNames(drugStrings[drug])

    drugs = dict()
    for key in drugLists.keys():
        for value in drugLists[key]:
            if value in drugs.keys() and drugs[value] != key:
                print(value + " appears more than once")
                sys.exit("value duplication in drugs file")
            drugs[value] = key

    return drugs

## maps the measure of response field to a numeric value ##
def mapResponse(response):
    if pd.isna(response):
        return 0
    else:
        return c.measureOfResponse[response]

## returns a table with patients that received a mono therapy ## here missing of response is not removed
def getMonoTable(drugsTable):
    mono = []
    for patient in drugsTable.groupby("bcr_patient_uuid"):
        if (patient[1]["drug_name"].unique().shape[0] == 1) and \
        (patient[1]["drug_name"].tolist()[0] not in c.nullDrugs) and \
        (not any(patient[1]["drug_name"].isna())):
            mono.append(patient[0])
    return drugsTable[drugsTable["bcr_patient_uuid"].isin(mono)]

### returns a table with patients that received a mono therapy ##
#def getMonoTable(drugsTable):
#    mono = []
#    for patient in drugsTable.groupby("bcr_patient_uuid"):
#        if (patient[1]["drug_name"].unique().shape[0] == 1) and \
#        (all(patient[1]["measure_of_response"].map(mapResponse) != 0)) and \
#        (patient[1]["drug_name"].tolist()[0] not in c.nullDrugs) and \
#        (not any(patient[1]["drug_name"].isna())):
#            mono.append(patient[0])
#    return drugsTable[drugsTable["bcr_patient_uuid"].isin(mono)]

## returns a dictionary with list of tubles of (patient uuid, responses [in numbers]) for each drug ##
def getResponse(drugsTable):
    response = dict()
    for patient in drugsTable.groupby("bcr_patient_uuid"):
        for drug in patient[1].groupby("drug_name"):
            if drug[0] in c.nullDrugs:
                continue
            value = drug[1]["measure_of_response"].map(mapResponse).tolist()
            if 0 in value and np.sum(value) != 0:
                value = 0
            else:
                value = np.mean(value)
            if drug[0] in response.keys():
                response[drug[0]].append((patient[0],value))
            else:
                response[drug[0]] = [(patient[0],value)]
    return response

## summarizes a response dictionary received from getResponse method ##
def summarizeResponse(response):
    columns = ["unknown", "complete response", "partial response", "stable disease", "clinical progressive disease"]
    columns = c.responses
    summary = pd.DataFrame(index = response.keys(), columns = columns)
    for key in response:
        summary.at[key, c.responses[0]] = [p for p, v in response[key] if v == 0]
        summary.at[key, c.responses[1]] = [p for p, v in response[key] if (0 < v) and (v <= 1)]
        summary.at[key, c.responses[2]] = [p for p, v in response[key] if (1 < v) and (v <= 2)]
        summary.at[key, c.responses[3]] = [p for p, v in response[key] if (2 < v) and (v <= 3)]
        summary.at[key, c.responses[4]] = [p for p, v in response[key] if (3 < v) and (v <= 4)]
    return summary

## counts the number of cases in each cell of summarizeResponse and sorts according to the sum ##
def tablizeResponseSummaryAll(summary):
    summary = summary.copy().applymap(lambda x : len(x))
    summary["known total"] = summary[c.responses[1:]].sum(1)
    summary = summary.sort_values(by = "known total", ascending = False)
    return summary

## counts the number of cases in each cell of summarizeResponse that have dataType and sorts according to the sum ##
def tablizeResponseSummaryWithDataType(summary, dataType, fileData):
    summary = summary.copy().applymap(lambda caseList : sum(isDataTypeInCase(dataType, caseList, fileData)))
    summary["known total"] = summary[c.responses[1:]].sum(1)
    summary = summary.sort_values(by = "known total", ascending = False)
    return summary

## returns a list of size s, from point f, of the files in gdc ##
def getFileDataHelper(f, s):

    endpt = 'https://api.gdc.cancer.gov/files'

    fields = [
            "origin",
            "type",
            "file_name",
            "file_id",
            "created_datetime",
            "updated_datetime",
            "data_format",
            "data_type",
            "experimental_strategy",
            "submitter_id",
            "center.name",
            "cases.case_id",
            "cases.samples.sample_id",
            "cases.samples.annotations.notes",
            "cases.samples.sample_type",
            "cases.samples.created_datetime",
            "cases.samples.tissue_type",
            "cases.samples.tumor_descriptor",
            "cases.samples.annotations.entity_type",
            "cases.samples.annotations.notes",
            "analysis.workflow_type",
            "analysis.input_files.file_id",
            "analysis.input_files.data_type",
            "downstream_analyses.output_files.data_category",
            "downstream_analyses.output_files.data_format",
            "downstream_analyses.output_files.data_type",
            "downstream_analyses.output_files.experimental_strategy"
            ]

    fields = ','.join(fields)

    params = {
            "fields": fields,
            "format": "JSON",
            "from": str(f),
            "size": str(s)
            }

    response = requests.get(endpt, params = params)

    result = json.loads(response.content)["data"]["hits"]
    print("files: downloaded " + str(len(result)) + " items")

    return result

## returns a dictionary of all the cases in gdc. The values are the files related to the cases ##
def getFilesCollection():
    db = connectToDatabase()
    db.drop_collection("files")
    filesCollection = db.files
    f = 0
    result = ["init"]
    while len(result) != 0:
        result = getFileDataHelper(f, SIZE)
        f += SIZE
        try:
            filesCollection.insert_many(result)
        except TypeError as error:
            print("files: end")
    return filesCollection

def readFilesCollection():
    db = connectToDatabase()
    return db.files

## reading a json into a dictionary ##
def readJson(fileName):
    with open(fileName) as f:
        data = json.load(f)
    return data

## writing a json into a dictionary ##
def writeJson(data, fileName):
    with open(fileName, "w") as f:
        json.dump(data, fileName)
    print(fileName + " saved")

## attach a text label above each bar in *rects*, displaying its height ##
def autolabel(ax, rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    return

## for each of the cases in casesList, returns True if it has a file of type dataType and False otherwise ##
def isDataTypeInCase(dataType, caseList, fileData):
    result = []
    for case in caseList:
        result.append(dataType in [f["data_type"] for f in fileData[case]])
    return result

## barplots the first n drugs from the drugSummary format ##
def plotDrugSummary(tableDrugSummary, n):
    labels = tableDrugSummary.index[0:n]
    x = np.arange(len(labels))  # the label locations
    fig, ax = plt.subplots()
    rects = []
    for i in range(4):
        rects.append(ax.bar(x + (i - 1.5) * WIDTH, tableDrugSummary.iloc[0:n, i + 1], WIDTH, label = tableDrugSummary.columns[i + 1]))
        autolabel(ax, rects[i])
    ax.set_ylabel('# patients')
    ax.set_title('The effects of the most common drugs')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()
    plt.show()

## barplots the first n drugs from the drugSummary format ##
def plotDrugSummaryWithDataType(tableDrugResponse, fileType, n, fileData):
    totalTable = tablizeResponseSummaryAll(tableDrugResponse)
    withTypeTable = tablizeResponseSummaryWithDataType(tableDrugResponse, fileType, fileData).reindex(totalTable.index)
    labels = totalTable.columns[1:5]
    drugs = totalTable.index[0:n]
    xs = np.arange(n)
    fig, ax = plt.subplots()
    rects = []
    for i in range(4):
        nTotal = totalTable.iloc[0:n, i + 1]
        nWithType = withTypeTable.iloc[0:n, i + 1]
        x = xs + (i - 1.5) * WIDTH
        rects.append(ax.bar(x, nWithType, WIDTH, label = labels[i], color = c.drugsWithTypeColors[i][0]))
        rects.append(ax.bar(x, nTotal - nWithType, WIDTH, label = labels[i] + " (no file)", bottom = nWithType, color = c.drugsWithTypeColors[i][1]))
        for loc in zip(x, zip(nTotal, nWithType)):
            ax.text(loc[0], loc[1][0] + 5, str(loc[1][1]) + "\nof\n" + str(loc[1][0]), horizontalalignment='center')
    ax.set_ylabel('# patients')
    ax.set_title('Cases with \"' + fileType + '\" files')
    ax.set_xticks(xs)
    ax.set_xticklabels(drugs)
    ax.legend()

    fig.tight_layout()
    plt.show()
