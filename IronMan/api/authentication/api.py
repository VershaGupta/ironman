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


    def retrieve_user_identity(self, access_token, fields):
        """This API will return all the accepted privacy policies for the user by providing the access_token of that user.
        
        Args:
            access_token: Uniquely generated identifier key by IronMan that is activated after successful authentication.
		
        Returns:
            Complete Policy History data
        15.2
        """

        if(self._lr_object.is_null_or_whitespace(access_token)):
            raise Exception(self._lr_object.get_validation_message("access_token"))

        query_parameters = {}
        query_parameters["access_token"] = access_token
        query_parameters["apiKey"] = self._lr_object.get_api_key()

        resource_path = "/v1/profile"

        return self._lr_object.execute("GET", resource_path, query_parameters, None)

    def register(self, payload, verification_url=None, email_template=None):
        """This API creates a user in the database as well as sends a verification email to the user.
        
        Args:
            payload: Model Class containing Definition of payload for Auth User Registration API
            sott: IronMan Secured One Time Token
            email_template: Email template name
            fields: The fields parameter filters the API response so that the response only includes a specific set of fields
            options: PreventVerificationEmail (Specifying this value prevents the verification email from being sent. Only applicable if you have the optional email verification flow)
            verification_url: Email verification url
            welcome_email_template: Name of the welcome email template
		
        Returns:
            Response containing Definition of Complete Validation, UserProfile data and Access Token
        17.1.1
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
        print (resource_path)
        
        return self._lr_object.execute("POST", resource_path, query_parameters, payload)

    

    def resend_email_verification(self, email):
        """This API resends the verification email to the user.
        
        Args:
            email: user's email
            email_template: Email template name
            verification_url: Email verification url
		
        Returns:
            Response containing Definition of Complete Validation data
        17.3
        """

        if(self._lr_object.is_null_or_whitespace(email)):
            raise Exception(self._lr_object.get_validation_message("email"))

        query_parameters = {}
        query_parameters["apiKey"] = self._lr_object.get_api_key()

        body_parameters = {}
        body_parameters["email"] = email

        resource_path = "/v1/email/resendverify"
        return self._lr_object.execute("PUT", resource_path, query_parameters, body_parameters)
    
     def forgot(self, payload, resetPasswordUrl=None, emailTemplate=None):
        """This API send a user a reset password email.
        
        Args:
            payload: Model Class containing Definition of payload for Auth User Registration API
            sott: IronMan Secured One Time Token
            email_template: Email template name
            fields: The fields parameter filters the API response so that the response only includes a specific set of fields
            options: PreventVerificationEmail (Specifying this value prevents the verification email from being sent. Only applicable if you have the optional email verification flow)
            verification_url: Email verification url
		
        Returns:
            IsPosted true
        17.1.1
        """
        if(payload is None):
            raise Exception(self._lr_object.get_validation_message("payload"))


        query_parameters = {}
        query_parameters["apiKey"] = self._lr_object.get_api_key()
        if(not self._lr_object.is_null_or_whitespace(emailTemplate)):
            query_parameters["emailTemplate"] = emailTemplate
        if(not self._lr_object.is_null_or_whitespace(resetPasswordUrl)):
            query_parameters["resetPasswordUrl"] = resetPasswordUrl

        resource_path = "/v1/password/forgot"
        return self._lr_object.execute("POST", resource_path, query_parameters, payload)
