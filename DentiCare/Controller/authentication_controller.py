
from DentiCare.Model.authentication_model import AuthenticationModel


class AuthenticationController:
    def __init__(self):
        self.model = AuthenticationModel() #instantiate the model

    def login(self, username, password):
        # checks empty fields via validate credentials fucntion
        if not self._validate_credentials(username, password):
            return {
                'success': False,
                'staff_id': None,
                'role': None,
                'message': 'Username and password cannot be empty'
            }

        #authenticate via model
        result = self.model.authenticate(username, password)

        if result:
            staff_id = int(result['StaffID'])
            role = result['Role'].lower().strip()

            # Validate role then returns result in dictionary
            if role not in ['admin', 'frontdesk']:
                return {
                    'success': False,
                    'staff_id': None,
                    'role': None,
                    'message': f'Invalid role: {role}'
                }

            return {
                'success': True,
                'staff_id': staff_id,
                'role': role,
                'message': 'Login successful'
            }
        else:
            return {
                'success': False,
                'staff_id': None,
                'role': None,
                'message': 'Invalid username or password'
            }

    def _validate_credentials(self, username, password):
        #checks if current cred is not empty
        return bool(username and password)





