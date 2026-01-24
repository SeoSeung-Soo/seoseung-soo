from typing import Any

from django import forms

from orders.models import Order


class OrderCancellationForm(forms.Form):
    reason = forms.ChoiceField(
        label="취소 사유",
        choices=Order.CancellationReason.choices,
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control"
        }),
        help_text="취소 사유를 선택해주세요."
    )

    def __init__(self, *args: Any, order: Order | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.order = order

    def clean_reason(self) -> str:
        reason = self.cleaned_data.get("reason", "").strip()
        if not reason:
            raise forms.ValidationError("취소 사유를 선택해주세요.")
        valid_reasons = [choice[0] for choice in Order.CancellationReason.choices]
        if reason not in valid_reasons:
            raise forms.ValidationError("유효하지 않은 취소 사유입니다.")
        return str(reason)
