import os
import re
from docassemble.base.functions import value, define, undefine



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


def get_bounding(block_type, yaml_contents, **kwargs) -> (int, int):
    '''
        Returns the boundaries containing the appropriate information.

        Assumptions:
            - only 1 'objects' block per yaml
            - only 1 'agenda' metadata block per yaml
    '''

    # TODO: this needs urgent refactoring. At this point, this function is too bloated.
    # Suggest seperating into two, one handling the search, the other handling assignments

    blockSep = '---'
    objectsHeader = 'objects:'
    agendaHeader = '[\s]*agenda:'
    codeHeader = 'code:'
    findRight = False

    list_name = '^$'
    if kwargs:
        list_name = '\s*' + kwargs['list_name']

    if re.match('obj(ect)?s?',block_type):
        block_header = objectsHeader
    elif re.match('ag.?n(da)?',block_type):
        block_header = agendaHeader
    elif re.match('code',block_type):
        block_header = codeHeader

    for n, line in enumerate(yaml_contents):
        if re.match(block_header,line):
            lBound = n + 1 # items start from after the header is listed
            findRight = True
        if findRight and (re.match(blockSep,line)): # block seperator denotes end of list
            rBound = n
            if block_header != codeHeader or re.match(list_name, yaml_contents[lBound]):
                return (lBound, rBound)
            else:
                get_bounding('code',yaml_contents[rBound:],list_name=list_name)

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

def yaml_call_list(**kwargs) -> bool:
    # 1) given a list name and chunk, initialize counter to 0.
    # 2) substitute counter if counter in kwargs
    # 3)

    # definitions
    if 'state' in kwargs:
        state = kwargs['state']
    if 'sub_str' not in kwargs:
        kwargs['sub_str'] = '(' + kwargs['list_name'] + '\[)(?:i|j|k|l|m|n)(\])'


    if state == 'initialize':
        step = value(kwargs['list_name'] + '.there_are_any')
        kwargs['counter'] = 0
        if step:
            kwargs['state'] = 'collect'
            return yaml_call_list(**kwargs)
        else:
            return True # If there should not elements of the such, the empty list is complete

    elif state == 'collect':

        for attr in kwargs['chunk']:
            attr = attr.strip() # this should be handled before chunk is passed on initialization.
            tbc = re.sub(kwargs['sub_str'],r'\g<1>{}\g<2>'.format(kwargs['counter']),attr)

            if re.match(r'.*\.complete',attr):
                # notify completeness of inner DAList object
                tbc = re.sub('\s','',tbc)
                tbc = tbc.split('=')
                define(tbc[0], tbc[1])

                swp = kwargs['list_name'] + '.there_is_another'
                undefine(swp)
                nxt = value(swp) # it seems to be stuck here :/
                if nxt:
                    kwargs['counter'] += 1
                    return yaml_call_list(**kwargs)
                else:
                    return True # list fully collected

            else: ## TODO: REFACTOR
                if re.match(kwargs['list_name'] + r'\[[0-9]*\].value',tbc):
                    value(tbc)
                else:
                    tbc_init = re.sub(r'\.value','',tbc) # perhaps this should be handled somewhere else?
                    value(tbc_init)
                    value(tbc)

    raise Exception('yaml_call_list is not supposed to reach this point.')

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
            yaml_call_list(list_name=obj_name)
        else:
            yaml_call_object(obj_name)
    return
