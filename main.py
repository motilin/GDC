import helpergdc as hg
from gdcClasses.Connection import Connection
from gdcClasses.CaseBin import CaseBin
from gdcClasses.Drug import Drug
from gdcClasses.File import File
from gdcClasses.Case import Case
from gdcClasses.ClinicalSupplementXML import ClinicalSupplementXML
import constants as c
from gdcClasses.Node import Node
import glob

hg.initiate_logger()

GDC_DB = Connection()

# hg.download_gdc_data(GDC_DB)

# xml_per_schema_df = ClinicalSupplementXML.export_number_of_xmls_per_schema(GDC_DB)

# ClinicalSupplementXML.export_query_paths(GDC_DB, '@cde')

files = glob.glob(c.QUERY_PATHS_PREFIX + '*')
prefix_length = len(c.QUERY_PATHS_PREFIX) + 5
exported = [file[prefix_length:] for file in files]

cde_list = []
with open('./data/query_paths_export/query_paths_export_@cde_None') as f:
    for line in f:
        if len(line.strip()) == 0:
            continue
        cde_num = line.split('.')[-1].strip()
        if len(cde_num) > 0:
            cde_list.append(cde_num)
cde_list = list(set(cde_list))

not_exported = [x for x in cde_list if x not in exported]

print(len(cde_list), len(exported), len(not_exported))

for cde_num in not_exported:
    pass
    ClinicalSupplementXML.export_query_paths(GDC_DB, '@cde', cde_num)









# drugs = hg.update_clinical_supplement_data(GDC_DB)




# gen = ClinicalSupplementXML.XML_generator(GDC_DB)
# xml = next(gen)
# xml = next(gen)
# xml = next(gen)
# xml = next(gen)
# xml.get_values()




# leaves = tree.get_leaves()
# cde_leaves = []
# for leaf in leaves:
#     if leaf.parent.value == '@cde':
#         cde_leaves.append(leaf)
#
# print(len(leaves))
# print(len(cde_leaves))
#
# drug_name_leaves = []
# for leaf in cde_leaves:
#     if leaf.value == '2975232':
#         drug_name_leaves.append(leaf)




# xml.get_path_to_leaf('@cde', '2975232')




# drugs = hg.update_clinical_data(xml)


# import xmltodict
# with open(xml.file_name) as f:
#     doc = (xmltodict.parse(f.read()))
#
# content = File.clean_xml(doc)
# mydoc = {'a':'A'}
# print(File.clean_xml(mydoc))


# xml_file = '/media/motti/fbb44c37-f109-4e31-8cc4-194bb4293076/mottip/ChemotherapiesResistance/analysis/GDC/downloads/20190912-184033/fc2f950d-92ac-4a18-a9ed-e2ba8a15f4cf/nationwidechildrens.org_clinical.TCGA-ZJ-AAXD.xml'
# xml_file = "/home/motti/mottip/ChemotherapiesResistance/analysis/GDC/downloads/20190912-133548/20190912-133549_nationwidechildrens.org_clinical.TCGA-OU-A5PI.xml"

# schema_files = File.find_by_suffix(c.SCHEMA_DIR, '.xsd')

# Parser.get_schemas()

# schemas = hg.update_clinical_supplement_data(GDC_DB)

# N = 10
# responseDf = Drug.getDrugsFrequencyTable(GDC_DB)
# topNdf = responseDf.iloc[:N, ]
# topNdrugs = topNdf.index.to_list()

# fileTypes = File.getFileFrequencyTable(GDC_DB)
# caseBin = CaseBin(GDC_DB)
# fileDf = caseBin.drugs(topNdrugs).get().getFileFrequencyTable(topNdrugs, "Aggregated Somatic Mutation")
#
# hg.barPlot(topNdf.iloc[:, 1:], fileDf.iloc[:, 1:])

# xml1 = "/home/motti/mottip/ChemotherapiesResistance/analysis/GDC/downloads/20190910-182457/3fe4d42f-9a4d-4928-895b-4674d4aba96e/nationwidechildrens.org_clinical.TCGA-QD-A8IV.xml"
# xml2 = "/home/motti/mottip/ChemotherapiesResistance/analysis/GDC/downloads/20190910-182457/9cbfb435-4ed0-4780-8750-5e72dce19891/nationwidechildrens.org_clinical.TCGA-DD-AAEA.xml"
# xml3 = "/home/motti/mottip/ChemotherapiesResistance/analysis/GDC/downloads/20190912-133548/20190912-133549_nationwidechildrens.org_clinical.TCGA-OU-A5PI.xml"
# schema1 = "/home/motti/Downloads/TCGA_BCR.THCA_Clinical.xsd"
# schema2 = "/home/motti/Downloads/TCGA_BCR.LIHC_Clinical.xsd"

# import xmltodict
# with open(xml1) as f:
#     doc1 = xmltodict.parse(f.read())
# with open(xml2) as f:
#     doc2 = xmltodict.parse(f.read())
# with open(xml3) as f:
#     doc3 = xmltodict.parse(f.read())
#
# doc1 = File.clean_xml(doc1)
# doc2 = File.clean_xml(doc2)
# doc3 = File.clean_xml(doc3)

# case = Case.get_case(GDC_DB, "C35E4390-2809-4D88-86F3-208DE05B338A".lower())
# case = hg.update_clinical_data(doc3, GDC_DB)

# case = Case.get_case(GDC_DB,"a5be4e42-cb6c-4e67-8547-45dbd058bb95")