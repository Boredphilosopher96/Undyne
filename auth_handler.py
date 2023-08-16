import os
from typing import Optional
from urllib.parse import urlencode

from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Token
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import session
from werkzeug.local import LocalProxy

import utils
from db.auth import auth_handler, auth_models

load_dotenv(find_dotenv(utils.get_project_base_path()))

oauth = OAuth()


class Auth:
    def __init__(self, app: Flask):
        oauth.init_app(app)
        self.__registered_app = None
    
    def _get_app(self) -> Optional[LocalProxy]:
        if self.__registered_app is None:
            self.__registered_app = oauth.register(
                "auth0",
                client_id = os.getenv("CLIENT_ID"),
                client_secret = os.getenv("CLIENT_SECRET"),
                api_base_url = f"https://{os.getenv('DOMAIN')}",
                access_token_url = f"https://{os.getenv('DOMAIN')}/oauth/token",
                authorize_url = f"https://{os.getenv('DOMAIN')}/authorize",
                client_kwargs = {
                    "scope": "openid profile email",
                },
                server_metadata_url = f"https://{os.getenv('DOMAIN')}/.well-known/openid-configuration",
                fetch_token = self.fetch_token,
            )
        return self.__registered_app
    
    @staticmethod
    def fetch_token(name, request):
        token = OAuth2Token.find(
            name = name,
            user = request.user
        )
        return token.to_token()
    
    def handle_callbacks(self) -> bool:
        """
        Function to handle auth callback.
        Stores auth details in session if successful
        :return: The status of auth
        """
        auth0 = self._get_app()
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        # Just making sure the resp data is valid
        user_data = auth_models.UserModel(**resp.json())
        # Replacing user_data object because we want to treat users who have logged in from different authentication
        # methods as the same user
        user_data = auth_handler.check_if_user_in_db(user_data.user_id, user_email = user_data.user_email)
        if user_data:
            # Store the user information in flask session.
            session['profile'] = user_data.model_dump()
            return True
        else:
            # Storing user sent info temporarily
            session['temp'] = resp.json()
            return False
    
    def handle_login(self, redirect_uri: str):
        return self._get_app().authorize_redirect(redirect_uri = redirect_uri)
    
    @staticmethod
    def handle_logout(homepage: str):
        # Clear session stored data
        session.clear()
        params = {'returnTo': homepage, 'client_id': os.getenv('CLIENT_ID')}
        return f"https://{os.getenv('DOMAIN')}/v2/logout?{urlencode(params)}"
