from datetime import timedelta
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .forms import PeriodoForm
from .models import Emprestimo, Livro


def filtrar_periodo(request, qs):
    form = PeriodoForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get("inicio"):
            qs = qs.filter(data_emprestimo__date__gte=form.cleaned_data["inicio"])
        if form.cleaned_data.get("fim"):
            qs = qs.filter(data_emprestimo__date__lte=form.cleaned_data["fim"])
    return qs, form


def obter_dados_dashboard(request):
    agora = timezone.now()

    # Captura a unidade selecionada globalmente no menu
    biblio_ativa = request.session.get("biblioteca_global")

    # Querysets base filtrados por unidade (se houver uma ativa)
    livros_qs = Livro.objects.all()
    emprestimos_qs = Emprestimo.objects.all()

    if biblio_ativa:
        livros_qs = livros_qs.filter(biblioteca=biblio_ativa)
        emprestimos_qs = emprestimos_qs.filter(livro__biblioteca=biblio_ativa)

    base_emprestimos, form_periodo = filtrar_periodo(request, emprestimos_qs)

    # 1. KPIs em uma única consulta com aggregate + Count(filter=Q(...))
    kpis_emp = base_emprestimos.aggregate(
        total_emprestimos=Count("id"),
        leitores_ativos=Count("usuario", distinct=True),
        em_aberto=Count("id", filter=Q(data_devolucao__isnull=True)),
        atrasados=Count(
            "id", filter=Q(data_devolucao__isnull=True, data_prevista__lt=agora)
        ),
    )

    total_exemplares = livros_qs.aggregate(total=Sum("quantidade_total"))["total"] or 0
    total_disponiveis = max(0, total_exemplares - kpis_emp["em_aberto"])

    # 2. Ranking Top-5 (Semanal, Mensal ou Geral)
    periodo_ranking = request.GET.get("ranking", "geral")
    qs_ranking = base_emprestimos
    if periodo_ranking == "semanal":
        qs_ranking = qs_ranking.filter(data_emprestimo__gte=agora - timedelta(days=7))
    elif periodo_ranking == "mensal":
        qs_ranking = qs_ranking.filter(data_emprestimo__gte=agora - timedelta(days=30))

    ranking = list(
        qs_ranking.values("livro__titulo", "livro__autor")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    # 3. Série Temporal por Mês (TruncMonth + order_by)
    por_mes_qs = (
        base_emprestimos.annotate(mes=TruncMonth("data_emprestimo"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("mes")
    )
    por_mes = [
        {"mes": r["mes"].strftime("%m/%Y"), "total": r["total"]}
        for r in por_mes_qs
        if r["mes"]
    ]

    # 4. Distribuição por Categoria (filtrada pela unidade ativa)
    categorias_dict = dict(Livro.CATEGORIAS)
    dist_qs = (
        livros_qs.values("categoria")
        .annotate(total=Sum("quantidade_total"))
        .order_by("-total")
    )
    distribuicao = [
        {
            "categoria": categorias_dict.get(r["categoria"], r["categoria"])[:25],
            "total": r["total"] or 0,
        }
        for r in dist_qs
    ]

    return {
        "form_periodo": form_periodo,
        "periodo_ranking": periodo_ranking,
        "kpis": {
            "total_exemplares": total_exemplares,
            "total_disponiveis": total_disponiveis,
            **kpis_emp,
        },
        "ranking": ranking,
        "por_mes": por_mes,
        "distribuicao": distribuicao,
    }
