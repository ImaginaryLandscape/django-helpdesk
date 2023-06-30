from helpdesk.models import CustomField, KBItem, Queue


class AbstractCreateTicketMixin():
    def get_initial(self):
        initial_data = {}
        request = self.request
        try:
            initial_data['queue'] = Queue.objects.get(slug=request.GET.get('queue', None)).id
        except Queue.DoesNotExist:
            pass
        u = request.user
        if u.is_authenticated and u.usersettings_helpdesk.use_email_as_submitter and u.email:
            initial_data['submitter_email'] = u.email

        query_param_fields = ['submitter_email', 'title', 'body', 'queue', 'kbitem']
        custom_fields = ["custom_%s" % f.name for f in CustomField.objects.filter(staff_only=False)]
        query_param_fields += custom_fields
        for qpf in query_param_fields:
            initial_data[qpf] = request.GET.get(qpf, initial_data.get(qpf, ""))

        # Ugly hack to prepopulate UIC user data into custom form fields
        form_class = self.get_form_class()
        if hasattr(form_class, 'user_field_map'):
            user_map_items = form_class.user_field_map.items()
            user = self.request.user
            for ticket_field, user_field in user_map_items:
                initial_data[ticket_field] = getattr(user, user_field)
        if hasattr(form_class, 'profile_field_map') and hasattr(u, 'dashboarduserprofile'):
            profile_map_items = form_class.profile_field_map.items()
            user = self.request.user
            for ticket_field, profile_field in profile_map_items:
                if isinstance(profile_field, tuple):
                    # this deals with mapping mismatched radios/selects to
                    # corresponding equivalent value
                    profile_value = getattr(user.dashboarduserprofile, profile_field[0])
                    custom_val_map = profile_field[1]
                    custom_value = custom_val_map.get(profile_value)
                    initial_data[ticket_field] = custom_value
                else:
                    initial_data[ticket_field] = getattr(user.dashboarduserprofile, profile_field)

        return initial_data

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kbitem = self.request.GET.get(
            'kbitem',
            self.request.POST.get('kbitem', None),
        )
        if kbitem:
            try:
                kwargs['kbcategory'] = KBItem.objects.get(pk=int(kbitem)).category
            except (ValueError, KBItem.DoesNotExist):
                pass
        return kwargs
