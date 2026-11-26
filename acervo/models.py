from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Livro(models.Model):
    TIPO_ACERVO = [
        ("digital", "Digital"),
        ("fisico", "Físico"),
    ]

    BIBLIOTECAS = [
        ("saquarema", "Biblioteca Saquarema"),
        ("marica", "Biblioteca Maricá"),
    ]

    CATEGORIAS = [
        ("000", "000 – Generalidades e Informação"),
        ("100", "100 – Filosofia e Psicologia"),
        ("200", "200 – Religião e Teologia"),
        ("300", "300 – Ciências Sociais e Direito"),
        ("400", "400 – Linguística e Idiomas"),
        ("500", "500 – Ciências Puras"),
        ("600", "600 – Ciências Aplicadas"),
        ("700", "700 – Artes e Recreação"),
        ("800", "800 – Literatura"),
        ("900", "900 – História e Geografia"),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    ano = models.IntegerField()

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_ACERVO,
        default="fisico",
    )

    biblioteca = models.CharField(
        max_length=20,
        choices=BIBLIOTECAS,
        default="saquarema",
        verbose_name="Unidade / Biblioteca",
    )

    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIAS,
        default="000",
    )

    quantidade_total = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade Total",
    )

    prazo_dias = models.PositiveIntegerField(
        default=7,
        verbose_name="Prazo de Empréstimo (dias)",
    )

    @property
    def quantidade_emprestada(self):
        return self.emprestimos.filter(data_devolucao__isnull=True).count()

    @property
    def quantidade_disponivel(self):
        return max(0, self.quantidade_total - self.quantidade_emprestada)

    def __str__(self):
        return f"{self.titulo} ({self.get_biblioteca_display()})"


class Emprestimo(models.Model):
    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name="emprestimos",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="emprestimos",
    )
    data_emprestimo = models.DateTimeField(default=timezone.now)
    data_prevista = models.DateTimeField()
    data_devolucao = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["data_emprestimo"]),
        ]

    def save(self, *args, **kwargs):
        if not self.data_prevista:
            self.data_prevista = self.data_emprestimo + timedelta(
                days=self.livro.prazo_dias
            )
        super().save(*args, **kwargs)

    @property
    def esta_atrasado(self):
        if self.data_devolucao:
            return False
        return timezone.now() > self.data_prevista

    @property
    def dias_restantes(self):
        if self.data_devolucao:
            return 0
        return (self.data_prevista.date() - timezone.now().date()).days

    @property
    def dias_com_livro(self):
        fim = self.data_devolucao if self.data_devolucao else timezone.now()
        return max(0, (fim.date() - self.data_emprestimo.date()).days)

    def __str__(self):
        return f"{self.livro.titulo} - {self.usuario.username}"
