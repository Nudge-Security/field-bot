import ast
import datetime
import re

import boto3
from envs import env
from jose import JWTError, jwt
import requests
from pycognito import AWSSRP


class WarrantException(Exception):
    """Base class for all pyCognito exceptions"""


class TokenVerificationException(WarrantException):
    """Raised when token verification fails."""



class Cognito:


    def __init__(
            self,
            user_pool_id,
            client_id,
            user_pool_region=None,
            username=None,
            id_token=None,
            refresh_token=None,
            access_token=None,
            client_secret=None,
            access_key=None,
            secret_key=None,
            session=None,
            botocore_config=None,
    ):
        """
        :param user_pool_id: Cognito User Pool ID
        :param client_id: Cognito User Pool Application client ID
        :param username: User Pool username
        :param id_token: ID Token returned by authentication
        :param refresh_token: Refresh Token returned by authentication
        :param access_token: Access Token returned by authentication
        :param access_key: AWS IAM access key
        :param secret_key: AWS IAM secret key
        :param session: Boto3 client session
        :param botocore_config: Botocore Config object for the client
        """

        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.user_pool_region = (
            user_pool_region if user_pool_region else self.user_pool_id.split("_")[0]
        )
        self.username = username
        self.id_token = id_token
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_secret = client_secret
        self.token_type = None
        self.id_claims = None
        self.access_claims = None
        self.custom_attributes = None
        self.base_attributes = None
        self.pool_jwk = None

        boto3_client_kwargs = {}
        if access_key and secret_key:
            boto3_client_kwargs["aws_access_key_id"] = access_key
            boto3_client_kwargs["aws_secret_access_key"] = secret_key
        if self.user_pool_region:
            boto3_client_kwargs["region_name"] = self.user_pool_region
        if botocore_config:
            boto3_client_kwargs["config"] = botocore_config

        if session:
            self.client = session.client("cognito-idp", **boto3_client_kwargs)
        else:
            self.client = boto3.client("cognito-idp", **boto3_client_kwargs)

    @property
    def user_pool_url(self):
        return f"https://cognito-idp.{self.user_pool_region}.amazonaws.com/{self.user_pool_id}"

    def get_keys(self):
        if self.pool_jwk:
            return self.pool_jwk

        # Check for the dictionary in environment variables.
        pool_jwk_env = env("COGNITO_JWKS", {}, var_type="dict")
        if pool_jwk_env:
            self.pool_jwk = pool_jwk_env
        # If it is not there use the requests library to get it
        else:
            self.pool_jwk = requests.get(
                f"{self.user_pool_url}/.well-known/jwks.json"
            ).json()
        return self.pool_jwk

    def get_key(self, kid):
        keys = self.get_keys().get("keys")
        key = list(filter(lambda x: x.get("kid") == kid, keys))
        return key[0]

    def verify_tokens(self):
        """
        Verify the current id_token and access_token.  An exception will be
        thrown if they do not pass verification.  It can be useful to call this
        method after creating a Cognito instance where you've provided
        externally-remembered token values.
        """
        self.verify_token(self.id_token, "id_token", "id")
        self.verify_token(self.access_token, "access_token", "access")

    def verify_token(self, token, id_name, token_use):
        # https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html

        kid = jwt.get_unverified_header(token).get("kid")
        hmac_key = self.get_key(kid)
        try:
            verified = jwt.decode(
                token,
                hmac_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.user_pool_url,
                options={
                    "require_aud": token_use != "access",
                    "require_iss": True,
                    "require_exp": True,
                    "verify_at_hash":False

                },
            )
        except JWTError as err:
            raise TokenVerificationException(
                f"Your {id_name!r} token could not be verified ({err})."
            ) from None

        token_use_verified = verified.get("token_use") == token_use
        if not token_use_verified:
            raise TokenVerificationException(
                f"Your {id_name!r} token use ({token_use!r}) could not be verified."
            )

        setattr(self, id_name, token)
        setattr(self, f"{token_use}_claims", verified)
        return verified

    def is_token_expired(self, renew=True):
        """
        Checks the exp attribute of the access_token and either refreshes
        the tokens by calling the renew_access_tokens method or does nothing
        :param renew: bool indicating whether to refresh on expiration
        :return: bool indicating whether access_token has expired
        """
        if not self.access_token:
            raise AttributeError("Access Token Required to Check Token")
        now = datetime.datetime.now()
        dec_access_token = jwt.get_unverified_claims(self.access_token)

        if now > datetime.datetime.fromtimestamp(dec_access_token["exp"]):
            expired = True
            if renew:
                self.renew_access_token()
        else:
            expired = False
        return expired

    def set_base_attributes(self, **kwargs):
        self.base_attributes = kwargs

    def add_custom_attributes(self, **kwargs):
        custom_key = "custom"
        custom_attributes = {}

        for old_key, value in kwargs.items():
            new_key = custom_key + ":" + old_key
            custom_attributes[new_key] = value

        self.custom_attributes = custom_attributes



    def authenticate(self, password, client_metadata=None):
        """
        Authenticate the user using the SRP protocol
        :param password: The user's passsword
        :param client_metadata: Metadata you can provide for custom workflows that RespondToAuthChallenge triggers.
        :return:
        """
        aws = AWSSRP(
            username=self.username,
            password=password,
            pool_id=self.user_pool_id,
            client_id=self.client_id,
            client=self.client,
            client_secret=self.client_secret,
        )
        tokens = aws.authenticate_user(client_metadata=client_metadata)
        self._set_tokens(tokens)


    def renew_access_token(self):
        """
        Sets a new access token on the User using the refresh token.
        """
        auth_params = {"REFRESH_TOKEN": self.refresh_token}
        self._add_secret_hash(auth_params, "SECRET_HASH")
        refresh_response = self.client.initiate_auth(
            ClientId=self.client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters=auth_params,
        )
        self._set_tokens(refresh_response)


    def _add_secret_hash(self, parameters, key):
        """
        Helper function that computes SecretHash and adds it
        to a parameters dictionary at a specified key
        """
        if self.client_secret is not None:
            secret_hash = AWSSRP.get_secret_hash(
                self.username, self.client_id, self.client_secret
            )
            parameters[key] = secret_hash

    def _set_tokens(self, tokens):
        """
        Helper function to verify and set token attributes based on a Cognito
        AuthenticationResult.
        """
        self.verify_token(tokens["AuthenticationResult"]["IdToken"], "id_token", "id")
        if "RefreshToken" in tokens["AuthenticationResult"]:
            self.refresh_token = tokens["AuthenticationResult"]["RefreshToken"]
        self.verify_token(
            tokens["AuthenticationResult"]["AccessToken"], "access_token", "access"
        )
        self.token_type = tokens["AuthenticationResult"]["TokenType"]

    def _set_attributes(self, response, attribute_dict):
        """
        Set user attributes based on response code
        :param response: HTTP response from Cognito
        :attribute dict: Dictionary of attribute name and values
        """
        status_code = response.get(
            "HTTPStatusCode", response["ResponseMetadata"]["HTTPStatusCode"]
        )
        if status_code == 200:
            for key, value in attribute_dict.items():
                setattr(self, key, value)
