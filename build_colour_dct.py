
def build_colour_dct():

    H = {}

    with open('colours.txt','r') as f:
        lines = f.read().strip().split('\n')

    for line in lines:
        new_line = line.split('=')
        key = new_line[0].strip()
        val = eval(new_line[1].strip())
        
        H[key] = val

    return H

