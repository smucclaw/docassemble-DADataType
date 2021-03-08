import os
import re
from docassemble.base.functions import value



def path_convert(fname: str) -> str:
    '''
    Converts pathnames of static interviews that are served to the user, to the actual yaml file.

    TODO: While this will work when using playground files, I doubt that actual packaged yaml files will function in the same way.
          Perhaps it might be wiser to implement this within the module itself?

          - have a function that checks whether it is within a "playground" or "deployed" status
          - given the playground/deployed state, implement pathConvert accordingly
    '''
    return re.sub('playgroundstatic','playground',fname)

def agenda_path_convert(fname: str) -> str:
    '''
    Generates a pathname for the agenda file associated with the static interview served to the user.

    TODO: Right now this functions on the assumption that all agenda files will be within the
          playgroundsources directory. It also presumes that all agenda files associated with
          a <interview>.yml is named <interview>Agenda.yml
    '''
    stat2source = re.sub('playground(static)?','playgroundsources',fname)
    return re.sub('\.yml$','Agenda.yml',stat2source)


def get_contents(fname: str) -> list:
    with open(fname, 'r') as f:
        return f.readlines()


def get_bounding(block_type : str, yaml_contents : list) -> (int, int):
    '''
        Returns the boundaries containing the appropriate information.

        Assumptions:
            - only 1 'objects' block per yaml
            - only 1 'agenda' metadata block per yaml
    '''
    blockSep = '---'
    objectsHeader = 'objects:'
    agendaHeader = '[\s]*agenda:'
    findRight = False

    if re.match('obj(ect)?s?',block_type):
        block_header = objectsHeader
    elif re.match('ag.?n(da)?',block_type):
        block_header = agendaHeader

    for n, line in enumerate(yaml_contents):
        if re.match(block_header,line):
            lBound = n + 1 # items start from after the header is listed
            findRight = True
        if findRight and (re.match(blockSep,line)): # block seperator denotes end of list
            rBound = n
            return (lBound, rBound)

    raise Exception("get_bounding for {} failed".format(block_type))


def yaml_get_agenda(yaml_contents: list) -> list:
    '''
        Returns objects information
    '''
    lb, rb = get_bounding('agenda', yaml_contents)
    agenda_kebab = re.sub('\s', '', ''.join(yaml_contents[lb:rb]))

    return agenda_kebab.strip('-').split('-')


def yaml_get_objects(yaml_contents: list) -> dict:
    '''
        Returns objects information
    '''
    lb, rb = get_bounding('objects',yaml_contents)

    obj_nameType = {}
    for line in yaml_contents[lb:rb]:
        line=re.sub('-|\s','',line)

        if not line: # empty strings are falsy
            pass
        else:
            objName, objType = line.split(':')
            obj_nameType[objName] = objType

    return obj_nameType

def yaml_call_object(obj_name : str) -> None:
    value(obj_name + '.value')
    return

def yaml_call_list(list_name: str) -> None:
    value(list_name + '.there_are_any')
    return

def yaml_form_objects(yaml_path : str) -> None:
    this_file = get_contents(yaml_path)
    objs = yaml_get_objects(this_file)

    for obj_name in objs.keys():
        yaml_call_object(obj_name)
    return



## Working with external files

# TODO:
#   - refactor yaml_get_agenda and ext_get_agenda to agenda_from_file

def yaml_form_agenda(yaml_path : str):
    '''
    Takes a yaml file and calls the objects appropriately based on an agenda
    '''
    intv_file = get_contents(yaml_path)

    # check if external file exists, if true, use. else default to in-yaml metadata agenda block.
    ext_agenda_path = agenda_path_convert(yaml_path)
    if os.path.isfile(ext_agenda_path):
        agda_file = get_contents(ext_agenda_path)
    else:
        raise FileNotFoundError('Agenda file not found: {}'.format(ext_agenda_path))

    all_agenda = yaml_get_agenda(agda_file)
    all_objs   = yaml_get_objects(intv_file)
    for obj_name in all_agenda:
        if re.match('DAList.*',all_objs[obj_name]):
            yaml_call_list(obj_name)
        else:
            yaml_call_object(obj_name)
    return
