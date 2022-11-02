from PythonPreprocessor import PythonPreprocessor
from Py2BlockDiagram import Py2BlockDiagram
import json


def main():

    try:
        file_path = input('path: ')
        f = open(file_path, 'r', encoding='utf-8')
    except FileNotFoundError:
        exit('wrong path')

    p = PythonPreprocessor(f)
    programs_list = p.get_programs_list()
    diagram = Py2BlockDiagram.build_from_programs_list(programs_list)
    f.close()
    f = open(f'{file_path}.json', 'w+', encoding='utf-8')
    f.write(json.dumps(diagram, indent=4))
    f.close()
    print(f'Diagram has been saved as {file_path}.json')


if __name__ == "__main__":
    main()
