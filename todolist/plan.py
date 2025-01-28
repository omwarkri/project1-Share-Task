import requests

headers = {
    'Authorization': 'Bearer A21AAKuLhbnqOHrxNMNhRAqqnqeOfawr5CW2nxnbx9ynB9yEXTQeDo1Md2Wq-3zCojpOiYnJXwS1rCNb9IjNDMA4JPl0YEfzg',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'PayPal-Request-Id': 'PLAN-18062019-001',
    'Prefer': 'return=representation',
}


# import requests

# # Replace with your actual access token
access_token = "A21AAKuLhbnqOHrxNMNhRAqqnqeOfawr5CW2nxnbx9ynB9yEXTQeDo1Md2Wq-3zCojpOiYnJXwS1rCNb9IjNDMA4JPl0YEfzg"







#Create Product Code

# url = "https://api-m.sandbox.paypal.com/v1/catalogs/products"

# headers = {
#     "Authorization": f"Bearer {access_token}",
#     "Content-Type": "application/json",
#     "Accept": "application/json",
# }

# # Product data
# data = {
#     "name": "Share ToDo Service",
#     "description": "Share Todo Who are doing same todo",
#     "type": "SERVICE",  # Can also be 'PHYSICAL' or 'DIGITAL'
#     "category": "SOFTWARE",  # Check PayPal documentation for valid categories
# }

# # Send the request
# response = requests.post(url, headers=headers, json=data)

# # Handle the response
# if response.status_code == 201:  # HTTP 201 Created
#     product = response.json()
#     print("Product created successfully!")
#     print("Product ID:", product["id"])  # This is the product_id
# else:
#     print("Error:", response.status_code, response.text)



#Create Subscription Plan

url = "https://api-m.sandbox.paypal.com/v1/billing/plans"


headers = {
    "Authorization": f"Bearer {access_token}",
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'PayPal-Request-Id': 'PLAN-18062019-001',
    'Prefer': 'return=representation',
}

# data = { "product_id": "PROD-88R37386RJ224203D", "name": "Share Todo Service Plan", "description": "Share Todo Service basic plan", "status": "ACTIVE", "billing_cycles": [ { "frequency": { "interval_unit": "MONTH", "interval_count": 1 }, "tenure_type": "TRIAL", "sequence": 1, "total_cycles": 2, "pricing_scheme": { "fixed_price": { "value": "3", "currency_code": "USD" } } }, { "frequency": { "interval_unit": "MONTH", "interval_count": 1 }, "tenure_type": "TRIAL", "sequence": 2, "total_cycles": 3, "pricing_scheme": { "fixed_price": { "value": "6", "currency_code": "USD" } } }, { "frequency": { "interval_unit": "MONTH", "interval_count": 1 }, "tenure_type": "REGULAR", "sequence": 3, "total_cycles": 12, "pricing_scheme": { "fixed_price": { "value": "10", "currency_code": "USD" } } } ], "payment_preferences": { "auto_bill_outstanding": True, "setup_fee": { "value": "10", "currency_code": "USD" }, "setup_fee_failure_action": "CONTINUE", "payment_failure_threshold": 3 }, "taxes": { "percentage": "10", "inclusive": False } }

# response = requests.post(url, headers=headers, json=data)

# if response.status_code == 201:
#     print("Plan Created Successfully:", response.json())
# else:
#     print("Error:", response.status_code, response.text)



# url = "https://api-m.sandbox.paypal.com/v1/billing/plans/P-7X9246493R192901HM6LVXEI"
# response = requests.get(url, headers=headers)

# if response.status_code == 200:
#     print("Plan get Successfully:", response.json())
# else:
#     print("Error:", response.status_code, response.text)



import requests
from requests.auth import HTTPBasicAuth

PAYPAL_CLIENT_ID="AcXonSAOFg31vhUoYrzu-chZ29YHqAXKxJA971kPSLRMrpVxJdiie97p2PACVLj24deek5WjuGTl20yR"
PAYPAL_CLIENT_SECRET="EMkEBl8Gc21xA4cuXHGKyxWz8HNaZq4MGuVjH2bZm1EF1QfI3rKhNcFXrYrnpqj3-kQX4RQcmWKhlPkZ"

# Replace with your sandbox credentials
client_id = PAYPAL_CLIENT_ID
client_secret = PAYPAL_CLIENT_SECRET

# # PayPal OAuth 2.0 Token endpoint
url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

# Headers
headers = {
    "Accept": "application/json",
    "Accept-Language": "en_US",
}

# Request body
data = {
    "grant_type": "client_credentials",
}

# Make the POST request to get the access token
response = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret))

# Check the response
if response.status_code == 200:
    access_token = response.json().get("access_token")
    print("Access Token:", access_token)
else:
    print("Failed to get token:", response.status_code, response.text)
