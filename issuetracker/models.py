from django.db import models

# abstract class for models with creation date


class __HasCreationDate(models.Model):
    datetime_created = models.DateTimeField()

    class Meta:
        abstract = True


class User(__HasCreationDate):
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=256)
    is_admin = models.BooleanField()

    # get the checkbox value for the admin field in the edit user form
    def is_admin_checkbox(self):
        return 'checked' if self.is_admin else ''


# abstract class for models with creation date plus author
class __HasAuthorAndCreationDate(__HasCreationDate):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True

    # method to return readable description including creation date and author
    def get_creation_details(self):
        author_name = "deleted user" if self.author == None else self.author.nickname
        return f'Created by {author_name} at {self.datetime_created:%d %b %Y %H:%M}.'


class Category(__HasAuthorAndCreationDate, __HasCreationDate):
    name = models.CharField(max_length=128)


class Issue(__HasAuthorAndCreationDate, __HasCreationDate):
    title = models.CharField(max_length=128)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=512)


class Comment(__HasAuthorAndCreationDate, __HasCreationDate):
    parent_issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    text = models.CharField(max_length=512)

    def get_title_and_text(self):
        return f'Issue: {self.parent_issue.title}\r\n>\r\nComment: {self.text}'
