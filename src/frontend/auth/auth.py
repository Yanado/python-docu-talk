import os
from uuid import uuid4

import streamlit as st
from src.frontend.auth.cookies import TokenManager
from src.frontend.config import (
    GUEST_PERIOD_DOLLAR_AMOUNT,
    TOKEN_EXPIRATION_HOURS,
    USER_PERIOD_DOLLAR_AMOUNT,
)
from src.backend.docu_talk.docu_talk import DocuTalk
from src.backend.mailing.mailing_bot import MailingBot
from src.backend.utils.auth import is_valid_email


class Auth:
    """
    A class to manage user authentication, including sign-up, sign-in, guest access,
    and logout.
    """

    def __init__(
            self,
            docu_talk: DocuTalk,
            mailing_bot: MailingBot
        ) -> None:
        """
        Initializes the Auth class with the DocuTalk and MailingBot services.

        Parameters
        ----------
        docu_talk : DocuTalk
            The DocuTalk service instance.
        mailing_bot : MailingBot
            The mailing bot service instance.
        """

        self.docu_talk = docu_talk
        self.mailing_bot = mailing_bot
        self.logged_in = False

        self.token_manager = TokenManager(
            cookie_name="docu-talk",
            secret_key=os.getenv("TOKEN_SECRET_KEY"),
            token_expiration=TOKEN_EXPIRATION_HOURS
        )

        self.check_token()

    def check_token(self) -> None:
        """
        Checks the validity of the JWT token stored in cookies.
        If valid, retrieves the associated user; otherwise, deletes the token.
        """

        token = self.token_manager.get_token()

        if token is not None:
            email = self.token_manager.verify_token(token)
            if email is None:
                self.token_manager.delete_token()
            else:
                self.user = self.docu_talk.get_user(email)
                self.logged_in = True

    def logout(self) -> None:
        """
        Logs out the user by deleting the stored JWT token and updating the login state.
        """

        self.token_manager.delete_token()
        self.logged_in = False
        st.logout()

    def sign_up(
            self,
            email: str,
            first_name: str,
            last_name: str
        ) -> None:
        """
        Registers a new user and sends a welcome email with login details.

        Parameters
        ----------
        email : str
            The email address of the user.
        first_name : str
            The first name of the user.
        last_name : str
            The last name of the user.

        Raises
        ------
        streamlit.error
            If the email, first name, or last name format is invalid or the email
            already exists.
        """

        if not is_valid_email(email):
            st.error("Invalid Email format")

        elif first_name == "":
            st.error("Invalid First Name format")

        elif last_name == "":
            st.error("Invalid Last Name format")

        else:

            existing_users = self.docu_talk.get_users()
            if email in existing_users:
                st.error("Email already exists")
            else:
                password = self.docu_talk.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    period_dollar_amount=USER_PERIOD_DOLLAR_AMOUNT
                )

                self.mailing_bot.send_welcome_email(
                    recipient=email,
                    first_name=first_name,
                    id=email,
                    password=password
                )

                st.success(
                    "Successful registration. You have received an e-mail "
                    "containing your login details (check your spam)."
                )

                st.balloons()

    def sign_in(
            self,
            email: str,
            password: str
        ) -> None:
        """
        Logs in an existing user by verifying their credentials.

        Parameters
        ----------
        email : str
            The email address of the user.
        password : str
            The password of the user.

        Raises
        ------
        streamlit.error
            If the email or password is invalid.
        """

        if self.docu_talk.check_login(email, password) is True:
            self.token_manager.create_token(email)
            self.user = self.docu_talk.get_user(email)
            self.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Email or Password")

    def sign_up_from_provider(
            self,
            email: str
        ):
        """
        Registers a new user using an external authentication provider such as Microsoft
        or Google.

        Parameters
        ----------
        email : str
            The email address of the user.

        Notes
        -----
        - Extracts the first and last name from the authentication provider's user data.
        - Creates a new user in the DocuTalk system with a predefined dollar amount for
        usage.
        - Sends a welcome email to the user.
        """

        if "microsoft" in st.experimental_user.iss:
            first_name = st.experimental_user.name
            last_name = ""
        elif "google" in st.experimental_user.iss:
            first_name = st.experimental_user.given_name
            last_name = st.experimental_user.family_name

        self.docu_talk.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            period_dollar_amount=USER_PERIOD_DOLLAR_AMOUNT
        )

        self.mailing_bot.send_welcome_email(
            recipient=email,
            first_name=first_name
        )

    def sign_in_from_provider(self):
        """
        Logs in an existing user using an external authentication provider such as
        Microsoft or Google.

        Notes
        -----
        - Retrieves the authenticated user's email.
        - If the user does not exist in the system, registers them automatically.
        - Creates an authentication token and sets the user as logged in.
        - Triggers a Streamlit app rerun to reflect the updated login state.
        """

        email = st.experimental_user.email.lower() #type: ignore

        existing_users = self.docu_talk.get_users()
        if email not in existing_users:
            self.sign_up_from_provider(email=email)

        self.token_manager.create_token(email)
        self.user = self.docu_talk.get_user(email)
        self.logged_in = True
        st.rerun()

    def sign_guest(self) -> None:
        """
        Creates a guest account for temporary access and logs the guest in.
        """

        email = f"guest-{uuid4()}@ai-apps.cloud"

        self.docu_talk.create_user(
            email=email,
            first_name="Guest",
            last_name="GUEST",
            period_dollar_amount=GUEST_PERIOD_DOLLAR_AMOUNT,
            is_guest=True
        )

        self.token_manager.create_token(email)
        self.user = self.docu_talk.get_user(email)
        self.logged_in = True
        st.rerun()
