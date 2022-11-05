try:
    from Python2FlowChart.PyPreprocessor import PyPreprocessor
    from Python2FlowChart.Py2BlockDiagram import Py2BlockDiagram
    from Python2FlowChart.Py2PseudoCode import Py2PseudoCode
except ModuleNotFoundError:
    from PyPreprocessor import PyPreprocessor
    from Py2BlockDiagram import Py2BlockDiagram
    from Py2PseudoCode import Py2PseudoCode
import sys
import json


def main():
    args = sys.argv[1::]

    try:
        file_path = args[0]
        f = open(file_path, 'r', encoding='utf-8')
    except:
        try:
            file_path = input('path: ')
            f = open(file_path, 'r', encoding='utf-8')
        except FileNotFoundError:
            exit('wrong path')

    p = PyPreprocessor(f)
    programs_list = p.get_programs_list()
    diagram = Py2BlockDiagram.build_from_programs_list(programs_list, Py2PseudoCode, Py2BlockDiagram)

    f.close()

    f = open(f'{file_path}.json', 'w+', encoding='utf-8')
    f.write(json.dumps(diagram, indent=4))
    f.close()
    print(f'Diagram has been saved as {file_path}.json')


if __name__ == "__main__":
    main()
