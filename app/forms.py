from django import forms
from django.contrib.auth.models import User
from .models import Borrower

class BorrowerForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = ['bname', 'address', 'phone', 'ssn']

class FinePaymentForm(forms.Form):
    card_id = forms.IntegerField(label='Borrower Card ID')
    
class BorrowerRegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Borrower
        fields = ['bname', 'address', 'phone', 'ssn']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        borrower = super().save(commit=False)
        borrower.user = user
        if commit:
            borrower.save()
        return borrower    