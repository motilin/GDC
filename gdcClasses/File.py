import json
from typing import List, Any
import constants as c
import datetime
from dateutil.parser import parse
import helpergdc as hg
import pandas as pd
import requests
import time
import os
import re
import glob
import copy
from .Connection import Connection
from collections import OrderedDict


class File:

    def __init__(self, file_document, remote=False):
        self.file_id = None
        self.data_type = None
        self.created_datetime = None
        self.file_name = None
        self.md5sum = None
        self.data_format = None
        self.experimental_strategy = None
        if remote:
            self.load_remote(file_document)
        else:
            self.deserialize(file_document)

    def load_remote(self, file_document):
        keys = file_document.keys()
        if "file_id" in keys:
            self.set_file_id(file_document["file_id"])
        else:
            raise LookupError("missing file_id")
        if "created_datetime" in keys:
            self.set_created_datetime(file_document["created_datetime"])
        if "data_format" in keys:
            self.set_data_format(file_document["data_format"])
        if "data_type" in keys:
            self.set_data_type(file_document["data_type"])
        if "experimental_strategy" in keys:
            self.set_experimental_strategy(file_document["experimental_strategy"])
        if "md5sum" in keys:
            self.set_md5sum(file_document["md5sum"])
        if "file_name" in keys:
            self.set_file_name(file_document["file_name"])

    def serialize(self):
        return self.__dict__

    def deserialize(self, file_document):
        self.set_file_id(file_document["file_id"])
        self.created_datetime = file_document["created_datetime"]
        self.set_data_format(file_document["data_format"])
        self.set_data_type(file_document["data_type"])
        self.set_experimental_strategy(file_document["experimental_strategy"])
        self.set_md5sum(file_document["md5sum"])
        self.set_file_name(file_document["file_name"])

    def set_file_id(self, file_id):
        self.file_id = file_id

    def set_data_type(self, data_type):
        self.data_type = data_type

    def set_created_datetime(self, created_datetime):
        self.created_datetime = datetime.datetime.combine(parse(created_datetime).date(), datetime.time.min)

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_md5sum(self, md5sum):
        self.md5sum = md5sum

    def set_data_format(self, data_format):
        self.data_format = data_format

    def set_experimental_strategy(self, experimental_strategy):
        self.experimental_strategy = experimental_strategy

    @staticmethod
    def get_file_frequency_table(connection: Connection):
        cases_collection = hg.readCasesCollection(connection)
        file_dict = dict()
        for cur in cases_collection.find({}, {"files.data_type", "files.created_datetime"}):
            for file in cur["files"]:
                data_type = file["data_type"]
                year = file["created_datetime"].year
                if data_type not in file_dict.keys():
                    file_dict[data_type] = dict()
                    file_dict[data_type][year] = 1
                else:
                    if year not in file_dict[data_type].keys():
                        file_dict[data_type][year] = 1
                    else:
                        file_dict[data_type][year] += 1
        table = pd.DataFrame(file_dict).transpose().fillna(0)
        table["total"] = table.sum(1)
        return table.sort_values("total", ascending=False)


    @staticmethod
    def download_files(file_id_list: list, bulk: int = 100) -> list:
        """
        :param file_id_list: list of file ids to be downloaded
        :type bulk: int
        """
        dir_name = c.DOWNLOAD_DIR + "/" + time.strftime("%Y%m%d-%H%M%S")
        os.system("mkdir " + dir_name)
        reminder: List[Any] = copy.deepcopy(list(file_id_list))
        while len(reminder) > bulk:
            sub_list = reminder[:bulk]
            del reminder[:bulk]
            File.download_bulk(sub_list, dir_name)
        File.download_bulk(reminder, dir_name)
        gz_files = glob.glob(dir_name + "/*.tar.gz")
        for gzFile in gz_files:
            os.system("tar xvzf " + gzFile + " -C " + dir_name)
        files = glob.glob(dir_name + "/*/*")
        return files

    @staticmethod
    def download_bulk(fileId_id_ist: list, dir_name: str):
        """
        :param fileId_id_ist: list of file ids to be downloaded
        :type dir_name: str
        """
        with open(c.TOKEN_FILE) as f:
            token = str(f.read().strip())
        endpt = 'https://api.gdc.cancer.gov/data'
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": token
        }
        params = {
            "ids": fileId_id_ist
        }
        response = requests.post(endpt, data=json.dumps(params), headers=headers)
        response_head_cd = response.headers["Content-Disposition"]
        file_name = re.findall("filename=(.+)", response_head_cd)[0]
        file_name = dir_name + "/" + time.strftime("%Y%m%d-%H%M%S") + "_" + file_name
        with open(file_name, "wb") as output_file:
            output_file.write(response.content)
        return True

    # @staticmethod
    # def clean_xml_helper(doc):
    #     if type(doc) == OrderedDict or type(doc) == dict or type(doc) == list:
    #         keys = copy.deepcopy(list(doc.keys()))
    #         for key in keys:
    #             new_key = key.split(":")[-1].replace('.', '_')
    #             doc[new_key] = File.clean_xml(doc[key])
    #             if new_key != key:
    #                 del doc[key]
    #         return doc
    #     else:
    #         return doc


    @staticmethod
    def clean_xml_helper(doc):
        if type(doc) == OrderedDict or type(doc) == dict:
            keys = copy.deepcopy(list(doc.keys()))
            if '#text' not in doc.keys():
                doc['#text'] = None
            for key in keys:
                new_key = key.split(":")[-1].replace('.', '_')
                doc[new_key] = File.clean_xml_helper(doc[key])
                if new_key != key:
                    del doc[key]
            return doc
        elif type(doc) == list:
            for item in copy.deepcopy(doc):
                if type(item) == str:
                    new_item = item.split(":")[-1].replace('.', '_')
                else:
                    new_item = File.clean_xml_helper(copy.deepcopy(item))
                doc.remove(item)
                doc.append(new_item)
            return doc
        elif doc is None:
            return doc
        else:
            return str(doc).strip().lower()


    @staticmethod
    def clean_xml(doc):
        File.clean_xml_helper(doc)
        return json.loads(json.dumps(doc))

    @staticmethod
    def get_value(doc_dict, *levels):
        levels = list(levels)
        for level in levels:
            if level in doc_dict.keys():
                doc_dict = doc_dict[level]
            else:
                return set()
        return File.get_value_helper(doc_dict)

    @staticmethod
    def get_value_helper(doc_dict, value_set=None):
        if value_set is None:
            value_set = set()
        if type(doc_dict) == OrderedDict or type(doc_dict) == dict:
            if "#text" in doc_dict.keys():
                value_set.add(doc_dict["#text"].lower())
            else:
                for key in doc_dict.keys():
                    value_set.union(File.get_value_helper(doc_dict[key], value_set))
        return value_set

    @staticmethod
    def get_dict_depth(dict_doc, level=1):
        if not isinstance(dict_doc, dict) or not dict_doc:
            return level
        return max(File.get_dict_depth(dict_doc[key], level + 1) for key in dict_doc)

    @staticmethod
    def find_file(dir, file_name):
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file == file_name:
                    return root + "/" + file_name

    @staticmethod
    def find_by_suffix(dir, suffix):
        files_with_suffix = []
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file.endswith(suffix):
                    files_with_suffix.append(root + "/" + file)
        return files_with_suffix
