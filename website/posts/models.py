from django.db import models
from django.db.models.signals import pre_save #Do something before model is saved for slug
from django.utils.text import slugify
from django.conf import settings 
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
from django.core.urlresolvers import reverse
from markdown_deux import markdown
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User
# Create your models here.
#Post.objects.all() model manager
#Post.objects.create(user=user, title='any name') #with all required field to create Django
#Those are model manager 
class PostManager(models.Manager):
	def active(self, *args,**kwargs):
		#Post.objects.all() is refer to super
		return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())
		
		
def upload_location(instance,filename):
	#filebase, extension = filename.split(".")
	#return "%s%s.%s" %(instance.id,instance.id,filename) not good practice
	return "%s%s.%s" %(instance.id,instance.id,filename)
class Post(models.Model):
	user    = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
	title   = models.CharField(max_length=120)
	slug	= models.SlugField(unique=True)
	draft	=models.BooleanField(default=False)
	publish =models.DateTimeField(auto_now=False,auto_now_add=False)
	# image   = models.FileField(null=True,blank=True)
	image   = models.ImageField(upload_to=upload_location,null=True,blank=True,
		      height_field="height_field",
		      width_field="width_field")
	height_field = models.IntegerField(default=0)
	width_field = models.IntegerField(default=0)
	content = models.TextField()
	updated = models.DateTimeField(auto_now=True,auto_now_add=False)
	timestapm = models.DateTimeField(auto_now=False,auto_now_add=True)

	objects= PostManager()
	
	def __unicode__(self):
		return self.title
		
	def __str__(self):
		return self.title

	def get_absolute_url(self):
		# return "/posts/%s" %(self.id)
		return reverse("posts:detail",kwargs={"slug": self.slug})
	def get_markdown(self):
		content=self.content
		markdown_text=markdown(content)
		return mark_safe(markdown_text)
	@property
	def comments(self):
		instance=self
		qs=Comment.objects.filter_by_instance(instance)
		return qs	

	@property
	def get_content_type(self):
		instance=self
		qs=ContentType.objects.get_for_model(instance.__class__)
		return qs	
	class Meta:
		ordering=["-timestapm","updated"]	#negative sign manes reverse




def create_slug(instance, new_slug=None):
	slug =slugify(instance.title)
	if new_slug is not None:
		slug=new_slug
	qs=Post.objects.filter(slug=slug).order_by("-id")
	exists= qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug,qs.first().id)
		return create_slug(instance,new_slug=new_slug)
	return slug


def pre_save_post_receiver(sender,instance,*args,**kwargs):
	if not instance.slug:
		instance.slug=create_slug(instance)
	# slug =slugify(instance.title)
	# exists=Post.objects.filter(slug=slug).exists()
	# if exists:
	# 	slug= "%s-%s" %(slug,instance.id)

	# instance.slug=slug




pre_save.connect(pre_save_post_receiver,sender=Post)	 		