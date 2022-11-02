from PyChart.BlockDiagram import BlockDiagram


class Py2BlockDiagram(BlockDiagram):

    @staticmethod
    def _get_struct_type(line: str) -> str:
        line = line.strip()

        if line[0:2] == 'if':
            return 'if'
        elif line[0:4] == 'else':
            return 'else'
        elif line[0:4] == 'elif':
            return 'elif'
        elif line[0:3] == 'for':
            return 'loop'
        elif line[0:5] == 'while':
            return 'loop'
        elif line[0:3] == 'def':
            return 'function'
        else:
            if 'print' in line:
                return 'output'
            else:
                return 'block'

    @staticmethod
    def _get_bd_type_of_line(line: str) -> str:
        line = line.strip()

        if line[0:2] == 'if':
            return "Условие"
        elif line[0:4] == 'else':
            return 'none'
        elif line[0:4] == 'elif':
            return "Условие"
        elif line[0:3] == 'for':
            return "Цикл for"
        elif line[0:5] == 'while':
            return "Условие"
        elif 'print' in line:
            return "Ввод / вывод"
        elif 'return ' in line:
            return "Начало / конец"
        else:
            return "Блок"
