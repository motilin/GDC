from xml.parsers.expat import ExpatError
from .File import File
import xmltodict
import constants as c


class Parser:

    def __init__(self, gdc_xml_file):
        self.doc = None
        self.schema = None
        self.schema_set = set()
        self.load_schemas()
        self.load_doc(gdc_xml_file)

    def load_doc(self, gdc_xml_file):
        try:
            with open(gdc_xml_file) as f:
                doc = xmltodict.parse(f.read())
        except ExpatError:
            raise TypeError
        except UnicodeDecodeError:
            raise TypeError
        self.doc = File.clean_xml(doc)
        self.schema = self.doc['tcga_bcr']['schemaLocation']

    def load_schemas(self):
        with open(c.SCHEMA_FILE) as schema_file:
            for line in schema_file:
                self.schema_set.add(line.strip())

    def parse(self):
        if self.schema not in self.schema_set:
            print("schema file: " + self.schema)
            raise TypeError('unknown schema')
