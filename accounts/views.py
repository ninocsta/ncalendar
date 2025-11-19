from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views


class CustomLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Apply DaisyUI classes to widgets so template doesn't need to pass attrs
        username_widget = form.fields.get('username').widget
        password_widget = form.fields.get('password').widget
        username_widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Seu usuário ou e-mail',
            'id': 'username',
        })
        password_widget.attrs.update({
            'class': 'input input-bordered w-full',
            'placeholder': 'Sua senha',
            'id': 'password',
        })
        return form

