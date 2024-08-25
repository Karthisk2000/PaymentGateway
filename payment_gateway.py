import json
import requests
import logging
import io
from flask import Flask, render_template, request, Response
from requests.auth import HTTPBasicAuth


app = Flask(__name__)
# Configure logging
logging.basicConfig(
    filename='app.log',  # Log file location
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@app.route('/api/v1/payment_gateway_webpage', methods = ['GET'])
def payment_gateway_webpage():
    """
    Function to redirect the payment validation page.
    @return: Render the payment_validation template.
    """

    return render_template('payment_validation.html')


@app.route('/api/v1/payment_gateway', methods=['GET'])
def payment_gateway():
    """
    Function to process the payment through Elavon.
    @return: JSON response with the transaction result.
    """
    
    # Extract payment details from the request
    card_number = request.args.get('card_number')
    expiry_date = request.args.get('expiry_date')
    cvv = request.args.get('cvv')
    amount = request.args.get('amount')

    print(f'{card_number}: {expiry_date}: {cvv}: {amount}')

    # Replace these with your Elavon production credentials
    API_URL = 'https://api.convergepay.com/hosted-payments/transaction_token'
    MERCHANT_ID = '2492619'
    USER_ID = '8042636558api'
    PIN = 'D0W2QS8PC3ELP94CZAWTRMMUU0ZY7C0QF31XJFDX5LWBETT2XX468VD81V1X58GS'

    headers = {
        'Content-Type': 'application/xml',
    }

    xml_payload = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <txn>
        <ssl_merchant_id>{MERCHANT_ID}</ssl_merchant_id>
        <ssl_user_id>{USER_ID}</ssl_user_id>
        <ssl_pin>{PIN}</ssl_pin>
        <ssl_transaction_type>ccsale</ssl_transaction_type>
        <ssl_card_number>{card_number}</ssl_card_number>
        <ssl_exp_date>{expiry_date}</ssl_exp_date>
        <ssl_amount>{amount}</ssl_amount>
        <ssl_cvv>{cvv}</ssl_cvv>
        <ssl_test_mode>false</ssl_test_mode>
    </txn>
    """

    # Logging the XML Payload
    print("XML Payload being sent:")
    print(xml_payload)

    # Send the request
    response = requests.post(API_URL, headers=headers, data=xml_payload)

    print(f'\n Response text: {response.text}')
    print(f'\n Response status_code: {response.status_code}')

    if response.status_code == 200 and '<errorCode>' not in response.text:
        print("Payment successful!")
        data = {'status': 'success', 'message': response.text}
    else:
        print("Payment failed!")
        data = {'status': 'failed', 'message': response.text}

    return Response(
        response=json.dumps({
            'client_status_code': response.status_code,
            'message': data['status'],
            'data': data
        }),
        status=response.status_code,
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5007', debug=True)
    