from xml.parsers.expat import ExpatError
from pymongo.errors import DuplicateKeyError
from .File import File
import xmltodict
import constants as c
import os
import shutil
import copy
import glob
from .Document import Document
import bson
import logging
from gdcClasses.Node import Node
from gdcClasses.Connection import Connection
import pandas as pd

class ClinicalSupplementXML:

    def __init__(self, connection):
        self._id = None
        self.file_name = None
        self.connection = connection
        self.content = None
        self.schema_file = None
        self.query_file = None
        self.values = dict()

    def serialize(self):
        doc = dict()
        doc['_id'] = self._id
        doc['file_name'] = self.file_name
        doc['content'] = self.content
        doc['schema_file'] = self.schema_file
        doc['query_file'] = self.query_file
        return doc

    def deserialize(self, document):
        self._id = document['_id']
        self.file_name = document['file_name']
        self.content = document['content']
        self.schema_file = document['schema_file']
        self.query_file = document['query_file']
        return self

    @staticmethod
    def get_schemas():
        schema_main_path = c.SCHEMA_MAIN_PATH
        if os.path.isdir(schema_main_path):
            shutil.rmtree(schema_main_path)
        os.system('git clone https://github.com/nchbcr/xsd.git ' + schema_main_path)
        os.system("find " + c.SCHEMA_DIR + " -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;")
        if os.path.isdir(c.SCHEMA_DIR):
            for xsd_file in File.find_by_suffix(c.SCHEMA_DIR, '.xsd'):
                xsd_file = xsd_file.split('/')[-1]
                query_file = xsd_file[:-4]
                open(c.QUERIES_DIR + '/' + query_file, 'a').close()
        else:
            raise NotADirectoryError(c.SCHEMA_DIR + " wasn't found")

    def load_file(self, gdc_xml_file_name):
        try:
            with open(gdc_xml_file_name) as f:
                doc = xmltodict.parse(f.read())
        except ExpatError:
            raise TypeError
        except UnicodeDecodeError:
            raise TypeError
        self.file_name = gdc_xml_file_name
        self.content = File.clean_xml(doc)
        self._id = self.content['tcga_bcr']['admin']['file_uuid']['#text'].strip().lower()
        schema_file = self.content['tcga_bcr']['schemaLocation'].split("/")[-1]
        self.schema_file = File.find_file(c.SCHEMA_DIR, schema_file)
        self.query_file = c.QUERIES_DIR + '/' + schema_file[:-4]
        if self.schema_file is None:
            print('file name: ' + gdc_xml_file_name)
            raise EnvironmentError("schema file isn't recognized")
        return self

    # @staticmethod
    # def get_value(document, query_file_line):
    #     query_file_line_split = query_file_line.split(':')
    #     name = query_file_line_split[0].strip()
    #     var_type = query_file_line_split[1].strip()
    #     query = ':'.join(query_file_line_split[2:]).strip().strip('/').split('/')
    #     value = copy.deepcopy(document)
    #     node = 0
    #     while (value is not None) and (node < len(query)):
    #         if type(value) != dict:
    #             print('got value ' + value + ' prematurely')
    #             raise IndexError('missing path in schema')
    #         elif query[node] in value.keys():
    #             value = value[query[node]]
    #             node += 1
    #         else:
    #             value = None
    #             raise IndexError('missing path in schema')
    #     if value is None:
    #         if var_type == list:
    #             value = []
    #         elif var_type == set:
    #             value = set()
    #     elif var_type == 'int':
    #         value = int(value.strip())
    #     elif var_type == 'bool':
    #         value = (value.strip() == c.TRUE)
    #     elif var_type == 'str':
    #         value = value.strip().lower()
    #     elif var_type == 'list':
    #         if type(value) != list and len(value) == 1:
    #             value = [value]
    #     elif var_type == 'dict':
    #         pass
    #     else:
    #         raise TypeError('unfamiliar type in query file')
    #     return name, var_type, value

    def parse(self):
        with open(self.query_file) as query_file:
            for line in query_file:
                line = line.strip()

        return Document(self.values)

    def parse_query_file(self):
        query_dict = dict()
        with open(self.query_file) as query_file:
            for line in query_file:
                line = line.strip()
                if len(line) == 0:
                    continue
                line = line.split('|')
                name = line[0]
                query = line[-1].split('.')
                i = 0
                pointer = query_dict
                while i < len(query):
                    if query[i] in pointer.keys():
                        pointer = pointer[query[i]]
                        i += 1
                    else:
                        while i < len(query):
                            if i == len(query) - 1:
                                pointer[query[i]] = name
                            else:
                                pointer[query[i]] = dict()
                                pointer = pointer[query[i]]
                            i += 1
            return query_dict

    def get_values(self):
        '''
        requires running load_file() and save() first OR having the xml stored in the db already
        :return: returns a dict with the values requested by the query file
        '''

        stage1 = dict()
        stage1['$match'] = dict()
        stage1['$match']['_id'] = self._id
        stage2 = dict()
        stage2['$project'] = dict()
        stage2['$project']['_id'] = 0
        name_list = []

        xml_tree = Node()
        xml_tree.load_doc(self.content).get_leaves()
        with open(c.CDE_LIST) as f:
            for line in f:
                if len(line.strip()) == 0:
                    continue
                line = line.strip().lower().split('|')
                name = line[0]
                name_list.append(name)
                cde_number = line[-1]
                query_path_list = xml_tree.get_paths('@cde', cde_number)
                if len(query_path_list) > 1:
                    raise ValueError('more than one matching cde\'s in xml file')
                else:
                    query = '.'.join(['content'] + query_path_list[0][:-2] + ['#text'])
                stage2['$project'][name] = '$' + query

        with open(self.query_file) as f:
            for line in f:
                if len(line.strip()) == 0:
                    continue
                else:
                    line = line.strip().split('|')
                    name = line[0]
                    query = line[-1]
                    stage2['$project'][name] = '$' + query
                    name_list.append(name)

        pipeline = [stage1, stage2]
        cur = self.connection.get().clinical.aggregate(pipeline)
        self.values = [match for match in cur][0]
        for name in name_list:
            if (name not in self.values) or ((self.values[name] is not None) and (len(self.values[name]) == 0)):
                logging.debug('missing\t' + name + '\t' + self.schema_file)
        return self

    @staticmethod
    def write_query_line(query_line):
        query_files = glob.glob(c.QUERIES_DIR + '/*')
        for file in query_files:
            exists = False
            with open(file, 'r') as f:
                lines = [x.strip() for x in f.readlines()]
                if query_line.strip() in lines:
                    exists = True
            if not exists:
                with open(file, 'a') as f:
                    f.write(query_line.strip() + '\n')

    @staticmethod
    def remove_query_line(query_line):
        query_files = glob.glob(c.QUERIES_DIR + '/*')
        for file in query_files:
            exists = False
            with open(file, 'r') as f:
                lines = [x.strip() for x in f.readlines()]
            query_line = query_line.strip()
            if query_line in lines:
                exists = True
                lines.remove(query_line)
            if exists:
                with open(file, 'w') as f:
                    f.write('\n'.join(lines) + '\n')

    @staticmethod
    def remove_all_query_lines():
        query_files = glob.glob(c.QUERIES_DIR + '/*')
        for file in query_files:
            open(file, 'w').close()

    def save(self):
        local_clinical_collection = self.connection.get().clinical
        try:
            local_clinical_collection.insert_one(self.serialize())
            print("Saving clinical xml id: " + self._id)
        except DuplicateKeyError as error:
            local_clinical_collection.replace_one({'_id': self._id}, self.serialize())
            print("Replacing clinical xml id: " + self._id)
        except Exception as e:
            print(self.file_name)
            raise e

    @staticmethod
    def XML_generator(connection: Connection):
        local_clinical_collection = connection.get().clinical
        for xml_doc in local_clinical_collection.find({}):
            yield ClinicalSupplementXML(connection).deserialize(xml_doc)

    def get_path_to_leaf(self, key, value):
        self.get_path_to_leaf_helper(self.content, key, value)

    @staticmethod
    def get_path_to_leaf_helper(doc, key, value):
        if doc is None:
            pass
        elif type(doc) == list:
            for sub_doc in doc:
                ClinicalSupplementXML.get_path_to_leaf_helper(sub_doc, key, value)
        elif type(doc) != dict:
            pass
        elif (key in doc.keys()) and (doc[key] == value):
            print(key)
        else:
            for parent_key in doc.keys():
                ClinicalSupplementXML.get_path_to_leaf_helper(doc[parent_key], key, value)

    @staticmethod
    def export_number_of_xmls_per_schema(connection: Connection):
        counter = dict()
        for xml in ClinicalSupplementXML.XML_generator(connection):
            if xml.schema_file in counter.keys():
                counter[xml.schema_file] += 1
            else:
                counter[xml.schema_file] = 1
        table = pd.Series(counter).sort_values()
        table.to_csv(c.XMLS_PER_SCHEMA_FILE, sep='\t')
        return table

    @staticmethod
    def export_query_paths(connection: Connection, name, value=None):
        query_list = []
        for xml in ClinicalSupplementXML.XML_generator(connection):
            tree = Node()
            tree.load_doc(xml.content)
            paths = tree.get_paths(name, value)
            for path in paths:
                query_list.append('.'.join(path))
        query_list = list(set(query_list))
        query_list.sort()
        file_name = str(c.QUERY_PATHS_PREFIX + name + '_' + str(value))
        with open(file_name, 'w') as f:
            for query in query_list:
                f.write(query + '\n')
