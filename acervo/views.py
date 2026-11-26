import csv
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .dashboard import filtrar_periodo, obter_dados_dashboard
from .forms import CadastroAlunoForm, LivroForm
from .models import Emprestimo, Livro


def is_admin(user):
    return user.is_authenticated and user.is_staff


# --- FUNÇÃO AUXILIAR PARA CAPTURAR A BIBLIOTECA GLOBAL ---
def get_biblioteca_ativa(request):
    """Captura a unidade selecionada no menu global ou salva na sessão."""
    biblio_GET = request.GET.get("biblioteca_global")
    if biblio_GET is not None:
        if biblio_GET == "":
            if "biblioteca_global" in request.session:
                del request.session["biblioteca_global"]
        else:
            request.session["biblioteca_global"] = biblio_GET
    return request.session.get("biblioteca_global")


# --- TELA INICIAL / DASHBOARD (AULA 17) ---
def home(request):
    get_biblioteca_ativa(request)
    contexto = obter_dados_dashboard(request)
    contexto["mostra_series"] = request.user.is_authenticated and request.user.is_staff
    return render(request, "acervo/home.html", contexto)


# --- ACERVO PÚBLICO E FILTROS ---
def lista_livros(request):
    biblio_ativa = get_biblioteca_ativa(request)
    livros = Livro.objects.all()

    # Se houver unidade selecionada globalmente, já filtra por ela
    if biblio_ativa:
        livros = livros.filter(biblioteca=biblio_ativa)

    nome = request.GET.get("nome", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    biblioteca_filtro = request.GET.get("biblioteca", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    ordem = request.GET.get("ordem", "titulo")

    if nome:
        livros = livros.filter(Q(titulo__icontains=nome) | Q(autor__icontains=nome))

    if tipo:
        livros = livros.filter(tipo=tipo)

    if biblioteca_filtro:
        livros = livros.filter(biblioteca=biblioteca_filtro)

    if categoria:
        livros = livros.filter(categoria=categoria)

    opcoes_ordenacao = {
        "titulo": "titulo",
        "titulo_desc": "-titulo",
        "ano": "ano",
        "ano_desc": "-ano",
    }

    livros = livros.order_by(opcoes_ordenacao.get(ordem, "titulo"))

    return render(
        request,
        "acervo/lista.html",
        {
            "livros": livros,
            "nome": nome,
            "tipo": tipo,
            "biblioteca": biblioteca_filtro or biblio_ativa,
            "categoria": categoria,
            "ordem": ordem,
            "tipos": Livro.TIPO_ACERVO,
            "categorias": Livro.CATEGORIAS,
        },
    )


# --- RESERVAR / PEGAR EMPRESTADO (ALUNO LOGADO) ---
@login_required(login_url="login_usuario")
def reservar_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    if livro.quantidade_disponivel <= 0:
        messages.error(request, "Este livro está esgotado no momento.")
        return redirect("lista_livros")

    ja_possui = Emprestimo.objects.filter(
        livro=livro, usuario=request.user, data_devolucao__isnull=True
    ).exists()

    if ja_possui:
        messages.warning(
            request, "Você já está com um exemplar deste livro emprestado."
        )
        return redirect("lista_livros")

    Emprestimo.objects.create(livro=livro, usuario=request.user)
    messages.success(
        request,
        f"Empréstimo realizado! Você tem {livro.prazo_dias} dias para devolver '{livro.titulo}'.",
    )
    return redirect("meus_emprestimos")


@login_required(login_url="login_usuario")
def meus_emprestimos(request):
    biblioteca_filtro = request.GET.get("biblioteca", "").strip()

    emprestimos = (
        Emprestimo.objects.filter(usuario=request.user)
        .select_related("livro")
        .order_by("-data_emprestimo")
    )

    if biblioteca_filtro:
        emprestimos = emprestimos.filter(livro__biblioteca=biblioteca_filtro)

    return render(
        request,
        "acervo/meus_emprestimos.html",
        {"emprestimos": emprestimos, "biblioteca_filtro": biblioteca_filtro},
    )


# --- PAINEL EXCLUSIVO DO ADMIN ---
@user_passes_test(is_admin, login_url="login_usuario")
def painel_admin(request):
    biblio_ativa = get_biblioteca_ativa(request)

    ativos = Emprestimo.objects.filter(data_devolucao__isnull=True)
    if biblio_ativa:
        ativos = ativos.filter(livro__biblioteca=biblio_ativa)

    ativos = ativos.select_related("livro", "usuario").order_by("data_prevista")

    return render(
        request,
        "acervo/painel_admin.html",
        {"ativos": ativos, "biblio_ativa": biblio_ativa},
    )


@user_passes_test(is_admin, login_url="login_usuario")
def registrar_devolucao(request, emprestimo_id):
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
    if not emprestimo.data_devolucao:
        emprestimo.data_devolucao = timezone.now()
        emprestimo.save()
        messages.success(
            request,
            f"Devolução do livro '{emprestimo.livro.titulo}' registrada com sucesso!",
        )
    return redirect("painel_admin")


# --- EXPORTAR CSV E API (AULA 17) ---
@user_passes_test(is_admin, login_url="login_usuario")
def exportar_csv(request):
    qs, _ = filtrar_periodo(
        request,
        Emprestimo.objects.select_related("livro", "usuario").order_by(
            "-data_emprestimo"
        ),
    )

    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="relatorio_emprestimos.csv"'
    resp.write("\ufeff")  # BOM para o Excel ler acentos corretamente

    writer = csv.writer(resp, delimiter=";")
    writer.writerow(
        ["Livro", "Matrícula", "Aluno", "Data Saída", "Previsão Devolução", "Status"]
    )

    def sanitizar(valor):
        texto = str(valor or "")
        if texto.startswith(("=", "+", "-", "@")):
            return "'" + texto
        return texto

    for e in qs:
        status = (
            "Devolvido"
            if e.data_devolucao
            else ("Atrasado" if e.esta_atrasado else "Em aberto")
        )
        writer.writerow(
            [
                sanitizar(e.livro.titulo),
                sanitizar(e.usuario.username),
                sanitizar(e.usuario.first_name or e.usuario.username),
                e.data_emprestimo.strftime("%d/%m/%Y %H:%M"),
                e.data_prevista.strftime("%d/%m/%Y"),
                status,
            ]
        )

    return resp


@login_required(login_url="login_usuario")
def api_dashboard(request):
    dados = obter_dados_dashboard(request)
    return JsonResponse(
        {
            "kpis": dados["kpis"],
            "ranking": dados["ranking"],
            "por_mes": dados["por_mes"],
            "distribuicao": dados["distribuicao"],
        }
    )


# --- CRUD DE LIVROS (APENAS ADMIN) ---
@user_passes_test(is_admin, login_url="login_usuario")
def novo_livro(request):
    biblio_ativa = get_biblioteca_ativa(request)
    if request.method == "POST":
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Livro cadastrado no acervo!")
            return redirect("lista_livros")
    else:
        # Se houver uma biblioteca ativa no topo, pré-seleciona ela no form
        initial_data = {}
        if biblio_ativa:
            initial_data["biblioteca"] = biblio_ativa
        form = LivroForm(initial=initial_data)

    return render(request, "acervo/form.html", {"form": form})


@user_passes_test(is_admin, login_url="login_usuario")
def editar_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    if request.method == "POST":
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, "Livro atualizado com sucesso!")
            return redirect("lista_livros")
    else:
        form = LivroForm(instance=livro)
    return render(request, "acervo/form.html", {"form": form})


@user_passes_test(is_admin, login_url="login_usuario")
def excluir_livro(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    if request.method == "POST":
        livro.delete()
        messages.success(request, "Livro removido do acervo.")
        return redirect("lista_livros")
    return render(request, "acervo/confirmar_exclusao.html", {"livro": livro})


# --- AUTENTICAÇÃO ---
def login_usuario(request):
    if request.method == "POST":
        usuario_input = request.POST.get("username", "").strip()
        senha_input = request.POST.get("password", "")
        user = authenticate(request, username=usuario_input, password=senha_input)
        if user is not None:
            login(request, user)
            messages.success(
                request, f"Bem-vindo(a), {user.first_name or user.username}!"
            )
            if user.is_staff:
                return redirect("painel_admin")
            return redirect("lista_livros")
        else:
            messages.error(request, "Matrícula/Usuário ou senha inválidos.")
    return render(request, "acervo/login.html")


def cadastro_aluno(request):
    if request.method == "POST":
        form = CadastroAlunoForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["matricula"],
                first_name=form.cleaned_data["nome"],
                password=form.cleaned_data["senha"],
            )
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("lista_livros")
    else:
        form = CadastroAlunoForm()
    return render(request, "acervo/cadastro_aluno.html", {"form": form})


def logout_usuario(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect("home")
