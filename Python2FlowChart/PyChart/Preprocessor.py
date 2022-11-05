from typing import Iterable
from abc import ABC, abstractmethod


class Preprocessor(ABC):
    def __init__(self, file: Iterable) -> None:
        self._file = file
        self._parsed_code = []
        self._parse()
        self._serealized_code = self._get_serealized_code(self._parsed_code)

    @abstractmethod
    def _parse(self) -> list:
        """
            It creates list of code-lines without comments.

        Returns:
            str[]
        """
        pass

    @abstractmethod
    def _get_serealized_code(self, code: list) -> list:
        """
        Method creates a list of code like {'if n == 1:': ['n+=2',print(n)']}

        Args:
            code: list of parsed code.

        Returns:
            dict|str[]
        """
        pass

    @abstractmethod
    def _cut_functions(self, serealized_code: list):
        """
        It removes all functions from serealized-code and returns them.

        Args:
            serealized_code: list of code like {'if n == 1:': ['n+=2',print(n)']}

        Returns:
            list: [ { fun-name: body } ]
        """
        pass

    @abstractmethod
    def _get_function_name(self, line: str):
        """
        Args:
            line: function declaration line

        """
        pass

    @abstractmethod
    def _find_all_veribles(self, code: list) -> list:
        """
        It must not change input list.

        Args:
            code: parsed or serealized code.
        """
        pass

    def get_programs_list(self) -> list:
        main = self._serealized_code
        functions = self._cut_functions(main)
        programs_list = []

        for fun in functions:
            fun = fun.copy()
            body = list(fun.values())[0]
            head = list(fun.keys())[0]

            variables = self._find_all_veribles(body)
            name = self._get_function_name(head)
            variables += self._get_fun_args(head, name)

            programs_list.append({'code': body, 'name': name, 'variables': variables})

        for p in programs_list:
            if p['name'] == 'main':
                break
        else:
            if main:
                programs_list.append(
                    {'code': main, 'name': 'main', 'variables': self._find_all_veribles(main)})
            return programs_list

        return programs_list

    @abstractmethod
    def _get_fun_args(self, line: str, fun_name='') -> list:
        """
        Returns args of selected function.

        Args:
            line: function declaration line.
            fun_name: required function.

        Returns:
            str[]
        """
        pass
