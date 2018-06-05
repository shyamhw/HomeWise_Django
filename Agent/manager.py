from django.contrib.auth.models import UserManager
from django.db import models

class CustomUserManager(UserManager):
    """
        This class is necessary to create if using custom user model is desired
    """

    def _create_user(self, email, password, **extra_fields):
        """
            Creates and saves a User with the given username, email and password.
        """
        email = self.normalize_email(email)
        # extra_fields['username'] = extra_fields['username'] if extra_fields.get('username') else email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: creates a super user
        """

        u = self.create_user(email, password, **kwargs)
        u.is_staff = True
        u.is_active = True
        print("hi")
        u.save(using=self._db)
        return u

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)



    def get_agent_by_mls_region(self, mls_id, mls_region, **kwargs):
        """
        return agent object by mls_id and mls_region
        usage in: account.views.CheckMlsId get API,
                  account.views.CheckMlsEmail post API
                  account.views.CheckPasscode post API
                  account.views.ActivateAccount post API
                  account.views.AgentLogin post API
                  account.views.ForgotPassword post API
        """
        try:
            return self.get(mls_id=mls_id, mls_region=mls_region, **kwargs)
        except:
            # custom_log(log_level=logger_constants.LOGGING_LEVElS['ERROR'],
            #            logger_message=constants.MLS_DOES_NOT_EXIST_ERROR.format(mlsid, region_id))
            return None