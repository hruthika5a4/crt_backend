from django.contrib import admin

from crt_app.models import *

class TopicAdmin(admin.TabularInline):
    model = Topic

class LessonPlanAdmin(admin.ModelAdmin):
   inlines = [TopicAdmin,]

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(Topic)
admin.site.register(LessonPlan,LessonPlanAdmin)
admin.site.register(Approval)
admin.site.register(College)
