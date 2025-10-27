from django import forms


class FavoriteForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def clean_product_id(self) -> int:
        product_id = self.cleaned_data.get('product_id')
        if not product_id:
            raise forms.ValidationError('상품 ID가 필요합니다.')
        return int(product_id)