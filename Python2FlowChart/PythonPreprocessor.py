import re
from PyChart.Preprocessor import Preprocessor


class PythonPreprocessor(Preprocessor):

    def _parse(self) -> None:
        # split file by '\n'
        for i in self._file:
            # del single-line comments
            i = re.sub(r'\#.*', '', i)
            striped_i = i.strip()
            if striped_i != '\n' and striped_i != '\n' and striped_i != '':                
                # single-line to many
                if self._is_control_structure(i) and striped_i[-1] != ':':
                    body = striped_i.split(':')[-1]
                    self._parsed_code.append(i.replace(body, ''))
                    body = self._set_level_of_line(body, self._get_level_of_line(i)+1)
                    self._parsed_code.append(body)
                else:
                    self._parsed_code.append(i)

    def _get_serealized_code(self, code: list) -> list:
        # creates a dict of code like {'if n == 1:': ['n+=2',print(n)']}
        levels = []
        i = 0

        while i < len(code):
            item = code[i]

            if self._is_control_structure(item):
                end = self._find_end_of_body(code, i)
                levels.append({item.strip(): self._get_serealized_code(code[i+1:end+1])})
                i = end
            else:
                levels.append(item.strip())
            
            i += 1

        return levels

    def _cut_functions(self, serealized_code: list):
        serealized_code_copy = serealized_code.copy()
        functions = []
        
        for i in range(len(serealized_code_copy)):
            if i >= len(serealized_code_copy):
                continue
            line = serealized_code_copy[i]
            if type(line) == dict:
                key = list(line.keys())[0]
                value = list(line.values())[0]
                if 'def' in key:    
                    functions.append(line)
                    functions += self._cut_functions(value).copy()
                    serealized_code.pop(i - (len(serealized_code_copy) - len(serealized_code)))
                    
        return functions

    def _find_end_of_body(self, code: list, position: int) -> int:
        last_level = self._get_level_of_line(code[position])
        end = position

        for i in code[position+1::]:
            if self._get_level_of_line(i) > last_level:
                end += 1
            else:
                break

        return end

    @staticmethod
    def _get_level_of_line(line) -> int:
        return line.count('    ')

    @staticmethod
    def _increase_level_of_line(line, increase) -> str:
        level = PythonPreprocessor._get_level_of_line(line)
        return line.replace('    ' * level, '    ' * (level+increase))

    @staticmethod
    def _set_level_of_line(line, level) -> str:
        line = line.strip()
        return '    ' * level + line

    def _find_all_veribles(self, code=None) -> list:
        if code is None:
            code = []

        if not code:
            code = self._parsed_code
        m = []
        
        # find ver statements
        for string in code:
            if type(string) == str:
                m += re.findall(r'(\w+)\.? ?= ?', string)
                m += re.findall(r'for (\w+)\.?', string)
                m += re.findall(r'while (\w+)\.?', string)
                m += re.findall(r'for (\w+)', string)
                m += re.findall(r'in +(\w+)\.?', string)
                if '(' in string:
                    m += re.findall(r'[a-zA-Z_0-9]+', string[string.index('(')+1:string[::-1].index(')')])
            else:
                value = list(string.values())[0]
                m += self._find_all_veribles(value)
        
        m = list(set(m))
        
        # remove special words
        special_words = ['True', 'False', 'and', 'len', 'input', 'print', 'int', 'range']
        for sw in special_words:
            if sw in m:
                m.remove(sw)
        # remove nums
        new_m = []
        for e in m: 
            if not e.isdigit():
                new_m.append(e)
        m = new_m

        return m

    @staticmethod
    def _get_function_name(line: str) -> str:
        line = re.sub(r'def |\:', '', line)
        output = ''
        for i in line:
            if i != '(':
                output += i
            else:
                break
        
        return output

    @staticmethod
    def _get_fun_args(line: str, fun_name='') -> list:
        line = line[line.index(f'{fun_name}(')+len(fun_name) + 1:line.index(')')] + ','
        args = []
        last_arg = ''
        for i in line:
            if i == ',' and len(last_arg) > 0:
                last_arg = last_arg.strip()
                if (last_arg.count('[') + last_arg.count(']')) % 2 == 0 and (last_arg.count('{') + last_arg.count('}')) % 2 == 0:
                    args.append(last_arg)
                    last_arg = ''
                else:
                    last_arg += i
            else:
                last_arg += i
        return args

    @staticmethod
    def _is_control_structure(line: str) -> bool:
        line = line.strip()

        return line[0:2] == 'if' or line[0:3] == 'for' or line[0:5] == 'while' or line[0:4] == 'else' or line[0:3] == 'def '

