import xml.etree.ElementTree as ET

# Assuming the XML content is stored in a file named 'data.xml'
xml_file = 'MEITEResources.Defs.ME221.Generic.ME221-GENERIC_v86.medef'

# Parse the XML file
tree = ET.parse(xml_file)
root = tree.getroot()

# Find all 'DataLinkModel' elements
datalink_models = root.findall('.//DataLinkModel')

# Iterate over each model and print its 'id' and 'name'
for model in datalink_models:
    model_id = model.find('id').text
    model_name = model.find('name').text
    print(f"ID: {model_id}, Name: {model_name}")

