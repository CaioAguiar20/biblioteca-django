# Biblioteca Django (Multi-Unidade)

Este projeto foi desenvolvido para a avaliação P2 de Desenvolvimento Web, criando um sistema de biblioteca completo com suporte a múltiplas unidades (Saquarema e Maricá).

Com ele é possível gerir acervos, controlar empréstimos e gerenciar utilizadores com diferentes níveis de acesso.

## O que o sistema faz

- **Seletor Global de Unidades**: Permite alternar a visualização entre as unidades de Saquarema, Maricá ou ver todas consolidadas;
- **Painel do Administrador**: Dashboard com KPIs analíticos, gráficos dinâmicos de distribuição e evolução mensal (Chart.js), controle de devoluções e relatórios em CSV;
- **Área do Aluno**: Consulta de acervo por unidade, sistema de reservas e aba dedicada para acompanhar "Meus Empréstimos" e prazos de devolução;
- **Gestão de Livros (CRUD)**: Cadastra livros com título, autor, ano, tipo (físico/digital), categoria e unidade, permitindo editar, filtrar e excluir com confirmação;
- **Controle de Acessos**: Diferenciação automática entre perfis de Administrador e Aluno.

## Tecnologias usadas

- Python;
- Django;
- SQLite;
- HTML / Bootstrap 5;
- Chart.js;
- Git e GitHub.

## Como rodar o projeto

1. Baixe ou clone este repositório para o seu computador.
2. Entre na pasta do projeto pelo terminal.
3. Crie o ambiente virtual com o comando: `python -m venv venv`
4. Ative o ambiente virtual no Windows com o comando: `venv\Scripts\activate`
5. Instale o Django com o comando: `pip install django`
6. Faça as migrações com o comando: `python manage.py migrate`
7. Crie um administrador com o comando: `python manage.py createsuperuser`
8. Inicie o servidor com o comando: `python manage.py runserver`
9. Abra no navegador o endereço mostrado no terminal (`http://127.0.0.1:8000/`).