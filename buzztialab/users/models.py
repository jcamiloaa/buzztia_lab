from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import ImageField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for buzztialab.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    ROLE_CHOICES = [
        ("user", _("User")),
        ("staff", _("Staff")),
        ("admin", _("Admin")),
    ]

    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    profile_picture = ImageField(
        _("Profile Picture"),
        upload_to="profile_pics/",
        blank=True,
        null=True,
    )
    role = CharField(
        _("Role"),
        max_length=10,
        choices=ROLE_CHOICES,
        default="user",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
