from django.urls import path
from . import views


urlpatterns = [
    path("livros/", views.lista_livros, name="lista_livros"),
    path("livros/novo/", views.novo_livro, name="novo_livro"),
    path("livros/<int:livro_id>/editar/", views.editar_livro, name="editar_livro"),
    path("livros/<int:livro_id>/excluir/", views.excluir_livro, name="excluir_livro"),
]