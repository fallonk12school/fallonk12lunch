from django import forms

from cafeteria.models import School


class GeneralForm(forms.Form):
    open_time = forms.TimeField(required=False, widget=forms.TimeInput(format='%H:%M', attrs={
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md',
        'type': 'time', 'disabled': 'true'}))
    close_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md',
        'type': 'time'}))
    reports_email = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'text',
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md'}))
    balance_export_path = forms.CharField(widget=forms.TextInput(attrs={'type': 'text',
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md'}))


class SchoolsModelForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ('active', 'display_name', 'name')
        widgets = {
            'active': forms.CheckboxInput(attrs={
                'class': 'focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'name': forms.HiddenInput(attrs={'readonly': 'True'})
        }
