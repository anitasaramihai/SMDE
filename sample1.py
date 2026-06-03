numbers = input("Enter numbers separated by spaces: ")
my_list = list(map(int, numbers.split()))
my_list.sort()
print(my_list)
