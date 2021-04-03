# # from django.conf import settings
# # from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import ActiveOrgManager, OrgManager

# # from apps.rallz_auth.base_fields import SlugField
# # from apps.rallz_auth import exceptions as auth_exceptions

# # USER_MODEL = get_user_model()


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


# # class SharedTimestampModel(models.Model):
# #     created_at = models.DateTimeField(auto_now_add=True, editable=False)
# #     updated_at = models.DateTimeField(auto_now=True, editable=False)

# #     @property
# #     def _org_user_model(self):
# #         # model = self.__class__.module_registry[self.__class__.__module__][
# #         #     "OrgUserModel"
# #         # ]
# #         # if model is None:
# #         #     model = self.__class__.module_registry["organizations.models"][
# #         #         "OrgUserModel"
# #         #     ]
# #         return OrganizationUser

# #     @property
# #     def _org_owner_model(self):
# #         # model = self.__class__.module_registry[self.__class__.__module__][
# #         #     "OrgOwnerModel"
# #         # ]
# #         # if model is None:
# #         #     model = self.__class__.module_registry["organizations.models"][
# #         #         "OrgOwnerModel"
# #         #     ]
# #         return OrganizationOwner

# #     class Meta:
# #         abstract = True


# class AbstractBaseOrganization(models.Model):
#     """
#     The umbrella object with which users can be associated.
#     An organization can have multiple users but only one who can be designated
#     the owner user.
#     """

#     name = models.CharField(max_length=200, help_text=_(
#         "The name of the organization"))
#     is_active = models.BooleanField(default=True)

#     objects = OrgManager()
#     active = ActiveOrgManager()

#     class Meta:
#         abstract = True
#         ordering = ["name"]

#     def __str__(self):
#         return self.name

#     # def is_member(self, user):
#     #     return True if user in self.users.all() else False


# # class Organization(SharedTimestampModel, AbstractBaseOrganization):
# #     slug = SlugField(
# #         max_length=200,
# #         blank=False,
# #         editable=True,
# #         populate_from="name",
# #         unique=True,
# #         help_text=_(
# #             "The name in all lowercase, suitable for URL identification"),
# #     )

# #     users = models.ManyToManyField(  # mabye this should be a foreign many users to one organization
# #         USER_MODEL,
# #         through="OrganizationUser",  # or inherited parent
# #         related_name="%(app_label)s_%(class)s",
# #     ),
# #     # Owner is linked to OrganizationOwner by one to one

# #     class Meta(AbstractBaseOrganization.Meta):
# #         abstract = False
# #         verbose_name = _("organization")
# #         verbose_name_plural = _("organizations")

# #     def __str__(self):
# #         return self.name

# #     @property
# #     def _org_user_model(self):
# #         return OrganizationUser

# #     @property
# #     def _org_owner_model(self):
# #         return OrganizationOwner

# #     def add_user(self, user, is_admin=False):
# #         """
# #         Adds a new user and if the first user makes the user an admin and
# #         the owner.
# #         """
# #         users_count = self.users.all().count()
# #         if users_count == 0:
# #             is_admin = True
# #         # org_user = self._org_user_model.objects.create(
# #         org_user = self._org_user_model.objects.create(
# #             user=user, organization=self, is_admin=is_admin
# #         )
# #         if users_count == 0:
# #             # TODO get specific org user?
# #             # self.owner.objects.create(
# #             self._org_owner_model.objects.create(
# #                 organization=self, organization_user=org_user
# #             )
# #         # User added signal
# #         return org_user

# #     def remove_user(self, user):
# #         """
# #         Deletes a user from an organization.
# #         """
# #         org_user = self._org_user_model.objects.get(
# #             user=user, organization=self)
# #         org_user.delete()

# #         # User removed signal
# #         # user_removed.send(sender=self, user=user)

# #     def get_or_add_user(self, user, **kwargs):
# #         """
# #         Adds a new user to the organization, and if it's the first user makes
# #         the user an admin and the owner. Uses the `get_or_create` method to
# #         create or return the existing user.
# #         `user` should be a user instance, e.g. `auth.User`.
# #         Returns the same tuple as the `get_or_create` method, the
# #         `OrganizationUser` and a boolean value indicating whether the
# #         OrganizationUser was created or not.
# #         """
# #         is_admin = kwargs.pop("is_admin", False)
# #         users_count = self.users.all().count()
# #         if users_count == 0:
# #             is_admin = True

# #         org_user, created = self._org_user_model.objects.get_or_create(
# #             organization=self, user=user, defaults={"is_admin": is_admin}
# #         )
# #         if users_count == 0:
# #             self._org_owner_model.objects.create(
# #                 organization=self, organization_user=org_user
# #             )
# #         # if created:
# #             # User added signal
# #             # user_added.send(sender=self, user=user)
# #         return org_user, created

