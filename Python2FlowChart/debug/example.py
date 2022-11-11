def pointless_fun(dictionary, num):
    for key in dictionary:
        if len(key) == num:
            dictionary[key] += '+'
    return dictionary


print(
    pointless_fun({'a': 'fas', 'b': '2ads'}, 1)
)