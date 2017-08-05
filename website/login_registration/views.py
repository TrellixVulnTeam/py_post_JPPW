from django.shortcuts import render,redirect
from django.contrib.auth import (
	authenticate,
	get_user_model,
	login,
	logout
	)

from .forms import UserLoginForm
from .forms import UserRegisterForm
# Create your views here.

def login_view(request):
	print(request.user.is_authenticated())
	next2=request.GET.get("next")
	form=UserLoginForm(request.POST or None)
	title="Login"
	if form.is_valid():
		username=form.cleaned_data.get("username")
		password=form.cleaned_data.get("password")
		user= authenticate(username=username,password=password)
		login(request,user)
		if next2:
			return redirect(next2)
		return redirect('/')
		print(request.user.is_authenticated())
	context={
		"form":form,
		"title":title
	}	
	return render(request,'form.html',context)
def register_view(request):
	title="Register"
	next2=request.GET.get("next")
	form=UserRegisterForm(request.POST or None)
	if form.is_valid():
		username=form.cleaned_data.get("username")
		email  = form.cleaned_data.get("email")
		password= form.cleaned_data.get("password")
		user=form.save(commit=False)
		user.set_password(password)
		user.save()
		new_user= authenticate(username=username,password=password)
		login(request,user)
		if next2:
			return redirect(next2)
		return redirect('/')
	context={
		"form":form,
		"title":title
	}	
	return render(request,'form.html',context)

def logout_view(request):
	logout(request)
	return redirect('/')
