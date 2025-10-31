from typing import Any

from django import forms

from products.models import Color


class ProductColorForm(forms.ModelForm): # type: ignore
    hex_code = forms.CharField(
        max_length=7,
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'color',
            'class': 'color-picker',
            'placeholder': '#000000'
        }),
        help_text='색상을 선택하거나 HEX 코드를 입력하세요.'
    )
    
    class Meta:
        model = Color
        fields = ['name', 'hex_code']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '색상 이름 (예: 빨강, 파랑)'
            }),
        }
        labels = {
            'name': '색상 이름',
            'hex_code': 'HEX 코드',
        }
        help_texts = {
            'name': '색상의 이름을 입력하세요.',
            'hex_code': '색상을 선택하거나 HEX 코드를 입력하세요.',
        }
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        value = '#000000'
        if self.is_bound:
            value = self.data.get('hex_code', '#000000')
        elif self.instance and self.instance.pk:
            value = self.instance.hex_code or '#000000'
        self.fields['hex_code'].widget.attrs['value'] = value