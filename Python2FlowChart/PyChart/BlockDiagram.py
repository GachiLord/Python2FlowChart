import uuid
from abc import ABC, abstractmethod


class BlockDiagram(ABC):
    _diagram = {
        "blocks": [],
        "arrows": [],
        "x0": 0,
        "y0": 100,
    }

    _direction = {
        'UP': 0,
        'RIGHT': 1,
        'DOWN': 2,
        'LEFT': 3,
    }

    _last_x = 0
    _last_y = 0
    _last_if_id_list = []
    _last_arrow_pos_delta = 15

    def __init__(self,
                 pseudocode,
                 code_tree: list,
                 variables: list,
                 base_coor=None,
                 name='main',
                 start_block_index=0) -> None:

        if base_coor is None:
            base_coor = {'y': 0, 'x': 0}

        self._pseudocode = pseudocode
        self._last_x = base_coor['x']
        self._last_y = base_coor['y']
        self._name = name
        self._code_tree = self._connect_same_lines_in_tree(code_tree)
        self._variables = variables
        self._forbidden_aria = []
        self._start_block_index = start_block_index

    def build(self) -> dict:
        name = self._name
        if name == 'main':
            name = ''

        if self._variables:
            self._diagram['blocks'].insert(0, self._form_block(','.join(self._variables),
                                                               {'y': self._last_y,
                                                                'x': self._last_x},
                                                               uuid.uuid1().hex, '0',
                                                               'Ввод / вывод'))
        self._diagram['blocks'].insert(0,
                                       self._form_block(f'Начало {name}',
                                                        {'y': self._last_y - 100, 'x': self._last_x},
                                                        uuid.uuid1().hex,
                                                        '0',
                                                        'Начало / конец'))
        self._diagram['blocks'] += self._add_blocks(self._code_tree)
        if self._name == 'main':
            self._diagram['blocks'].append(
                self._form_block('Конец',
                                 {'y': self._last_y + 100, 'x': self._last_x},
                                 uuid.uuid1().hex,
                                 '0',
                                 'Начало / конец'))

        self._set_block_indexes()
        self._align_if_else_bodies()
        self._set_all_forbidden_areas()
        self._connect_all_blocks_by_arrows()

        return self._diagram

    @staticmethod
    def build_from_programs_list(programs: list, pseudocode, diagram_class):
        y = 0
        last_index = 0
        super_diagram = {
            "blocks": [],
            "arrows": [],
            "x0": 0,
            "y0": 0,
        }

        for prog in programs:
            diagram = diagram_class(pseudocode, prog['code'], prog['variables'], {'y': y, 'x': 0}, prog['name'], last_index)
            diagram = diagram.build()

            # find last index
            last_index = max([b['index'] for b in diagram['blocks']]) + 1

            super_diagram['blocks'] += diagram['blocks']
            super_diagram['arrows'] += diagram['arrows']
            y += len(diagram['blocks']) * 100

            # delete last blocks and arrows, because of pythons vars are links xD.
            diagram_class._diagram['blocks'] = []
            diagram_class._diagram['arrows'] = []

        return super_diagram

    def debug(self) -> dict:
        self.build()
        return {'diagram': self._diagram, 'forb_area': self._forbidden_aria}

    def _form_block(self, text='', pos=None, cur_el_id='0', parent_id='0', block_type='none'):
        if pos is None:
            pos = {'x': 0, 'y': 0}
        if block_type == 'none':
            block_type = self._get_bd_type_of_line(text.strip().split('\n')[0])
        text = text.strip()
        code = text
        struct_type = self._get_struct_type(code)
        size = BlockDiagram._get_size_of_block(text.split('\n'))
        if block_type == 'none':
            return
        text = self._to_pseudocode(text)
        if text.strip() == '':
            return

        block = {
            "code": code,
            "cur_el_id": cur_el_id,
            "parent_id": parent_id,
            "struct_type": struct_type,
            "x": pos['x'],
            "y": pos['y'],
            "text": text,
            "width": size['width'],
            "height": size['height'],
            "type": block_type,
            "isMenuBlock": False,
            "fontSize": 14,
            "textHeight": 14,
            "isBold": False,
            "isItalic": False,
            "textAlign": "center",
            "labelsPosition": 1
        }

        return block

    @abstractmethod
    def _get_struct_type(line: str) -> str:
        """
        It returns code-line type.
        For example: “if a > 4" => 'if'

        Args:
            line: code line

        Returns:
            'if', 'else', 'elif', 'loop', 'function', 'output', 'block'
        """
        if line:
            return 'block'

    @staticmethod
    def _get_size_of_block(lines: list) -> dict:
        height = len(lines) * 8
        width = 100

        for line in lines:
            if type(line) == str:
                line = line.strip()
                width = max(width, len(line) * 9)

        return {'width': max(100, width), 'height': max(height, 40)}

    def _is_point_free(self, position: dict) -> bool:
        x = position['x']
        y = position['y']
        for pos in self._forbidden_aria:
            if not ((x < pos['x0'] or x > pos['x1']) or (y < pos['y0'] or y > pos['y1'])):
                return False
        return True

    def _is_path_free(self, position: dict, coor='y') -> bool:
        coor1 = position['start']
        coor2 = position['end']

        if coor2[coor] - coor1[coor] > 0:
            direction_coef = 1
        else:
            direction_coef = -1

        coor1[coor] += 25 * direction_coef
        begin = 0
        end = abs(coor2[coor] - coor1[coor])
        while begin <= end:
            if self._is_point_free(coor1):
                coor1[coor] += 1 * direction_coef
            elif coor1[coor] == coor2[coor]:
                return True
            else:
                return False

            begin += 1
        return True

    @abstractmethod
    def _get_bd_type_of_line(line: str) -> str:
        """
        It returns line type for BlockDiagram redactor.

        Args:
            line: code-line

        Returns:
            'Условие', 'none', 'Цикл for', 'Ввод / вывод', 'Начало / конец', 'Блок'
        """
        if line:
            return 'Блок'

    def _set_forbidden_aria(self, position: dict, size: dict) -> None:
        x0 = position['x'] - size['width'] / 2
        x1 = position['x'] + size['width'] / 2
        y0 = position['y'] - size['height'] / 2
        y1 = position['y'] + size['height'] / 2
        self._forbidden_aria.append({'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1})

    def _set_all_forbidden_areas(self) -> None:
        for block in self._diagram['blocks']:
            self._set_forbidden_aria({'x': block['x'], 'y': block['y']},
                                     {'width': block['width'], 'height': block['height']})

    def _add_blocks(self, code_tree: list, parent_id='0') -> list:
        blocks = []

        for code in code_tree:
            cur_el_id = uuid.uuid1().hex
            if type(code) == str:
                self._last_y += 100
                block = self._form_block(code, {'x': 0, 'y': self._last_y}, cur_el_id, parent_id)
                if block is not None:
                    blocks.append(block)
                else:
                    self._last_y -= 100
            else:
                self._last_y += 100
                key = list(code.keys())[0]
                value = list(code.values())[0]
                block = self._form_block(key, {'x': 0, 'y': self._last_y}, cur_el_id, parent_id)
                if 'if ' in key:
                    self._last_if_id_list.append(cur_el_id)
                if block is not None and 'elif' not in key:
                    blocks.append(block)
                    blocks += self._add_blocks(value, cur_el_id)
                elif 'else' == key.replace(':', '').strip():
                    self._last_y -= 100
                    blocks += self._add_blocks(value, self._last_if_id_list[-1] + '-else')
                    self._last_if_id_list.pop()
                elif 'elif' in key:
                    self._last_y -= 100
                    blocks += self._add_blocks(value, self._last_if_id_list[-1] + '-else')
                    self._last_if_id_list.pop()
                else:
                    self._last_y -= 100
                    blocks += self._add_blocks(value, self._last_if_id_list[-1])

        return blocks

    def _connect_same_lines_in_tree(self, code_tree: list) -> list:
        tree = []
        lines = ''

        for i in range(len(code_tree)):
            line = code_tree[i]
            if type(line) == str:
                lines += line + '\n'
                last_type = self._get_bd_type_of_line(line)
                if i + 1 < len(code_tree):
                    next_line = code_tree[i + 1]
                    if type(next_line) != str:
                        tree.append(lines)
                        lines = ''
                    elif self._get_bd_type_of_line(next_line) not in ['Блок', 'Ввод / вывод',
                                                                      'Дисплей'] \
                            or last_type != self._get_bd_type_of_line(
                            next_line):
                        tree.append(lines)
                        lines = ''
                else:
                    tree.append(lines)
                    lines = ''
            else:
                tree.append({list(line.keys())[0]: self._connect_same_lines_in_tree(list(line.values())[0])})

        return tree

    def _set_block_indexes(self) -> None:
        count = self._start_block_index
        for block in self._diagram['blocks']:
            block['index'] = count
            count += 1

    def _to_pseudocode(self, lines: str) -> str:
        return self._pseudocode.to_pseudocode(lines)

    def _draw_arrow(self, start_end_pos: dict, start_end_indexes: dict, direction: dict) -> None:
        dirs = self._direction
        delta = self._last_arrow_pos_delta - 1
        arrow = {
            "startIndex": start_end_indexes['start'],
            "endIndex": start_end_indexes['end'],
            "startConnectorIndex": direction['start'],
            "endConnectorIndex": direction['end'],
            "nodes": [],
            "counts": []
        }

        x1 = start_end_pos['start']['x']
        y1 = start_end_pos['start']['y']
        x2 = start_end_pos['end']['x']
        y2 = start_end_pos['end']['y']

        x_direction_coef = 1
        if direction['start'] == dirs['LEFT']:
            x_direction_coef = -1

        if direction['start'] == dirs['LEFT'] and direction['end'] == dirs['RIGHT']:
            arrow['nodes'].append({'x': x1, 'y': y1})

            while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x2, 'y': y1}}, 'x'):
                y1 += 50

            arrow['nodes'].append({'x': x1 + delta, 'y': y1})

            while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x1, 'y': y2}}, 'y'):
                x1 += 50

            arrow['nodes'].append({'x': x1 + delta, 'y': y1})
            arrow['nodes'].append({'x': x1 + delta, 'y': y2})
            arrow['nodes'].append({'x': x2, 'y': y2})

        elif direction['start'] == dirs['DOWN'] and direction['end'] == dirs['RIGHT']:
            arrow['nodes'].append({'x': x1, 'y': y1})
            y1 += 50
            arrow['nodes'].append({'x': x1, 'y': y1})

            while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x1, 'y': y2}}, 'y'):
                x1 += 50 * x_direction_coef

            arrow['nodes'].append({'x': x1 + delta, 'y': y1})
            arrow['nodes'].append({'x': x1 + delta, 'y': y2})
            arrow['nodes'].append({'x': x2, 'y': y2})

        else:
            arrow['nodes'].append({'x': x1, 'y': y1})
            if not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x2, 'y': y2}}):
                while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x1, 'y': y2}}):
                    x1 += 30 * x_direction_coef

                arrow['nodes'].append({'x': x1 + delta, 'y': y1})
                arrow['nodes'].append({'x': x1 + delta, 'y': y2 - 40})
                arrow['nodes'].append({'x': x2, 'y': y2 - 40})
                arrow['nodes'].append({'x': x2, 'y': y2 + 40})
            else:
                arrow['nodes'].append({'x': x2, 'y': y2})

        for _ in arrow['nodes']:
            arrow['counts'].append(1)
        self._last_arrow_pos_delta -= 1
        self._diagram['arrows'].append(arrow)

    def _connect_blocks(self, block1: dict, block2: dict, direction: dict) -> None:
        self._draw_arrow({'start': {'y': block1['y'], 'x': block1['x']}, 'end': {'y': block2['y'], 'x': block2['y']}},
                         {'start': block1['index'], 'end': block2['index']}, direction)

    def _align_if_else_bodies(self) -> None:
        if_structs = self._find_blocks_by_property('struct_type', 'if')

        for if_struct in if_structs:
            struct_id = if_struct['cur_el_id']

            if_body = self._find_blocks_by_property('parent_id', struct_id)
            else_body = self._find_blocks_by_property('parent_id', struct_id + '-else')
            max_width_if_body = max([i['width'] for i in if_body])

            base_x = if_struct['x']
            for block in if_body:
                block['x'] = base_x + max_width_if_body

            base_y = if_body[0]['y']
            for block in else_body:
                block['y'] = base_y
                block['x'] = base_x - max_width_if_body
                base_y += 100

    def _find_blocks_by_property(self, block_property: str, value, required_field='', block_list=None) -> list:
        if block_list is None:
            block_list = []
        if not block_list:
            block_list = self._diagram['blocks']
        output = []

        for block in block_list:
            if block[block_property] == value:
                if required_field != '':
                    output.append(block[required_field])
                else:
                    output.append(block)

        return output

    def _connect_all_blocks_by_arrows(self, parent_id='0') -> None:
        blocks = self._find_blocks_by_property('parent_id', parent_id)
        dirs = self._direction

        for i in range(len(blocks)):
            b_c = blocks[i]
            if i + 1 <= len(blocks) - 1:
                b_n = blocks[i + 1]
            else:
                b_n = None
            struct_type = b_c['struct_type']
            cur_id = b_c['cur_el_id']
            if (struct_type == 'block' or struct_type == 'output') and b_n is not None:
                self._connect_blocks(b_c, b_n, {'start': dirs['DOWN'], 'end': dirs['UP']})
            else:
                if struct_type == 'loop':
                    body = self._find_blocks_by_property('parent_id', cur_id)
                    is_last_close_child_loop = body[-1]['struct_type'] == 'loop'

                    self._connect_blocks(b_c, body[0], {'start': dirs['DOWN'], 'end': dirs['UP']})
                    self._connect_all_blocks_by_arrows(cur_id)
                    if b_n is not None:
                        self._connect_blocks(b_c, b_n, {'start': dirs['LEFT'], 'end': dirs['UP']})

                    if is_last_close_child_loop:
                        self._connect_blocks(body[-1], b_c, {'start': dirs['LEFT'], 'end': dirs['RIGHT']})

                    for item in self._find_farthest_children([b_c]):
                        if item['struct_type'] == 'if':
                            self._connect_blocks(item, b_c, {'start': dirs['LEFT'], 'end': dirs['RIGHT']})
                        elif not is_last_close_child_loop:
                            self._connect_blocks(item, b_c, {'start': dirs['DOWN'], 'end': dirs['RIGHT']})

                if struct_type == 'if':
                    if_body = self._find_blocks_by_property('parent_id', cur_id)
                    else_body = self._find_blocks_by_property('parent_id', cur_id + '-else')

                    if len(else_body) > 0:
                        self._connect_blocks(b_c, else_body[0], {'start': dirs['LEFT'], 'end': dirs['UP']})
                    self._connect_blocks(b_c, if_body[0], {'start': dirs['RIGHT'], 'end': dirs['UP']})

                    self._connect_all_blocks_by_arrows(cur_id)
                    self._connect_all_blocks_by_arrows(cur_id + '-else')

                    for item in self._find_farthest_children([b_c]):
                        if item == b_c and b_n is not None:
                            self._connect_blocks(item, b_n, {'start': dirs['LEFT'], 'end': dirs['UP']})
                        elif b_n is not None:
                            self._connect_blocks(item, b_n, {'start': dirs['DOWN'], 'end': dirs['UP']})

    def _find_farthest_children(self, blocks: list) -> list:
        children = []
        if len(blocks) == 0:
            return []

        for block in blocks:
            struct_type = block['struct_type']
            body = self._find_blocks_by_property('parent_id', block['cur_el_id'])
            else_body = self._find_blocks_by_property('parent_id', block['cur_el_id'] + '-else')

            if struct_type == 'loop':
                if len(body) > 0:
                    children += self._find_farthest_children([body[-1]])
            elif struct_type == 'if':
                if len(body) > 0:
                    children += self._find_farthest_children([body[-1]])
                if len(else_body) > 0:
                    children += self._find_farthest_children([else_body[-1]])
                else:
                    children += [block]

            else:
                children.append(block)

        return children
