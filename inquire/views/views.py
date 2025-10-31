
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from inquire.forms.inqurie_create import InquireForm
from inquire.services.inquire_user_valid import InquireUserValidService


class InquireView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        form = InquireForm(user=request.user)

        context = {'form': form}
        return render(request, 'inquire/inquire.html', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = InquireForm(request.POST, user=request.user)

        context = {'form': form}

        if not form.is_valid():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': '입력한 정보를 확인해주세요.'})
            return render(request, 'inquire/inquire.html', context)

        data = form.cleaned_data
        user, email = InquireUserValidService.validate_inquire_user_valid(request.user)

        if not email:
            if 'email' in data:
                email = data['email']
            else:
                email = request.user.email if request.user.is_authenticated else None

        if not email:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': '이메일 주소를 입력해주세요.'})
            return render(request, 'inquire/inquire.html', context)

        success, message = InquireUserValidService.process_inquire(
            user=user,
            email=email,
            title=data['title'],
            content=data['content'],
            item=data['item']
        )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': success, 'message': message})

        if success:
            return redirect('inquire_success')
        else:
            return render(request, 'inquire/inquire.html', context)


class InquireSuccessView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'inquire/inquire_success.html')