from django.contrib import admin

from .models import Comment, Follow, Group, Post


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("slug",)
    empty_value_display = "-пусто-"
    prepopulated_fields = {'slug': ('title',)}


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date", "group")
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "post", "author", "text", "created")
    search_fields = ("text",)
    list_filter = ("post", "author", "created")
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    list_filter = ("user", "author")


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
