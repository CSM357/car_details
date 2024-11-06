import http.client
import json
import sys

# Get the vehicle number from command line argument
if len(sys.argv) < 2:
    print("Vehicle number not provided.")
    sys.exit(1)

vehicle_number = sys.argv[1]  # Vehicle number passed from app.py

# Define the API connection
conn = http.client.HTTPSConnection("rto-vehicle-information-india.p.rapidapi.com")

# Define the payload with vehicle number and consent
payload = json.dumps({
    "vehicle_no": vehicle_number,
    "consent": "Y",
    "consent_text": "I hereby give my consent for Eccentric Labs API to fetch my information"
})

# Set the headers
headers = {
    'x-rapidapi-key': "5d897c86camsh2b725b03133325bp156e50jsn424b68b5e400",
    'x-rapidapi-host': "rto-vehicle-information-india.p.rapidapi.com",
    'Content-Type': "application/json"
}

# Make the POST request
try:
    conn.request("POST", "/getVehicleInfo", payload, headers)
    res = conn.getresponse()
    
    # Read the response
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))  # Parse the JSON response

    # Save the output to a JSON file
    with open('vehicle_info.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)  # Save pretty-printed JSON

    print("Vehicle information saved to vehicle_info.json")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    conn.close()  # Close the connection
