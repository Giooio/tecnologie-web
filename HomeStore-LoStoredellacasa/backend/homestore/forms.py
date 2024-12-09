from django import forms
from .models import Product
from django.contrib.auth.models import User
from .models import Question

class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nome', 'descrizione', 'prezzo', 'immagine', 'categoria', 'stock']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome del prodotto'}),
            'descrizione': forms.Textarea(attrs={'placeholder': 'Descrizione'}),
            'prezzo': forms.NumberInput(attrs={'placeholder': 'Prezzo'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'Quantità disponibile'}),
            'categoria': forms.TextInput(),
        }
        
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock in (None, ''):
            return 0  # Impostiamo 0 se stock è None o vuoto
        return stock

class CustomUserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Conferma Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Le due password devono coincidere.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class QuestionForm(forms.ModelForm):
    question_text = forms.CharField(
        required=True,
        label="Domanda",
        widget=forms.Textarea(attrs={'placeholder': 'Scrivi qui la tua domanda...'}),
        error_messages={
        'required': 'Questo campo è obbligatorio.'
    })
    
    class Meta:
        model = Question
        fields = ['question_text']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['answer_text']