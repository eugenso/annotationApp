from django.contrib import admin

from .models import Document, Label, Annotation, QueueElement, AnnotationQueue, NBC_class_count, NBC_word_count_given_class, NBC_vocabulary

admin.site.register(Document)
admin.site.register(Label)
admin.site.register(Annotation)
admin.site.register(QueueElement)
admin.site.register(AnnotationQueue)
admin.site.register(NBC_class_count)
admin.site.register(NBC_word_count_given_class)
admin.site.register(NBC_vocabulary)


# from django.conf.urls import url

# class MyModelAdmin(admin.ModelAdmin):
#     def get_urls(self):
#         urls = super(MyModelAdmin, self).get_urls()
#         my_urls = [
#             url(r'^my_view/$', self.my_view),
#                 ]
#         with open('/tmp/log.txt', 'w') as f:
#             f.write(urls.__str__())
#             f.write(my_urls.__str__())
#         return my_urls + urls

#     def my_view(self, request):
#         # custom view which should return an HttpResponse
#         pass

# admin.site.register(Annotation, MyModelAdmin)
