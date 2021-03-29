from organizations.models import AbstractOrganization
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _


from .utils import user_email
from django.db import transaction
from .signals import email_confirmed, email_confirmation_sent
from .managers import EmailAddressManager, EmailConfirmationManager


class UserManager(BaseUserManager):
    """User Model manager for custom User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        user = self._create_user(email, password, **extra_fields)
        user.emailaddress_set.create(email=email, verified=True, primary=True)
        user.userprofile.create(user=user)
        return user


class Organization(AbstractOrganization):
    class Meta(AbstractOrganization.Meta):
        abstract = False


class User(AbstractUser):
    """Custom User model that requires an email address for username and also makes name mandatory."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    organization = models.ForeignKey(
        'Organization', on_delete=models.SET_NULL, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ('first_name',)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, verbose_name=_("user"), on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    photo_url = models.ImageField(upload_to='avatars/', blank=True)
#     phone = PhoneNumberField(blank=True)
#     dob = models.DateField(blank=True)

    def __str__(self):
        return "{0} profile".format(self.user.get_full_name())


class Contact(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, **kwargs):
#     user = kwargs["instance"]
#     if kwargs["created"]:
#         user.emailaddress_set.create(
#             email=user.email, verified=False, primary=True)
#         user_profile = UserProfile(user=user)
#         user_profile.save()
