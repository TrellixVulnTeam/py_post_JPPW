from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,Http404
from .models import Comment
from .forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

# @login_required(login_url='/login/') #Login url = '/login/'

def comment_thread(request,id):
	obj=get_object_or_404(Comment,id=id)
	content_object=obj.content_object
	content_id=obj.content_object.id
	# initial_data={
	# 	"content_type":content_object.get_content_type,
	# 	"object_id":content_id,

	# }
	initial_data={
		"content_type":obj.content_type,
		"object_id":obj.object_id,

	}
	comment_form=CommentForm(request.POST or None,initial=initial_data)
	print(comment_form.errors)
	# print(dir(comment_form))
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
	context={
	"comment": obj,
	'form':comment_form
	}
	return render (request,'comment_thread.html',context)
	