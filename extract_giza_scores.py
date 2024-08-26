import xml.etree.ElementTree as ET
import os, re
from tqdm import tqdm
import pickle
with open("/mmfs1/data/leferran/scripts/Formosan/giza-pp/MT_corp/2024-04-24.092344.leferran.A3.final", mode="r") as afile:
    aling = afile.read().split("\n")
meta_cpt = 0
en_cpt = 1
aling_cpt = 2

align_info = {}
data_id = 0
refs = {}
am_data = []
en_data = []
chars_to_remove_regex = '[\(\)\_\,\?\.\!\-\;\:\"\“\%\‘\”\�\'–\’\/\*=\[\]]'
chars_to_remove_regex_am = '[\(\)\_\,\?\.\!\-\;\:\"\“\%\‘\”\�–><\[\]\/\*=]'
namespace = {'xml': 'http://www.w3.org/XML/1998/namespace'}
root = "/mmfs1/data/leferran/scripts/Formosan/MT-xml-part-one/"
for collection in tqdm(os.listdir(root)):
    refs[collection] = []
    align_info[collection] = []
    xml_root = "/mmfs1/data/leferran/scripts/Formosan/MT-xml-part-one/{}/".format(collection)
    for xml_name in os.listdir(xml_root):
        print(collection, xml_name)
        xml_path = xml_root+xml_name
        with open(xml_path, mode="r", encoding="utf-8") as xfile:
            xml_string = xfile.read()

        # Parse the XML string
        root = ET.fromstring(xml_string)

        # Initialize dictionaries for FORM and TRANS
        
        # Iterate through each 'S' element
        for s_element in root.findall('S'):
            s_id = s_element.get('id')  # Get the 'id' attribute

            # Find the 'FORM' and 'TRANSL' elements
            form_element = s_element.find('FORM')
            
            form_element = re.sub(chars_to_remove_regex_am, '', form_element.text).lower()
            form_element = form_element.replace("’", "'")
            form_element = form_element.replace("ˈ", "'")
            form_element = form_element.replace("—", "")
            form_element = form_element.replace("-", "")

            trans_element = s_element.find('TRANSL[@xml:lang="en"]', namespaces=namespace)
            
            if trans_element.text!=None:
                trans_element = re.sub(chars_to_remove_regex, '', trans_element.text).lower()

                if aling[en_cpt].split()==trans_element.split() and meta_cpt<len(aling):

                    score = aling[meta_cpt].split()[-1]
                    en_sent = aling[en_cpt]
                    align_sent = aling[aling_cpt]
                    align_info[collection].append({"id" : s_id, "score" : score, "english": en_sent, "align" : align_sent, "xml": xml_name, "WARNING" : False})
                    meta_cpt+=3
                    en_cpt+=3
                    aling_cpt+=3
                elif meta_cpt>len(aling):
                    with open("alignement_results.pkl", mode="wb") as pfile:
                        pickle.dump(align_info, pfile)
                else:
                    print("alignment mismatch")
                    if aling[en_cpt-3].split()==trans_element.split():
                        print(aling[en_cpt-3].split(),trans_element.split())
                        print("mismatch gd too fast")
                        meta_cpt-=3
                        en_cpt-=3
                        aling_cpt-=3
                        # input()
                    align_info[collection].append({"id" : s_id, "score" : score, "english": en_sent, "align" : align_sent, "xml": xml_name, "WARNING" : True})
                    print(aling[en_cpt].split(),trans_element.split(), en_cpt)
                    meta_cpt+=3
                    en_cpt+=3
                    aling_cpt+=3
                    # input()

                # Extract the text content
                if form_element is not None:
                    am_data.append(form_element.strip())

                if trans_element is not None:
                    en_data.append(trans_element.strip())
                    refs[collection].append(trans_element.strip())
with open("alignement_results.pkl", mode="wb") as pfile:
    pickle.dump(align_info, pfile)
