from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
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


def editar_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    if request.method == "POST":
        form = LivroForm(request.POST, instance=livro)

        if form.is_valid():
            form.save()
            return redirect("lista_livros")
    else:
        form = LivroForm(instance=livro)

    return render(
        request,
        "acervo/form.html",
        {"form": form},
    )


def excluir_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    if request.method == "POST":
        livro.delete()
        return redirect("lista_livros")

    return render(
        request,
        "acervo/confirmar_exclusao.html",
        {"livro": livro},
    )