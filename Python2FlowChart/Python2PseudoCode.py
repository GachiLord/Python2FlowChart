import re
from PyChart.PseudoCode import PseudoCode


class Python2PseudoCode(PseudoCode):
    
    @staticmethod
    def to_pseudocode(lines: str) -> str:
        pseudocode = ''
        lines = lines.split('\n')  # type: ignore

        for line in lines:
            # clear type-changing operators, input, print
            line = line.replace('**', '^')  # IT MUST BE BEFORE THE '*' statement!!!
            line = line.replace('*', '×')
            line = line.replace('/', '÷')
            if 'import ' in line:
                line = ''
            line = re.sub(r'print ?\((.*)\)?\)', r'\g<1>', line)
            line = re.sub(r'(\=| |\()(int|float|str|bool|tuple|list|dict|set) ?\((.*)\)',
                          r'\g<3>', line)  # IT MUST BE LAST!!!!

            # control structs to c-style
            if line[0:2] == 'if':
                pseudocode += re.sub(r'if ', '', line)[0:-1]
            elif line[0:4] == 'else':
                pseudocode += ''
            elif line[0:4] == 'elif':
                pseudocode += re.sub(r'elif ', '', line)[0:-1]
            elif line[0:3] == 'for':
                pseudocode += re.sub(r'for ', '', line)[0:-1]
            elif line[0:5] == 'while':
                pseudocode += re.sub(r'while ', '', line)[0:-1]
            elif line[0:3] == 'def':
                pseudocode += 'function ' + re.sub(r'def |\:', '', line)[0:-1]
            else:
                if 'return ' in line:
                    pseudocode += line.replace('return', 'передача')
                else:
                    if line.strip() == '':
                        pseudocode += line
                    else:
                        pseudocode += f'{line}\n'

        return pseudocode
