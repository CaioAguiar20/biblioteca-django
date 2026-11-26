from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("livros/", views.lista_livros, name="lista_livros"),
    path("livros/novo/", views.novo_livro, name="novo_livro"),
    path("livros/<int:livro_id>/editar/", views.editar_livro, name="editar_livro"),
    path("livros/<int:livro_id>/excluir/", views.excluir_livro, name="excluir_livro"),
    path(
        "livros/<int:livro_id>/reservar/", views.reservar_livro, name="reservar_livro"
    ),
    path("meus-emprestimos/", views.meus_emprestimos, name="meus_emprestimos"),
    path("painel-admin/", views.painel_admin, name="painel_admin"),
    path(
        "devolver/<int:emprestimo_id>/",
        views.registrar_devolucao,
        name="registrar_devolucao",
    ),
    path("exportar-csv/", views.exportar_csv, name="exportar_csv"),
    path("api/dashboard/", views.api_dashboard, name="api_dashboard"),
    path("login/", views.login_usuario, name="login_usuario"),
    path("cadastro/", views.cadastro_aluno, name="cadastro_aluno"),
    path("logout/", views.logout_usuario, name="logout_usuario"),
]
