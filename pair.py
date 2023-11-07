import json

# Load JSON data from the "forecast.json" file
with open('api/forecast.json', 'r') as file:
    data = json.load(file)

forecast = data["forecast"]
2
group_size = int(input("Enter the number of elements to group together: "))

if group_size < 2:
    print("Group size must be at least 2.")
else:
    data_list = forecast  # Convert JSON object to a list (if not already)
    lowest_group = None
    lowest_count = float('inf')

    for i in range(len(data_list) - group_size + 1):
        group = data_list[i:i + group_size]
        count = sum(item["carbonIntensity"] for item in group)
        first_datetime = group[0]["datetime"]
        if count < lowest_count:
            lowest_count = count
            lowest_group = group
        print(f"First Datetime: {first_datetime}, CarbonIntensity Sum: {count}")

    print(f"The group with the lowest CarbonIntensity sum is: {lowest_group} with a sum of {lowest_count}")
