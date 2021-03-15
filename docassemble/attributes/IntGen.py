# Function to generate a Docassemble Interview using
# DADataType object types on the basis of a YAML
# description of a data structure.

import yaml

__all__ = ['generate_interview']

def generate_interview(filename):
    with open(filename) as file:
        data_structure = yaml.load(file, Loader=yaml.FullLoader)
    
    ## Include DADataType
    output = "\n\ninclude:\n"
    output += "  - DADataType.yml\n"
    output += "  - DAScasp.yml\n"
    output += "---\n"

    ## Generate the parameters for DAScasp
    output += "mandatory: True \n"
    output += "code: |\n"
    output += "  ruleSource = \"" + data_structure['rules'] + "\"\n"
    output += "  query = \"" + data_structure['query'] + ".\"\n"
    output += "---\n"

    ## Copy the terms from the source file
    output += "terms:\n"
    output += yaml.dump(data_structure['terms'],width=1000000)
    output += "---\n"

    ## Include the Source File So It Can Be Accessed At RunTime
    output += "variable name: data_structure\n"
    output += yaml.dump(data_structure,width=1000000)
    output += "---\n"


    ## Generate Objects Block
    output += "objects:\n"
    for var in data_structure['data']:
        output += generate_object(var)
    output += "---\n"

    ## Generate Code Blocks for Lists.
    for var in data_structure['data']:
        output += make_complete_code_block(var)

    ## Generate Agenda Block (Temporarily Including Everything in The Root)
    output += "variable name: agenda\n"
    output += "data:\n"
    for var in data_structure['data']:
        if is_list(var):
            output += "  - " + var['name'] + ".gather()\n"
        else:
            output += "  - " + var['name'] + ".value\n"
    output += "---\n"

    ## Generate a Code Block That will Generate s(CASP) code.
    output += "code: |\n"
    output += "  facts = \"\"\n"
    for var in data_structure['data']:
        output += generate_translation_code(var)
    output += "---\n"

    ## Generate Mandatory Code Block That Will Prompt Collection
    output += "mandatory: True\n"
    output += "code: |\n"
    output += "  for a in agenda:\n"
    output += "    exec(a)\n"
    output += "---\n"

    ## Generate The Closing Question
    output += "mandatory: True\n"
    output += "question: Finished\n"
    output += "subquestion: |\n"
    output += "  ${ show_answers }\n"
    output += "---\n"

    return output

def generate_translation_code(input_object,indent_level=2,parent=""):
    output = ""
    indent = (" ") * indent_level
    #output += indent + "# Regarding " + input_object['name'] + "\n"
    if 'encodings' in input_object:
        if is_list(input_object):
            if parent == "": # This is a root list
                output += indent + "for " + input_object['name'] + "_element in " + input_object['name'] + ":\n"
                for e in input_object['encodings']:
                    output += indent + "  facts += \"" + e.replace('X',"\" + " + input_object['name'] + "_element.value + \"") + ".\\n\"\n"
            else: # This is a non-root list
                output += indent + "for " + input_object['name'] + "_element in " + parent + "." + input_object['name'] + ":\n"
                for e in input_object['encodings']:
                    output += indent + "  facts += \"" + e.replace('X',"\" + " + input_object['name'] + "_element.value + \"").replace('Y',"\" + " + parent + ".value + \"") + ".\\n\"\n"
        else: # This is not a list.
            for e in input_object['encodings']:
                output += indent + "facts += \"" + e.replace('X',"\" + " + parent + "." + input_object['name'] + ".value + \"").replace('Y',"\" + " + parent + ".value + \"") + ".\\n\"\n"
    if 'attributes' in input_object:
        for a in input_object['attributes']:
            output += generate_translation_code(a,indent_level+2,input_object['name'] + "_element")
    return output

