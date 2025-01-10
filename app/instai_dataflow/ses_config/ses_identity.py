from botocore.exceptions import WaiterError

class SesIdentity:
    def __init__(self, client):
        self.client = client

    def get_identity_status(self, email):
        try:
            response = self.client.get_identity_verification_attributes(
                Identities=[email]
            )
            status = response['VerificationAttributes'][email]['VerificationStatus']
            return status
        except Exception as e:
            print(f"Error getting identity status: {e}")
            return "Error"

    def verify_email_identity(self, email):
        try:
            self.client.verify_email_identity(EmailAddress=email)
        except Exception as e:
            print(f"Error verifying email identity: {e}")

    def wait_until_identity_exists(self, email):
        waiter = self.client.get_waiter('identity_exists')
        waiter.wait(Identities=[email])

    def delete_identity(self, email):
        try:
            self.client.delete_identity(Identity=email)
        except Exception as e:
            print(f"Error deleting identity: {e}")