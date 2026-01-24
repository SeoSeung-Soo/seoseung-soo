from django import forms

from orders.models import Order


class OrderCancellationForm(forms.Form):
    reason = forms.ChoiceField(
        label="취소 사유",
        choices=[('', '--- 취소 사유를 선택해주세요 ---')] + list(Order.CancellationReason.choices),
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "cancellationReason"
        }),
        help_text="취소 사유를 선택해주세요."
    )
