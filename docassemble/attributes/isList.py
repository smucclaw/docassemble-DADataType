import yaml
import re
from copy import deepcopy

def stripIndices(varname : str) -> list[str]:
    substr = "[ijklmn]*[0-9]*"
    vn = re.sub("\[" + substr + "\]",'',varname)
    return vn.split('.')

def isolateSpec(ds : list[dict], varname: list[str]) -> dict:
    ''' Takes the data structure, and isolates the spec of the object required
    '''

    for i, item in enumerate(varname):
        for dtype in ds:
            if item == dtype['name']:
                if i + 1 == len(varname):
                    return deepcopy(dtype)
                elif "attributes" in dtype.keys():
                    ds = deepcopy(dtype["attributes"])
                pass

    return {}

def isList(spec : dict) -> bool:
    spk = set(spec.keys())
    if "exactly" in spk and (spec["exactly"] == 1):
        return False
    elif (set(["minimum","maximum","exactly"]) & spk) == set():
        return False
    else:
        return True

if __name__ == "__main__":
    contents = []
    with open("./root.yml", 'r') as f:
        fgen = yaml.load_all(f, Loader=yaml.SafeLoader)
        while x:=next(fgen):
            contents.append(x)

    traversal = stripIndices("person[i].birthdate")
    print(traversal)

    print("Test 1")
    spec1 = isolateSpec(contents[0]['data'], traversal)
    print(spec1)
    print(isList(spec1))

    print ()
    print("test 2")
    spec2 = isolateSpec(contents[0]['data'], ['person'])
    print(spec2)
    print(isList(spec2))
