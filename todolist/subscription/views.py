import requests
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import json
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
# View to create a subscription
@login_required
def create_subscription(request):
    if request.method == 'POST':
        # Extract form data
        email = request.POST.get('email')
        card_type = request.POST.get('card-type')
        card_number = request.POST.get('card-number')
        expire_month = request.POST.get('expire-month')
        expire_year = request.POST.get('expire-year')
        cvv = request.POST.get('cvv')
        address_line1 = request.POST.get('address-line1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal-code')
        country = "IN"
        plan_id = request.POST.get('plan-id')

        # Generate valid start date
        start_date = (datetime.utcnow() + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%SZ')

        # PayPal access token (use your actual token)
        access_token = 'A21AAI7C10liRsjwZ-jYIkp-U3ktu0rFrj6O1IIyMPp_Bdam4ZkJsBIE2MdWbC2wR3txwZ_tqvCFFneBYH3-IwmA64nyM8SIw'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Data for PayPal API
        data = {
            "name": "Direct Payment Recurring Profile",
            "description": "Credit card payment",
            "start_date": start_date,
            "plan": {
                "id": plan_id
            },
            "payer": {
                "payment_method": "credit_card",
                "payer_info": {
                    "email": email
                },
                "funding_instruments": [
                    {
                        "credit_card": {
                            "type": card_type,
                            "number": card_number,
                            "expire_month": expire_month,
                            "expire_year": expire_year,
                            "cvv2": cvv,
                            "billing_address": {
                                "line1": address_line1,
                                "city": city,
                                "state": state,
                                "postal_code": postal_code,
                                "country_code": country
                            }
                        }
                    }
                ]
            }
        }

        # Make the request
        response = requests.post('https://api-m.sandbox.paypal.com/v1/payments/billing-agreements/', headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            # Success
            approval_url = response.json().get('links')[1]['href']
            return redirect(approval_url)
        else:
            # Handle error
            error_message = f"Error creating PayPal subscription: {response.text}"
            return HttpResponse(error_message, status=400)

    return render(request, 'subscription/subscription_page.html')




# Handle the return from PayPal (successful subscription approval)
@login_required
def paypal_return(request):
    token = request.GET.get('token')
    payer_id = request.GET.get('PayerID')

    # Get access token from PayPal
    access_token = 'your_access_token_here'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Make the request to execute the agreement
    data = {
        "payer_id": payer_id
    }

    response = requests.post(f'https://api-m.sandbox.paypal.com/v1/payments/billing-agreements/{token}/execute', headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return HttpResponse("Subscription completed successfully.")
    else:
        return HttpResponse(f"Error completing subscription: {response.text}", status=400)

# Handle the cancel from PayPal (user canceled the subscription)
@login_required
def paypal_cancel(request):
    return HttpResponse("Subscription was canceled.")

