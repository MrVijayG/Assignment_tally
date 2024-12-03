import xml.etree.ElementTree as ET

class XMLParser:
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path

    def get_root(self):
        tree = ET.parse(self.xml_file_path)
        return tree.getroot()
