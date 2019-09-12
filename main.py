import helpergdc as hg
from gdcClasses.Connection import Connection
from gdcClasses.CaseBin import CaseBin
from gdcClasses.Drug import Drug
from gdcClasses.File import File
from gdcClasses.Case import Case

GDC_DB = Connection()

# hg.download_gdc_data(GDC_DB)

schemas = hg.update_clinical_supplement_data(GDC_DB)

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