from django import forms


class ProjectChangeOwnerForm(forms.Form):
    new_owner = forms.ChoiceField(choices=[], required=False, label="New Owner")
    
