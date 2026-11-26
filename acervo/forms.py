from django import forms
from django.contrib.auth.models import User
from .models import Livro


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = [
            "titulo",
            "autor",
            "ano",
            "tipo",
            "biblioteca",
            "categoria",
            "quantidade_total",
            "prazo_dias",
        ]
        labels = {
            "titulo": "Título da Obra",
            "autor": "Autor(a)",
            "ano": "Ano de Publicação",
            "tipo": "Formato",
            "biblioteca": "Unidade da Biblioteca",
            "categoria": "Categoria",
            "quantidade_total": "Quantidade de Exemplares",
            "prazo_dias": "Prazo de Devolução (em dias)",
        }
        widgets = {
            "titulo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: O Pequeno Príncipe"}
            ),
            "autor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: Antoine de Saint-Exupéry",
                }
            ),
            "ano": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: 1943"}
            ),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "biblioteca": forms.Select(attrs={"class": "form-select"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "quantidade_total": forms.NumberInput(
                attrs={"class": "form-control", "min": "1"}
            ),
            "prazo_dias": forms.NumberInput(
                attrs={"class": "form-control", "min": "1"}
            ),
        }


class CadastroAlunoForm(forms.Form):
    matricula = forms.CharField(
        label="Matrícula (será seu login)",
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ex: 20261045"}
        ),
    )
    nome = forms.CharField(
        label="Nome Completo",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ex: João da Silva"}
        ),
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Crie uma senha"}
        ),
    )

    def clean_matricula(self):
        matricula = self.cleaned_data["matricula"].strip()
        if User.objects.filter(username=matricula).exists():
            raise forms.ValidationError("Esta matrícula já está cadastrada.")
        return matricula


class PeriodoForm(forms.Form):
    inicio = forms.DateField(
        required=False,
        label="Início",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control form-control-sm"}
        ),
    )
    fim = forms.DateField(
        required=False,
        label="Fim",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control form-control-sm"}
        ),
    )