# #     def change_owner(self, new_owner):
# #         """
# #         Changes ownership of an organization.
# #         """
# #         old_owner = self.owner.organization_user
# #         self.owner.organization_user = new_owner
# #         self.owner.save()

# #         # Owner changed signal
# #         # owner_changed.send(sender=self, old=old_owner, new=new_owner)

# #     def is_admin(self, user):
# #         """
# #         Returns True is user is an admin in the organization, otherwise false
# #         """
# #         return (
# #             True if self.organization_users.filter(
# #                 user=user, is_admin=True) else False
# #         )

# #     def is_owner(self, user):
# #         """
# #         Returns True is user is the organization's owner, otherwise false
# #         """
# #         return self.owner.organization_user.user == user


# class AbstractBaseOrganizationUser(models.Model):
#     """
#     ManyToMany through field relating Users to Organizations.
#     It is possible for a User to be a member of multiple organizations, so this
#     class relates the OrganizationUser to the User model using a ForeignKey
#     relationship, rather than a OneToOne relationship.
#     Authentication and general user information is handled by the User class
#     and the contrib.auth application.
#     """

#     class Meta:
#         abstract = True
#         # ordering = ["organization", "user"]
#         # unique_together = ("user", "organization")

#     # def __str__(self):
#     #     return "{name} {org}".format(
#     #         name=self.name if self.user.is_active else self.user.email,
#     #         org=self.organization.name,
#     #     )

#     # @property
#     # def name(self):
#     #     """
#     #     Returns the connected user's full name or string representation if the
#     #     full name method is unavailable (e.g. on a custom user class).
#     #     """
#     #     try:
#     #         return self.user.get_full_name()
#     #     except AttributeError:
#     #         return str(self.user)


# # class OrganizationUser(SharedTimestampModel, AbstractBaseOrganizationUser):
# #     """
# #     Abstract OrganizationUser model
# #     """

# #     is_admin = models.BooleanField(default=False)

# #     user = models.ForeignKey(
# #         USER_MODEL,
# #         related_name="%(app_label)s_%(class)s",
# #         on_delete=models.CASCADE,
# #     ),

# #     organization = models.ForeignKey(
# #         Organization,
# #         related_name="organization_users",
# #         on_delete=models.CASCADE,
# #     ),

# #     class Meta(AbstractBaseOrganizationUser.Meta):
# #         abstract = False
# #         verbose_name = _("organization user")
# #         verbose_name_plural = _("organization users")

# #     def __str__(self):
# #         return "{0} ({1})".format(
# #             self.name if self.user.is_active else self.user.email,
# #             self.organization.name,
# #         )

# #     def delete(self, using=None):
# #         """
# #         If the organization user is also the owner, this should not be deleted
# #         unless it's part of a cascade from the Organization.
# #         If there is no owner then the deletion should proceed.
# #         """
# #         # from organizations.exceptions import OwnershipRequired

# #         try:
# #             if self.organization.owner.organization_user.pk == self.pk:
# #                 raise auth_exceptions.OwnershipRequired(
# #                     _(
# #                         "Cannot delete organization owner "
# #                         "before organization or transferring ownership."
# #                     )
# #                 )
# #         # TODO This line presumes that OrgOwner model can't be modified
# #         except self._org_owner_model.DoesNotExist:
# #             pass
# #         super().delete(using=using)


# class AbstractBaseOrganizationOwner(models.Model):
#     """
#     Each organization must have one and only one organization owner.
#     """

#     class Meta:
#         abstract = True

#     # def __str__(self):
#     #     return "{0}: {1}".format(self.organization, self.organization_user)


# # class OrganizationOwner(SharedTimestampModel, AbstractBaseOrganizationOwner):
# #     """
# #     Abstract OrganizationOwner model
# #     """
# #     organization_user = models.OneToOneField(
# #         # cls.module_registry[module]["OrgUserModel"],
# #         OrganizationUser,
# #         on_delete=models.CASCADE,
# #     ),

# #     organization = models.OneToOneField(
# #         # cls.module_registry[module]["OrgUserModel"],
# #         Organization,
# #         on_delete=models.CASCADE,
# #     ),

# #     class Meta:
# #         abstract = False
# #         verbose_name = _("organization owner")
# #         verbose_name_plural = _("organization owners")

# #     def save(self, *args, **kwargs):
# #         """
# #         Extends the default save method by verifying that the chosen
# #         organization user is associated with the organization.
# #         Method validates against the primary key of the organization because
# #         when validating an inherited model it may be checking an instance of
# #         `Organization` against an instance of `CustomOrganization`. Mutli-table
# #         inheritance means the database keys will be identical though.
# #         """
# #         # from organizations.exceptions import OrganizationMismatch

# #         if self.organization_user.organization.pk != self.organization.pk:
# #             raise auth_exceptions.OrganizationMismatch
# #         else:
# #             super().save(*args, **kwargs)
# #         pass
