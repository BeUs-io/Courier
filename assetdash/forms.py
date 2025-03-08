from django import forms
from dashboard import models
from crispy_forms import layout, helper


class AssetRequestModelForm(forms.ModelForm):
    details = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Message"
    )

    class Meta:
        model = models.AssetRequest
        fields = ('details',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        btn_title = "Submit Request"
        if self.instance.details:
            btn_title = "Update Request"
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            'details',
            layout.Column(
                layout.Submit(
                    'submit', btn_title, css_class="px-4 btn-primary"
                ),
                css_class='text-end'
            )
        )
