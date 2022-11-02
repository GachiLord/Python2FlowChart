from random import shuffle
from uuid import uuid1
from os import listdir

no_test_error_msg = 'Теста не существует или введен неправильный номер'


def get_parsed_test(f):
    test = {}

    cur_task = []
    for line in f:
        line = line.strip()

        if not line.isdigit():
            cur_task.append(line)
        else:
            test[line + '_' + uuid1().hex] = cur_task
            cur_task = []

    return test


def game(test_name):
    try:
        f = open(f'tests/{test_name}.txt')
    except FileNotFoundError:
        exit(no_test_error_msg)
    tasks = get_parsed_test(f)
    test_ids = list(tasks.keys())
    shuffle(test_ids)

    score = 0
    for test_id in test_ids:
        task = tasks[test_id]
        question = task.copy()[0]
        task = task[1::]
        right_answer = task.copy()[int(test_id.split('_')[0])-1]
        shuffle(task)

        print(f'Вопрос: {question}')
        for answer_index in range(0, len(task)):
            print(f'{answer_index+1} -> {task[answer_index]}')

        if right_answer == task[int(input('Введите номер ответа: \n').strip())-1]:
            score += 1

    f.close()
    return f'{score}/{str(len(tasks))}'


def update_leader_board(user_name, score, test_name):
    f = open('leader_board.txt', 'r')
    f_string = f.read()
    f.close()
    f_string += f'{user_name} -> {score} -> {test_name}\n'
    f = open('leader_board.txt', 'w+')
    f.write(f_string)
    f.close()
    return f_string


def main():
    user_name = input('Введите имя: ')
    tests = listdir('tests/')
    for i in range(len(tests)):
        tests[i] = tests[i].replace('.txt', '')
    for i in range(0, len(tests)):
        print(f'{i+1} -> {tests[i]}')

    try:
        test_index = int(input('Введите номер теста:\n')) - 1
        if test_index < 0:
            raise IndexError
        test_name = tests[test_index]
    except IndexError:
        exit(no_test_error_msg)

    score = game(test_name)
    print(update_leader_board(user_name, score, test_name))
    

if __name__ == '__main__':
    main()