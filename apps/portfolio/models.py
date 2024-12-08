from django.db import models
from apps.photo.models import Photo
from apps.users.models import Studio, Photographer
from django.core.exceptions import ValidationError


class Portfolio(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='portfolios', null=True, blank=True)
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE, related_name='portfolios', null=True,
                                     blank=True)

    description = models.TextField()
    photos = models.ManyToManyField(Photo, through='PortfolioPhotos', related_name='portfolios')

    def __str__(self):
        owner = self.studio if self.studio else self.photographer
        return f"Portfolio {self.id} ({owner})"

    def clean(self):
        if not self.studio and not self.photographer:
            raise ValidationError('Портфолио должно принадлежать либо Studio, либо Photographer.')
        if self.studio and self.photographer:
            raise ValidationError('Портфолио не может одновременно принадлежать и Studio, и Photographer.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class PortfolioPhotos(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'portfolio_photos'
        unique_together = ('portfolio', 'photo')

    def __str__(self):
        return f"Portfolio {self.portfolio.id} - Photo {self.photo.id}"
