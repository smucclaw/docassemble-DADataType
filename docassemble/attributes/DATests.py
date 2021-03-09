import DAFunctions as DA

def yaml_call_list(yaml_path):
    this_file = DA.get_contents(yaml_path)
    lb, rb = DA.get_bounding('code', this_file, list_name='peeps')
    chunk = this_file[lb:rb]
    return DA.yaml_call_list(state='initialize', list_name='peeps',chunk=chunk)

if __name__=='__main__':
    print(yaml_call_list('data/questions/ouroboros.yml'))
