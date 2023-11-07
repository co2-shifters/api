import json

# Load JSON data from the "forecast.json" file
with open('api/forecast.json', 'r') as file:
    data = json.load(file)

# Extract the "forecast" data
forecast = data["forecast"]

# Sort the forecast data by carbon intensity in ascending order
forecast.sort(key=lambda x: x["carbonIntensity"])

# Calculate the highest carbon intensity
highest_intensity = forecast[-1]["carbonIntensity"]

# Initialize a list to store the top 3 best times
top_3 = []

# Loop through the forecast data to find the top 3 best times
for i, entry in enumerate(forecast):
    carbon_intensity = entry["carbonIntensity"]
    datetime = entry["datetime"]
    
    # Calculate the percentageSaved using the overall highest intensity
    percentage_saved = 100 - (carbon_intensity / highest_intensity * 100)

    # Check if this time is in the top 3
    if len(top_3) < 3 or percentage_saved > top_3[-1]["percentageSaved"]:
        top_3.append({
            "ranking": len(top_3) + 1,
            "carbonIntensity": carbon_intensity,
            "time": datetime,
            "percentageSaved": round(percentage_saved, 2)
        })

    # Check if the next hour has low carbon intensity
    if i + 1 < len(forecast) and forecast[i + 1]["carbonIntensity"] < top_3[-1]["carbonIntensity"]:
        carbon_intensity_next = forecast[i + 1]["carbonIntensity"]
        percentage_saved_next = 100 - (carbon_intensity_next / highest_intensity * 100)

        top_3.append({
            "ranking": len(top_3) + 1,
            "carbonIntensity": carbon_intensity_next,
            "time": forecast[i + 1]["datetime"],
            "percentageSaved": round(percentage_saved_next, 2)
        })

    # Sort the list of top times by percentageSaved
    top_3.sort(key=lambda x: x["percentageSaved"], reverse=True)

    # If we have found 3 top times, break the loop
    if len(top_3) >= 3:
        break

# Create a JSON output with the top 3 best times and the highest overall intensity
output_data = {
    "top3BestTimes": top_3,
    "highestOverallIntensity": highest_intensity
}

# Create a JSON output
output_json = json.dumps(output_data, indent=4)

# Print the JSON output
print(output_json)
