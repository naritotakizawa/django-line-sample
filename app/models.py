from django.db import models
from django.utils import timezone


class LinePush(models.Model):
    """Lineでのプッシュ先を表す"""
    user_id = models.CharField('ユーザーID', max_length=100, unique=True)
    display_name = models.CharField('表示名', max_length=255, blank=True)

    def __str__(self):
        return self.display_name


class LineMessage(models.Model):
    """Lineの各メッセージを表現する"""
    push = models.ForeignKey(LinePush, verbose_name='プッシュ先', on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField('テキスト')
    is_admin = models.BooleanField('このメッセージは管理者側の発言か', default=True)
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return f'{self.push} - {self.text[:10]} - {self.is_admin}'

