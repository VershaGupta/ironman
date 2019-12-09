# -- coding: utf-8 --
# Created by IronMan Development Team
# Copyright 2019 IronMan Inc. All rights reserved.
#


class AuthenticationApi:

    def __init__(self, lr_object):
        """
        :param lr_object: this is the reference to the parent IronMan object.
        """
        self._lr_object = lr_object


    def retrieve_user_identity(self, access_token, fields = ''):
        """This API will return all the accepted privacy policies for the user by providing the access_token of that user.
        
        Args:
            access_token: Uniquely generated identifier key by IronMan that is activated after successful authentication.

        """

        if(self._lr_object.is_null_or_whitespace(access_token)):
            raise Exception(self._lr_object.get_validation_message("access_token"))

        if(not self._lr_object.is_null_or_whitespace(fields)):
            query_parameters["fields"] = fields

        query_parameters = {}
        query_parameters["access_token"] = access_token
        query_parameters["apiKey"] = self._lr_object.get_api_key()

        resource_path = "/v1/profile"

        return self._lr_object.execute("GET", resource_path, query_parameters, None)

    def register(self, payload, verification_url=None, email_template=None):
        """This API creates a user in the database as well as sends a verification email to the user.
        
	
        """
        if(payload is None):
            raise Exception(self._lr_object.get_validation_message("payload"))


        query_parameters = {}
        query_parameters["apiKey"] = self._lr_object.get_api_key()
        if(not self._lr_object.is_null_or_whitespace(email_template)):
            query_parameters["emailTemplate"] = email_template
        if(not self._lr_object.is_null_or_whitespace(verification_url)):
            query_parameters["verificationUrl"] = verification_url

        resource_path = "/v1/register"
        
        return self._lr_object.execute("POST", resource_path, query_parameters, payload)
		
	def login(self, payload, verification_url=None, email_template=None):
            """This API is used to login a user.
            
            Args:
                payload: Model Class containing Definition of payload for Auth User Registration API
                email_template: Email template name               
                verification_url: Email verification url
            
          
            """
            if(payload is None):
                raise Exception(self._lr_object.get_validation_message("payload"))


            query_parameters = {}
            query_parameters["apiKey"] = self._lr_object.get_api_key()
            if(not self._lr_object.is_null_or_whitespace(email_template)):
                query_parameters["emailTemplate"] = email_template
            if(not self._lr_object.is_null_or_whitespace(verification_url)):
                query_parameters["verificationUrl"] = verification_url

            resource_path = "/v1/login"      
            
            return self._lr_object.execute("POST", resource_path, query_parameters, payload)	

    

    def resend_email_verification(self, email):
        """This API resends the verification email to the user.
        
        Args:
            email: user's email
 
		
  
        """

        if(self._lr_object.is_null_or_whitespace(email)):
            raise Exception(self._lr_object.get_validation_message("email"))

        query_parameters = {}
        query_parameters["apiKey"] = self._lr_object.get_api_key()

        body_parameters = {}
        body_parameters["email"] = email

        resource_path = "/v1/email/resendverify"
        return self._lr_object.execute("PUT", resource_path, query_parameters, body_parameters)

 
    def reset_user_password(self, resetPasswordEmailTemplate, resetToken, password):
        """This API reset a user's password.

        Args:
            resetPasswordEmailTemplate: The name of the template to be used to format the confirmation email sent to your user.
            resetToken: The reset token retrieved from the recovery email previously sent to your user.
            password: The new password to be used to authenticate your user.

        Returns:
            Response containing Definition of Reset user password
        """

        query_parameters = {}
        query_parameters["apiKey"] = self._lr_object.get_api_key()

        query_parameters = {}
        query_parameters["resetPasswordEmailTemplate"] = resetPasswordEmailTemplate

        body_parameters = {}
        body_parameters["resetToken"] = resetToken

        body_parameters = {}
        body_parameters["password"] = password

        resource_path = "/v1/password/reset"
        return self._lr_object.execute("PUT", resource_path, query_parameters, body_parameters)


    def change_user_password(self, access_token, oldPassword, newPassword):
        """This API change a user's password.

        Args:
            access_token: A access token.
            oldPassword: The current password used to authenticate your user.
            newPassword: The new password to be used to authenticate your user.

        Returns:
            Response containing Definition of change user password
        """

        query_parameters = {}
        query_parameters["apiKey"] = self._lr_object.get_api_key()

        query_parameters = {}
        query_parameters["access_token"] = access_token

        body_parameters = {}
        body_parameters["oldPassword"] = oldPassword

        body_parameters = {}
        body_parameters["newPassword"] = newPassword

        resource_path = "/v1/password/change"
        return self._lr_object.execute("PUT", resource_path, query_parameters, body_parameters)
