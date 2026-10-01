# Biblioteca Django

Este projeto foi feito para praticar Django e criar um sistema simples de biblioteca.

Com ele é possível cadastrar livros e organizar o acervo. Também é possível pesquisar, editar e excluir os livros cadastrados.

## O que o sistema faz

- Cadastra livros com título, autor e ano;
- Define se o livro é físico ou digital;
- Organiza os livros por categoria;
- Mostra os livros em uma tabela;
- Pesquisa por título ou nome do autor;
- Filtra por tipo e categoria;
- Ordena por título ou ano;
- Permite editar os dados de um livro;
- Permite excluir um livro com confirmação.

## Tecnologias usadas

- Python;
- Django;
- SQLite;
- HTML;
- Git e GitHub.

## Como rodar o projeto

1. Baixe ou clone este repositório para o seu computador.
2. Entre na pasta do projeto pelo terminal.
3. Crie o ambiente virtual com o comando: python -m venv venv
4. Ative o ambiente virtual no Windows com o comando: venv\Scripts\activate
5. Instale o Django com o comando: pip install django
6. Faça as migrações com o comando: python manage.py migrate
7. Inicie o servidor com o comando: python manage.py runserver
8. Abra no navegador o endereço mostrado no terminal.