from django.contrib.auth.models import AbstractUser  # , BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

# from apps.rallz_auth.base_models import AbstractBaseOrganization, AbstractBaseOrganizationOwner, AbstractBaseOrganizationUser
from apps.rallz_auth import exceptions as auth_exceptions
from apps.rallz_auth.base_fields import SlugField


from .managers import UserManager


class User(AbstractUser):
    """Custom User model that requires an email address for username and also makes name mandatory."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    organization = models.ForeignKey(
        'Organization', related_name='users', on_delete=models.SET_NULL, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta():
        ordering = ('first_name',)


class UserProfile(models.Model):
    user = models.OneToOneField(
        'User', verbose_name=_("user"), on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    photo_url = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return "{0} profile".format(self.user.get_full_name())


# try:
#     # from apps.rallz_auth.base_models import AbstractBaseOrganization, AbstractBaseOrganizationOwner, AbstractBaseOrganizationUser
# #     from apps.rallz_auth.base_fields import SlugField
# #     from apps.rallz_auth import exceptions as auth_exceptions
# except ImportError:
#     print('failed to use organizations stuff')
class OrgManager(models.Manager):
    def get_for_user(self, user):
        return self.get_queryset().filter(users=user)


class ActiveOrgManager(OrgManager):
    """
    A more useful extension of the default manager which returns querysets
    including only active organizations
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class AbstractBaseOrganization(models.Model):
    """
    The umbrella object with which users can be associated.
    An organization can have multiple users but only one who can be designated
    the owner user.
    """

    name = models.CharField(max_length=200, help_text=_(
        "The name of the organization"))
    is_active = models.BooleanField(default=True)

    objects = OrgManager()
    active = ActiveOrgManager()

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class SharedTimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class Organization(SharedTimestampModel, AbstractBaseOrganization):
    slug = SlugField(
        max_length=200,
        blank=False,
        editable=True,
        populate_from="name",
        unique=True,
        help_text=_(
            "The name in all lowercase, suitable for URL identification"),
    )

    # users = models.ManyToManyField(  # mabye this should be a foreign many users to one organization
    # users = models.ForeignKey(  # mabye this should be a foreign many users to one organization
    #     'User',
    #     # through="OrganizationUser",  # or inherited parent
    #     related_name="rallz_auth_organizations",
    #     on_delete=models.CASCADE
    # )
    # Owner is linked to OrganizationOwner by one to one

    class Meta(AbstractBaseOrganization.Meta):
        abstract = False
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    def __str__(self):
        return self.name

    def is_member(self, user):
        return True if user in self.users.all() else False

    def add_user(self, user, is_admin=False):
        """
        Adds a new user and if the first user makes the user an admin and
        the owner.
        """
        users_count = self.users.all().count()
        if users_count == 0:
            is_admin = True
        # org_user = self._org_user_model.objects.create(
        org_user = OrganizationUser.objects.create(
            user=user, organization=self, is_admin=is_admin
        )
        if users_count == 0:
            # TODO get specific org user?
            # self.owner.objects.create(
            OrganizationOwner.objects.create(
                organization=self, organization_user=org_user
            )
        # User added signal
        return org_user

    def remove_user(self, user):
        """
        Deletes a user from an organization.
        """
        org_user = OrganizationUser.objects.get(
            user=user, organization=self)
        org_user.delete()

        # User removed signal
        # user_removed.send(sender=self, user=user)

    def get_or_add_user(self, user, **kwargs):
        """
        Adds a new user to the organization, and if it's the first user makes
        the user an admin and the owner. Uses the `get_or_create` method to
        create or return the existing user.
        `user` should be a user instance, e.g. `auth.User`.
        Returns the same tuple as the `get_or_create` method, the
        `OrganizationUser` and a boolean value indicating whether the
        OrganizationUser was created or not.
        """
        is_admin = kwargs.pop("is_admin", False)
        users_count = self.users.all().count()
        if users_count == 0:
            is_admin = True

        org_user, created = OrganizationUser.objects.get_or_create(
            organization=self, user=user, defaults={"is_admin": is_admin}
        )
        if users_count == 0:
            OrganizationOwner.objects.create(
                organization=self, organization_user=org_user
            )
        # if created:
            # User added signal
            # user_added.send(sender=self, user=user)
        return org_user, created

    def change_owner(self, new_owner):
        """
        Changes ownership of an organization.
        """
        old_owner = self.owner.organization_user
        self.owner.organization_user = new_owner
        self.owner.save()

        # Owner changed signal
        # owner_changed.send(sender=self, old=old_owner, new=new_owner)

    def is_admin(self, user):
        """
        Returns True is user is an admin in the organization, otherwise false
        """
        return (
            True if self.organization_users.filter(
                user=user, is_admin=True) else False
        )

    def is_owner(self, user):
        """
        Returns True is user is the organization's owner, otherwise false
        """
        return self.owner.organization_user.user == user


class OrganizationUser(SharedTimestampModel):
    """
    Abstract OrganizationUser model
    """
    is_admin = models.BooleanField(default=False)

    user = models.OneToOneField(
        User,
        related_name="organization_user",
        on_delete=models.CASCADE,
    )
    # user = models.ForeignKey(
    #     User,
    #     related_name="rallz_auth_organization_users",
    #     on_delete=models.CASCADE,
    # )

    organization = models.ForeignKey(
        Organization,
        related_name="organization_users",
        on_delete=models.CASCADE,
    )

    class Meta():
        unique_together = ("user", "organization")
        ordering = ("organization", "user",)
        verbose_name = _("organization user")
        verbose_name_plural = _("organization users")

    def __str__(self):
        return "{0} ({1})".format(
            self.name if self.user.is_active else self.user.email,
            self.organization.name,
        )

    @property
    def name(self):
        """
        Returns the connected user's full name or string representation if the
        full name method is unavailable (e.g. on a custom user class).
        """
        try:
            return self.user.get_full_name()
        except AttributeError:
            return str(self.user)

    def delete(self, using=None):
        """
        If the organization user is also the owner, this should not be deleted
        unless it's part of a cascade from the Organization.
        If there is no owner then the deletion should proceed.
        """
        # from organizations.exceptions import OwnershipRequired

        try:
            if self.organization.owner.organization_user.pk == self.pk:
                raise auth_exceptions.OwnershipRequired(
                    _(
                        "Cannot delete organization owner "
                        "before organization or transferring ownership."
                    )
                )
        # TODO This line presumes that OrgOwner model can't be modified
        except OrganizationOwner.DoesNotExist:
            pass
        super().delete(using=using)


class OrganizationOwner(SharedTimestampModel):
    """
    Abstract OrganizationOwner model
    """
    organization_user = models.OneToOneField(
        # cls.module_registry[module]["OrgUserModel"],
        OrganizationUser,
        on_delete=models.CASCADE,
    )

    organization = models.OneToOneField(
        # cls.module_registry[module]["OrgUserModel"],
        Organization,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = False
        verbose_name = _("organization owner")
        verbose_name_plural = _("organization owners")

    def __str__(self):
        return "{0}: {1}".format(self.organization, self.organization_user)

    def save(self, *args, **kwargs):
        """
        Extends the default save method by verifying that the chosen
        organization user is associated with the organization.
        Method validates against the primary key of the organization because
        when validating an inherited model it may be checking an instance of
        `Organization` against an instance of `CustomOrganization`. Mutli-table
        inheritance means the database keys will be identical though.
        """
        # from organizations.exceptions import OrganizationMismatch

        if self.organization_user.organization.pk != self.organization.pk:
            raise auth_exceptions.OrganizationMismatch
        else:
            super().save(*args, **kwargs)
