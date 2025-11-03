# forms.py
from django import forms
from .models import *

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')