def make_complete_code_block(input_object,root=""):
    output = ""
    if root == "":
        dot = ""
    else:
        dot = "."
    if "[i]" not in root:
        level = "[i]"
    else:
        if "[j]" not in root:
            level = "[j]"
        else:
            if "[k]" not in root:
                level = "[k]"
            else:
                if "[l]" not in root:
                    level = "[l]"
                else:
                    if "[m]" not in root:
                        level = "[m]"
                    else:
                        raise Error("Docassemble cannot handle nested lists of depth > 5")
    if is_list(input_object):
        new_root = root + dot + input_object['name'] + level
        this_root = root + dot + input_object['name']
    else:
        new_root = root + dot + input_object['name']
        this_root = new_root
    if is_list(input_object):
        output += "code: |\n"
        output += "  " + new_root + ".value\n"
        if 'attributes' in input_object:
            for a in input_object['attributes']:
                if is_list(a):
                    output += "  " + new_root + "." + a['name'] + ".gather()\n"
                else:
                    output += "  " + new_root + "." + a['name'] + ".value\n"
        output += "  " + new_root + ".complete =  True\n"
        output += "---\n"
    if 'attributes' in input_object:
        for a in input_object['attributes']:
            output += make_complete_code_block(a,new_root)
    return output

def generate_object(input_object,root=""):
    if root == "":
        dot = ""
    else:
        dot = "."
    if "[i]" not in root:
        level = "[i]"
    else:
        if "[j]" not in root:
            level = "[j]"
        else:
            if "[k]" not in root:
                level = "[k]"
            else:
                if "[l]" not in root:
                    level = "[l]"
                else:
                    if "[m]" not in root:
                        level = "[m]"
                    else:
                        raise Error("Docassemble cannot handle nested lists of depth > 5")
    if is_list(input_object):
        new_root = root + dot + input_object['name'] + level
        this_root = root + dot + input_object['name']
    else:
        new_root = root + dot + input_object['name']
        this_root = new_root
    output = "  - " + this_root + ": "
    if is_list(input_object):
        output += "DAList.using(object_type=" + generate_DADTDataType(input_object['type'])
        if 'minimum' in input_object:
            output += ",minimum=" + str(input_object['minimum'])
        if 'maximum' in input_object:
            output += ",maximum=" + str(input_object['maximum'])
        if 'exactly' in input_object:
            output += ",target_number=" + str(input_object['exactly'])
        if 'exactly' in input_object:
            output += ",ask_number=True"
        output += ",complete_attribute=\"complete\")\n"
    else:
        if input_object['type'] == "Enum":
            output += "|\n"
            output += "      " + generate_DADTDataType(input_object['type']) + ".using(options="
            output += str(input_object['options']) + ")\n"
        else: 
            output += generate_DADTDataType(input_object['type']) + "\n"
    
    if 'attributes' in input_object:
        for a in input_object['attributes']:
            output += generate_object(a,new_root)
    return output

dadatatypes = {
        "Boolean": "DADTBoolean",
        "Continue": "DADTContinue",
        "String": "DADTString",
        "Enum": "DADTEnum",
        "Number": "DADTNumber",
        "Date": "DADTDate",
        "DateTime": "DADTDateTime",
        "Time": "DADTTime",
        "YesNoMaybe": "DADTYesNoMaybe",
        "File": "DADTFile",
        "Object": "DADTObjectRef"
    }

def generate_DADTDataType(input_type):
    if input_type not in dadatatypes:
        raise Error("Unknown datatpye.")
    return dadatatypes.get(input_type)

def is_list(input):
    # Something with exactly 1 or 0 values is not a list.
    if 'exactly' in input and (input['exactly'] == 1 or input['exactly'] == 0):
        return False
    # Something with a minimum of more than one, or with a minumum and no maximum
    # is a list
    if 'minimum' in input:
        if input['minimum'] > 1:
            return True
        if 'maximum' not in input:
            return True
    # Something with a maximum above one is a list
    if 'maximum' in input and input['maximum'] > 1:
        return True
    # Something with an exact number above 1 is a list
    if 'exactly' in input and input['exactly'] > 1:
        return True
    # Otherwise
    return False