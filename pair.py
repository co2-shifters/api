import json

# Your JSON data
data = {
    "number": [
        7, 14, 3, 18, 9, 2, 16, 11, 4, 10, 1, 20, 5, 8, 12, 15, 6, 13, 17, 19
    ]
}

numbers = data["number"]

group_size = int(input("Enter the number of elements to group together: "))

if group_size < 2:
    print("Group size must be at least 2.")
else:
    lowest_group = None
    lowest_count = float('inf')

    for i in range(len(numbers) - group_size + 1):
        group = numbers[i:i + group_size]
        count = sum(group)
        if count < lowest_count:
            lowest_count = count
            lowest_group = group
        print(f"Group {i+1}: {group}, Count: {count}")

    print(f"The group with the lowest sum is: {lowest_group} with a count of {lowest_count}")
