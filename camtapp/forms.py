from django import forms
from camtapp.models import ApiResource

class ApiResourceForm(forms.ModelForm):
    class Meta:
        model = ApiResource
        fields = ("company_name",
                "api_base_url",
                "api_service_name",
                "default_company",
                "tenant_id",
                "api_username",
                "api_pass",
                "keepass_uuid",
                )   # NOTE: the trailing comma is required
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'api_base_url': forms.TextInput(attrs={'class': 'form-control'}),
            'api_service_name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_company': forms.TextInput(attrs={'class': 'form-control'}),
            'tenant_id': forms.TextInput(attrs={'class': 'form-control','required': False}),
            'api_username': forms.TextInput(attrs={'class': 'form-control'}),
            'api_pass': forms.TextInput(attrs={'class': 'form-control'}),
            'keepass_uuid': forms.TextInput(attrs={'class': 'form-control','required': False}),
        }