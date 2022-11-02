from Python2DiagramRedactor.Preprocessor import *
from Python2DiagramRedactor.BlockDiagram import *
import sys
from Python2DiagramRedactor.debug.Preview import *


def main():
    args = sys.argv[1::]

    try:
        file_path = args[0]
        f = open(file_path, 'r', encoding='utf-8')
    except:
        try:
            f = open(input('path: '), 'r', encoding='utf-8')
        except:
            exit('wrong path')

    try:
        if args[1] == 'procedural': mode = Preprocessor.CONVERT_MODS['FUNCTIONAL_TO_PROCEDURAL']
        else: mode = Preprocessor.CONVERT_MODS['NO_CONVERT']
        
        
    except:
        mode = Preprocessor.CONVERT_MODS['NO_CONVERT']


    p = Preprocessor(f, mode)
    serealized = p.get_serealized_code()
    diagram = Block_diagram(serealized, p.find_all_veribles())

    f.close()


    Preview.draw(diagram.debug())


if __name__ == "__main__":
    main()