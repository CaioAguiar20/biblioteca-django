from django.db.models import Q
from django.shortcuts import redirect, render
from .forms import LivroForm
from .models import Livro


def lista_livros(request):
    livros = Livro.objects.all().order_by("titulo")

    nome = request.GET.get("nome", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    if nome:
        livros = livros.filter(
            Q(titulo__icontains=nome) |
            Q(autor__icontains=nome)
        )

    if tipo:
        livros = livros.filter(tipo=tipo)

    if categoria:
        livros = livros.filter(categoria=categoria)

    return render(
        request,
        "acervo/lista.html",
        {
            "livros": livros,
            "nome": nome,
            "tipo": tipo,
            "categoria": categoria,
            "tipos": Livro.TIPO_ACERVO,
            "categorias": Livro.CATEGORIAS,
        },
    )


def novo_livro(request):
    if request.method == "POST":
        form = LivroForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("lista_livros")
    else:
        form = LivroForm()

    return render(
        request,
        "acervo/form.html",
        {"form": form},
    )