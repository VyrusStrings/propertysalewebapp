from django.db import models
from django.utils.translation import gettext_lazy as _


class Lead(models.Model):
    full_name  = models.CharField(_("Full name"), max_length=120)
    phone      = models.CharField(_("Phone"), max_length=50)
    email      = models.EmailField(_("Email"), blank=True)
    country    = models.CharField(_("Country"), max_length=80, blank=True)

    budget_min = models.PositiveIntegerField(_("Budget (min)"), null=True, blank=True)
    budget_max = models.PositiveIntegerField(_("Budget (max)"), null=True, blank=True)

    # Replaced old timeline field
    message    = models.TextField(_("Message"), blank=True)

    property   = models.ForeignKey(
        "properties.Property",
        verbose_name=_("Property"),
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )

    consent    = models.BooleanField(_("Consent"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, db_index=True)

    STATUS_NEW       = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_CHOICES = [
        (STATUS_NEW,       _("New")),
        (STATUS_CONTACTED, _("Contacted")),
    ]
    status = models.CharField(_("Status"), max_length=20, default=STATUS_NEW, choices=STATUS_CHOICES, db_index=True)

    # New fields
    remote_purchase = models.BooleanField(
        _("Buy remotely?"),
        null=True, blank=True,
        help_text=_("Whether the customer wants to complete the purchase remotely."),
    )
    visit_date = models.DateField(
        _("Planned visit date"),
        null=True, blank=True,
        help_text=_("If not remote, the date the customer plans to visit Cyprus."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")

    def __str__(self):
        who = self.full_name or self.email or self.phone or _("Lead")
        return f"{who} ({self.phone})" if self.phone else str(who)
