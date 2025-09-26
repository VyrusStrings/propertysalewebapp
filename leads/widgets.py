from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django_countries.widgets import CountrySelectWidget

class FlagLabelCountrySelect(CountrySelectWidget):
    """
    Instead of using 'layout' with {flag}/{name}, we decorate each option's label
    with a flag icon directly. This avoids KeyError on missing keys and works for
    both ISO countries and custom entries like TRNC.
    """
    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)

        # optgroups: list of tuples (group_label, options_list, index)
        for _group_label, options, _idx in ctx["widget"]["optgroups"]:
            for opt in options:
                # 'value' is the country code; placeholder has empty value
                code = (opt.get("value") or "").strip()
                label = str(opt.get("label", "")).strip()

                # Do not try to add a flag for the empty "Select country" placeholder
                if not code:
                    # Keep the placeholder readable
                    opt["label"] = label or "Select country"
                    continue

                # Custom TRNC
                if code.upper() == "TRNC":
                    url = static("flags/trnc.gif")  # or .png if that's your file
                    flag_html = f'<img src="{url}" alt="" style="width:1.1em;height:1.1em;vertical-align:-2px;border-radius:2px;">'
                else:
                    # Use built-in sprite classes from django_countries/flags.css
                    # They expect .flag.flag-xx (lowercase iso code)
                    flag_html = f'<span class="flag flag-{code.lower()}"></span>'

                # Replace the label with "flag + text"
                opt["label"] = mark_safe(f'{flag_html} <span style="margin-left:.4em">{label}</span>')

        return ctx
