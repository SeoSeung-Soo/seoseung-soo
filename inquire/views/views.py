
from django.http import HttpRequest, JsonResponse
from django.views import View

from inquire.forms.inqurie_create import InquireForm
from inquire.services.inquire_user_valid import InquireUserValidService


class InquireView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        form = InquireForm(request.POST, user=request.user)

        if not form.is_valid():
            return JsonResponse({'success': False, 'message': '입력한 정보를 확인해주세요.'})

        data = form.cleaned_data
        user, email = InquireUserValidService.validate_inquire_user_valid(request.user)

        if not email:
            if 'email' in data:
                email = data['email']
            else:
                email = request.user.email if request.user.is_authenticated else None

        if not email:
            return JsonResponse({'success': False, 'message': '이메일 주소를 입력해주세요.'})

        success, message = InquireUserValidService.process_inquire(
            user=user,
            email=email,
            title=data['title'],
            content=data['content'],
            item=data['item']
        )

        return JsonResponse({'success': success, 'message': message})