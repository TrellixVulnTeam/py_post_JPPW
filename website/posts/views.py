from __future__ import unicode_literals
from urllib.parse import quote 
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect,Http404
from .forms import PostForm
# from django.contrib.contenttypes.models import ContentType #Moved to Commnet models
#Import for search query
from django.db.models import Q
from django.utils import timezone
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from comments.models import Comment
from comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType

# Create your views here.

def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	if not request.user.is_authenticated: # Use 1st or 2nd one to verify user 
		raise Http404	
	form = PostForm(request.POST or None,request.FILES or None)		
	
	# if request.method =="POST":
	# 	print (request.POST.get('title'))
	# 	print ("Hello")
	if form.is_valid():
		instance=form.save(commit=False)
		#print (form.cleaned_data.get("title"))
		instance.user=request.user #Check user is valid and loagged in to post checked user
		instance.save()
		messages.success(request,"Created successfully")
		return HttpResponseRedirect(instance.get_absolute_url())


	context ={
		"form": form
	}
	
	return render(request, 'post_form.html',context)

def post_detail(request,slug=None):
	instance= get_object_or_404(Post,slug=slug)
	if instance.draft or instance.publish.date() >timezone.now().date():
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	share_string=quote(instance.content)

	# content_type=ContentType.objects.get_for_model(Post) #moved to commnets Model
	# object_id   =instance.id
	# comments =Comment.objects.filter(content_type=content_type,object_id=object_id)
	comments =Comment.objects.filter_by_instance(instance)
	initial_data={
		"content_type":instance.get_content_type,
		"object_id":instance.id,

	}
	comment_form=CommentForm(request.POST or None,initial=initial_data)
	if comment_form.is_valid() and request.user.is_authenticated():
		# print(comment_form.cleaned_data)
		c_type=comment_form.cleaned_data.get('content_type')
		content_type=ContentType.objects.get(model=c_type)
		obj_id=comment_form.cleaned_data.get('object_id')
		content_data=comment_form.cleaned_data.get('content')
		parent_obj=None

		try:
			parent_id  = int(request.POST.get('parent_id'))
		except:
			parent_id=None
		if parent_id:
			parent_qs=Comment.objects.filter(id=parent_id)
			if parent_qs and parent_qs.count()==1:
				parent_obj=parent_qs.first()


		new_comment, created=Comment.objects.get_or_create(

								user=request.user,
								content_type=content_type,
								object_id=obj_id,
								content=content_data,
								parent=parent_obj
		
								)
		return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
		if created:
			print("It worked")
			

	context= {
	#"dataset" : queryset,
	"title" : instance.title,
	"instance" : instance,
	"share_string":share_string,
	"comments":comments,
	'comment_form':comment_form
	}

	return render(request, 'post_detail.html',context)
def post_list(request):
	today=timezone.now().date()
	queryset_list=Post.objects.active() #filter(draft=False).filter(publish__lte=timezone.now()) define in Model now #all() #.order_by("-timestapm")
	if  request.user.is_staff or  request.user.is_superuser:
		queryset_list=Post.objects.all()
	#Search start
	query=request.GET.get("search")
	if query:
		queryset_list=queryset_list.filter(
			Q(title__icontains=query) |
			Q(content__icontains=query) |
			Q(user__first_name__icontains=query) |
			Q(user__last_name__icontains=query) 
			).distinct()
	#search end 
	paginator = Paginator(queryset_list, 2) # Show 25 contacts per page
	page_request_var="page"
	page = request.GET.get(page_request_var)
	try:
		queryset_list = paginator.page(page)
	except PageNotAnInteger:
        # If page is not an integer, deliver first page.
		queryset_list = paginator.page(1)
	except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
		queryset_list = paginator.page(paginator.num_pages)

	context= {
	"dataset" : queryset_list,
	"title" : "list",
	"page_request_var" :page_request_var,
	'today':today
	}

	return render(request, 'posts_list.html', context)

def post_update(request, slug=None):
	instance= get_object_or_404(Post,slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	
	# if request.method =="POST":
	# 	print (request.POST.get('title'))
	# 	print ("Hello")
	if form.is_valid():
		instance=form.save(commit=False)
		#print (form.cleaned_data.get("title"))
		instance.save()
		#Mess success
		messages.success(request,"Upadated successfully")
		return HttpResponseRedirect(instance.get_absolute_url())
	# else:
	# 	messages.error(request,"Not Upadated ")		
	context= {
	#"dataset" : queryset,
	"title" : instance.title,
	"instance" : instance,
	"form": form
	}

	return render(request, 'post_update.html',context)
def post_delete(request,id=None):
	instance= get_object_or_404(Post,id=id)
	# form = PostForm(request.POST or None)	
	instance.delete()
	messages.success(request,"Deleted successfully")
	return redirect("posts:list")              
