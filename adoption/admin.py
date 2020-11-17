from django.contrib import admin
from adoption.models import Comment, Post
# Register your models here.


class CommentAdminInline(admin.StackedInline):
    model = Comment
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'kind')
    search_fields = ('pk', 'title',)
    readonly_fields = ('pk', )
    inlines = (CommentAdminInline,)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created', 'author')
    search_fields = ('pk', 'author')
    readonly_fields = ('pk',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()