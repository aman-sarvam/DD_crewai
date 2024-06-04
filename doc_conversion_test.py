import requests

# Specify the URL to which you want to send the data
url = "https://law-dev.sarvam.ai/api/autodraft/conversion_routes/convert"

# Set the conversion type as a string
conversion_type = "pdf_to_text"

# Specify the path to your file
file_path = "Ambuja Cement/Ambuja-Q4-FY-2023-24.pdf"

# Open the file in binary mode
with open(file_path, 'rb') as file:
    # Create a dictionary for the multipart/form-data
    files = {
        'conversion_type': (None, conversion_type),
        'file': (file_path, file, 'application/pdf')
    }

    # Make the POST request
    response = requests.post(url, files=files)

# Print the status code and response data
print("Status Code:", response.status_code)
print("Response Body:", response.text)