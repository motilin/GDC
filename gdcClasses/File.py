import datetime
from dateutil.parser import parse


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
            self.setFileId(file_document["file_id"])
        else:
            raise LookupError("missing file_id")
        if "created_datetime" in keys:
            self.setCreatedDatetime(file_document["created_datetime"])
        if "data_format" in keys:
            self.setDataFormat(file_document["data_format"])
        if "data_type" in keys:
            self.setDataType(file_document["data_type"])
        if "experimental_strategy" in keys:
            self.setExperimentalStrategy(file_document["experimental_strategy"])
        if "md5sum" in keys:
            self.setMd5sum(file_document["md5sum"])
        if "file_name" in keys:
            self.setFileName(file_document["file_name"])

    def serialize(self):
        return self.__dict__

    def deserialize(self, file_document):
        self.setFileId(file_document["file_id"])
        self.created_datetime = file_document["created_datetime"]
        self.setDataFormat(file_document["data_format"])
        self.setDataType(file_document["data_type"])
        self.setExperimentalStrategy(file_document["experimental_strategy"])
        self.setMd5sum(file_document["md5sum"])
        self.setFileName(file_document["file_name"])

    def setFileId(self, file_id):
        self.file_id = file_id

    def setDataType(self, data_type):
        self.data_type = data_type

    def setCreatedDatetime(self, created_datetime):
        self.created_datetime = parse(created_datetime).date()

    def setFileName(self, file_name):
        self.file_name = file_name

    def setMd5sum(self, md5sum):
        self.md5sum = md5sum

    def setDataFormat(self, data_format):
        self.data_format = data_format

    def setExperimentalStrategy(self, experimental_strategy):
        self.experimental_strategy = experimental_strategy
