import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from dropbox_sign import Configuration, ApiClient, ApiException
from dropbox_sign.api.signature_request_api import SignatureRequestApi
from dropbox_sign.models import (
    SignatureRequestSendWithTemplateRequest,
    SubSignatureRequestTemplateSigner
)

load_dotenv()

app = Flask(__name__)
CORS(app)

configuration = Configuration(username=os.getenv("DROPBOX_API_KEY"))

@app.route("/send-consent-form", methods=["POST"])
def send_consent_form():
    data = request.json

    with ApiClient(configuration) as api_client:
        signature_api = SignatureRequestApi(api_client)

        # Create signers matching your template roles exactly
        signer1 = SubSignatureRequestTemplateSigner(
            role="Supervisee",
            name=data.get("signer1_name"),
            email_address=data.get("signer1_email"),
        )
        signer2 = SubSignatureRequestTemplateSigner(
            role="Supervisor",
            name=data.get("signer2_name"),
            email_address=data.get("signer2_email"),
        )
        
        # ADDED: Hardcoded third signer for the Admin role
        signer3 = SubSignatureRequestTemplateSigner(
            role="Admin",
            name="Seanna Neo",
            email_address="snyq@nus.edu.sg"
        )

        signature_request = SignatureRequestSendWithTemplateRequest(
            template_ids=[os.getenv("DROPBOX_TEMPLATE_ID")],
            subject="Consent Form",
            message="Please review and sign the supervision contract. For any issues, please contact john.yap@nus.edu.sg"
            # UPDATED: Added the third signer to the list
            signers=[signer1, signer2, signer3],
            # REMOVED: The ccs parameter is no longer needed
            test_mode=True  # Set to False in production
        )

        try:
            response = signature_api.signature_request_send_with_template(
                signature_request_send_with_template_request=signature_request
            )
            return jsonify({
                "success": True,
                "request_id": response.signature_request.signature_request_id
            })
        except ApiException as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400

if __name__ == "__main__":
    app.run(debug=True)


