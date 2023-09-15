#!/usr/bin/python

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from helpdesk.models import Ticket


User = get_user_model()


class Command(BaseCommand):
    help = _("Use the 'submitter_email' field on a Ticket to try to populate the"
             "'submitter_user' field on tickets where this is blank.")

    def handle(self, *args, **options):
        total_processed = 0
        userless = Ticket.objects.filter(submitter_user__isnull=True)
        if userless.count() == 0:
            self.stdout.write(self.style.SUCCESS(_("No tickets to update.")))
        else:
            self.stdout.write(self.style.SUCCESS(_("Updating %d tickets." % userless.count())))
            for ticket in userless:
                try:
                    user = User.objects.get(email=ticket.submitter_email)
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(_("Could not find user with email '%s'." % ticket.submitter_email)))
                else:
                    ticket.submitter_user = user
                    ticket.save()
                    total_processed += 1
            self.stdout.write(self.style.SUCCESS(_("Updated %d tickets." % total_processed)))
