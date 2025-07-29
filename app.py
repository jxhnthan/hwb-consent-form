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

# Initialize Dropbox Sign API configuration
configuration = Configuration(username=os.getenv("DROPBOX_API_KEY"))

@app.route("/send-consent-form", methods=["POST"])
def send_consent_form():
    data = request.json or {}

    supervisee_name = data.get("signer1_name")
    supervisee_email = data.get("signer1_email")
    supervisor_name = data.get("signer2_name")
    supervisor_email = data.get("signer2_email")

    # Validate required fields
    if not all([supervisee_name, supervisee_email, supervisor_name, supervisor_email]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    with ApiClient(configuration) as api_client:
        signature_api = SignatureRequestApi(api_client)

        # Map to template roles
        signer1 = SubSignatureRequestTemplateSigner(
            role="Supervisee",
            name=supervisee_name,
            email_address=supervisee_email,
        )
        signer2 = SubSignatureRequestTemplateSigner(
            role="Supervisor",
            name=supervisor_name,
            email_address=supervisor_email,
        )
        signer3 = SubSignatureRequestTemplateSigner(
            role="Admin",
            name="Seanna Neo",
            email_address="snyq@nus.edu.sg"
        )

        # Create the signature request with the updated subject/title
        signature_request = SignatureRequestSendWithTemplateRequest(
            template_ids=[os.getenv("DROPBOX_TEMPLATE_ID")],
            subject="Supervision Contract",          # Email subject
            title="Supervision Contract",            # Internal document title
            message=(
                "Please review and sign the supervision contract.\n"
                "For any issues, please contact john.yap@nus.edu.sg or snyq@nus.edu.sg"
            ),
            signers=[signer1, signer2, signer3],
            test_mode=False  # Set to False for production
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
            return jsonify({"success": False, "error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)



