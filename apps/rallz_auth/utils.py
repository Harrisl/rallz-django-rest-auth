from itertools import chain

# def default_org_model():
#     """Encapsulates importing the concrete model"""
#     from apps.rallz_auth.models import Organization

#     return Organization


def model_field_names(model):
    """
    Returns a list of field names in the model

    Direct from Django upgrade migration guide.
    """
    return list(
        set(
            chain.from_iterable(
                (field.name, field.attname)
                if hasattr(field, "attname")
                else (field.name,)
                for field in model._meta.get_fields()
                if not (field.many_to_one and field.related_model is None)
            )
        )
    )


def create_organization(
    user,
    name,
    is_active=None,
    org_defaults=None,
    org_user_defaults=None,
    **kwargs
):
    """
    Returns a new organization, also creating an initial organization user who
    is the owner.

    The specific models can be specified if a custom organization app is used.
    The simplest way would be to use a partial.

    >>> from organizations.utils import create_organization
    >>> from myapp.models import Account
    >>> from functools import partial
    >>> create_account = partial(create_organization, model=Account)
    """
    # from apps.rallz_auth.models import OrganizationOwner, OrganizationUser
    from apps.rallz_auth_multitenant.models import (TenantOrganization,
                                                    TenantOrganizationOwner,
                                                    TenantOrganizationUser)

    # org_model = (
    #     kwargs.pop("model", None)
    #     or kwargs.pop("org_model", None)
    #     or default_org_model()
    # )

    use_tenant = kwargs.pop('use_tenant', False)

    defaultOrg = TenantOrganization  # if use_tenant else default_org_model()
    defaultOrgUser = TenantOrganizationUser  # if use_tenant else OrganizationUser
    # if use_tenant else OrganizationOwner
    defaultOrgOwner = TenantOrganizationOwner

    # org_model.owner.related.related_model or
    # org_owner_model = OrganizationOwner
    org_owner_model = (kwargs.pop("owner_model", None)
                       or kwargs.pop("org_owner_model", None)
                       or defaultOrgOwner
                       )
    # org_user_model = OrganizationUser
    org_user_model = (kwargs.pop("user_model", None)
                      or kwargs.pop("org_user_model", None)
                      or defaultOrgUser
                      )
    if org_defaults is None:
        org_defaults = {}
    if org_user_defaults is None:
        if "is_admin" in model_field_names(org_user_model):
            org_user_defaults = {"is_admin": True}
        else:
            org_user_defaults = {}

    # if slug is not None:
    #     org_defaults.update({"slug": slug})
    if is_active is not None:
        org_defaults.update({"is_active": is_active})

    org_defaults.update({"name": name})
    organization = defaultOrg.objects.create(**org_defaults)
    user.organization = organization

    if(use_tenant):
        from django_multitenant.utils import set_current_tenant
        set_current_tenant(organization)

    org_user_defaults.update({"organization": organization, "user": user})
    new_user = org_user_model.objects.create(**org_user_defaults)

    org_owner_model.objects.create(
        organization=organization, organization_user=new_user
    )
    return organization
