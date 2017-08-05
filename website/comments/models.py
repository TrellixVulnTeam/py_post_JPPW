from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# from posts.models import Post

# Create your models here.
class CommentManager(models.Manager):
	def all(self):
		qs=super(CommentManager, self).filter(parent=None)
		return qs
	"""docstring for ClassName"""
	def filter_by_instance(self, instance):
		content_type=ContentType.objects.get_for_model(instance.__class__) # is equal to (Post)
		object_id   =instance.id
		query_set   = super(CommentManager,self).filter(content_type=content_type,object_id=object_id).filter(parent=None)
		#Comment.objetcs ==Supper(CommentManager,self) is refering Commnet supper calss
		return query_set
		# comments =Comment.objects.filter(content_type=content_type,object_id=object_id)



class Comment(models.Model):

	user      = models.ForeignKey(settings.AUTH_USER_MODEL,default=1)
	#post      = models.ForeignKey(Post)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	content	  = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	parent	  =models.ForeignKey("self",null=True,blank=True)

	objects =CommentManager() #Instanciating 
	class Meta:
		ordering=['-timestamp']
	def __unicode__(self):
		return str(self.user.username)
	def __str__(self):
		return str(self.user.username)

	def get_get_absolute_url(self):
		# return "/posts/%s" %(self.id)
		return reverse("comments:thread",kwargs={"id": self.id})
	def children(self): #replies under comment
		return Comment.objects.filter(parent=self)
	@property 
	def is_parent(self):
		if self.parent is not None:
			return True
		return False

		
	"""docstring for ClassName"""
	# def __init__(self, arg):
	# 	super(ClassName, self).__init__()
	# 	self.arg = arg

