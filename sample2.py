def reverse_list(lst):
    reversed_list = []
    for i in range(len(lst) - 1, -1, -1):
        reversed_list.append(lst[i])
    return reversed_list

numbers = input("Enter numbers separated by spaces: ")
my_list = list(map(int, numbers.split()))
#my_list.sort()
my_list = reverse_list(my_list)
print(my_list)
