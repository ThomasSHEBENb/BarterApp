from django import forms
from .models import Ad, ExchangeProposal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image', 'category', 'condition']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condition'].empty_label = None

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ExchangeProposalForm(forms.ModelForm):
    ad_receiver = forms.ModelChoiceField(queryset=Ad.objects.none(), label="Выберите своё объявление")

    class Meta:
        model = ExchangeProposal
        fields = ['ad_receiver', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['ad_receiver'].queryset = Ad.objects.filter(user=user)