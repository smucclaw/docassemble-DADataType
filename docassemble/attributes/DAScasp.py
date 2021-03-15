# A simple interface to the s(CASP) constraint answer set programming
# tool from inside a Docassemble interview.
import docassemble.base.util

def a_of_the_b(a, b, **kwargs):
  return str(a) + " of the " + str(b)

docassemble.base.util.update_language_function('en', 'a_in_the_b', a_of_the_b)

import subprocess

# Convert the Docassemble Interview Data into a set of s(CASP) statements
def da2scasp():
    pass

# Send an s(CASP) file to the reasoner and return the results.
def sendQuery(filename):
    results = subprocess.run(['/usr/bin/sudo', '/root/.ciao/build/bin/scasp', '--human', '--tree', '-s0', filename], stdout=subprocess.PIPE).stdout.decode('utf-8')
    
    output = {}

    # If result is no models
    if results.endswith('no models\n\n'):
        query = results.replace('\n\nno models\n\n','').replace('\n    ','').replace('QUERY:','')
        output['query'] = query
        output['result'] = 'No'
        return output
    else:
        # Divide up the remainder into individual answers
        answers = results.split("\tANSWER:\t")
        query = answers[0]
        del answers[0]
        query = query.replace('\n','').replace('     ',' ').replace('QUERY:','')
        output['query'] = query
        output['result'] = 'Yes'
        output['answers'] = []
        
        # for each actual answer
        for a in answers:
            #Separate out the time, tree, model, and bindings
            answer_parts = a.split('\n\nJUSTIFICATION_TREE:\n')
            time = answer_parts[0]
            answer_parts = answer_parts[1].split('\n\nMODEL:\n')
            tree = answer_parts[0]
            answer_parts = answer_parts[1].split('\n\nBINDINGS:')
            model = answer_parts[0]
            bindings = []
            # The bindings may not exist
            if len(answer_parts) > 1:
                bindings = answer_parts[1].splitlines()
            # Reformat the Time
            time = time.replace(' ms)','').replace('(in ','').split(' ')[1]

            # Reformat the Tree
            explanations = make_tree(tree)
            explanations = new_display_list(explanations)

            # Reformat the Model
            model = model.replace('{ ','').replace(' }','').split(',  ')

            # Reformat the Bindings
            if bindings:
                bindings = [b for b in bindings if b != '' and b != ' ']
                bindings = [b.replace(' equal ',': ') for b in bindings]

            # Create a dictionary for this answer
            new_answer = {}
            new_answer['time'] = time
            new_answer['model'] = model
            if bindings:
                new_answer['bindings'] = bindings
            new_answer['explanations'] = explanations

            # Add the answer to the output_answers list
            output['answers'].append(new_answer.copy())
        
        # Now add the output answers to the result
        return output

def get_depths(lines):
    output = []
    for l in lines:
        # If we get to global constraints, stop.
        if l.startswith('The global constraints hold'):
            break
        # Skip lines that start with 'abducible' holds
        if l.lstrip(' ').startswith('\'abducible\' holds'):
            continue
        this_line = {}
        depth = (len(l) - len(l.lstrip(' ')))/4
        this_line['text'] = l.lstrip(' ')
        # s(CASP) applies periods to some lines that we don't display, so
        # just get rid of them all.
        if this_line['text'].endswith('.'):
            this_line['text'] = this_line['text'].rstrip('.')
        this_line['depth'] = depth
        output.append(this_line.copy())
    return output


def make_tree(lines):
    lines = lines.splitlines()

    # The first step is to create a list of tuples of the lines of text, and their depths.
    meta_lines = get_depths(lines)
    
    # Recursively create a tree from the meta_lines
    #new_tree = convert_tree(meta_lines,0)
    #output = new_tree
    return meta_lines

def convert_tree(lines,depth):
    
    output = []
            
    # Go through all of the lines.
    for x in range(len(lines)):

        # If the next line is shallower, that is the edge case, just do nothing.
        # And stop processing the list.
        if lines[x]['depth'] < depth:
            break

        # If the next line is at the same depth, add it to the list,
        # and continue looping through the lines
        if lines[x]['depth'] == depth:
            output.append(lines[x]['text'])

        # If the next line is at a deeper depth, add a list.
        # then set the value of that list to the results of covert_tree
        # for this and following lines with the new depth.
        # Then go back to adding lines to this level.
        if lines[x]['depth'] > depth:
            output.append(convert_tree(lines[x:],lines[x]['depth']))

    return output



def new_display_list(input,depth=0):
    if depth==0:
        output = "<ul id=\"explanation\" class=\"active\">"
    else:
        output = "<ul class=\"nested\">"
    skip = 0
    for i in range(len(input)):
        if skip > 0:
            skip = skip-1
            continue
        while input[i]['depth'] < depth:
            output += "</li></ul>"
            depth = depth-1
        if input[i]['depth'] == depth:
            if input[i]['text'].endswith('because'):
                output += "<li><span class=\"caret\">"
            else:
                output += "<li>"
            output += input[i]['text']
            if input[i]['text'].endswith('because'):
                output += "</span>"
            else:
                output += "</li>"
        if input[i]['depth'] > depth:
            sub_output = new_display_list(input[i:],input[i]['depth'])
            skip = sub_output.count("<li>") # skip the parts already done.
            output += sub_output

    output += "</ul>"
    return output
  
def display_list(input,element=0,root_node=True):
  output = ""
  
  print("Considering " + str(input[element]) + '\n')
  if len(input) > element+1:
    print("There are more.\n")
    if isinstance(input[element+1],list):
      print('This has sub-elements.\n')
      has_branches = True
    else:
      print('This does not have sub-elements.\n')
      has_branches = False
  else:
    print('This does not have sub-elements.\n')
    has_branches = False
  if root_node:
    output += "<ul id=\"explanation\">"
  output += "<li>"
  if has_branches:
    output += "<span class=\"caret\">"
  if not isinstance(input[element],list):
    output += input[element]
  if has_branches:
    output += "</span><ul class=\"nested\">"
    output += display_list(input[element+1:],0,False)
  if has_branches:
    output += "</ul>"
  output += "</li>"
  if root_node:
    output += "</ul>"
    
  return output