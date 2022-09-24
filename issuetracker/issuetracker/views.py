from datetime import datetime
from logging import exception
import os
import re
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
import django.contrib.auth.password_validation as validators

from issuetracker import admin
from .models import Category
from .models import User
from .models import Issue
from .models import Comment
import issuetracker.forms as forms
from web_project.settings import AUTH_PASSWORD_VALIDATORS, BASE_DIR
import django.contrib.auth.hashers as hashers
# Create your views here.


def index(request):
    return render(request, 'index.html')


def register(request):
    if __check_user_is_authenticated(request):
        return redirect('/categories')
    error_messages = []
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['username'].replace(' ', '')
            try:
                user = __get_user_from_username(new_username)
                error_messages.append(
                    'User with this username already exists.')
            except User.DoesNotExist:  # user not already registered
                pass
            password_validation = __validate_password_secure(
                form.cleaned_data['password'])
            if password_validation != None:
                error_messages.append(password_validation)
            if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
                error_messages.append('Passwords do not match.')
            if len(error_messages) == 0:
                user = User()
                user.username = new_username
                # https://docs.djangoproject.com/en/4.1/topics/auth/passwords/
                # hash password using django's built-in hashers. these implement the industry-standard PBKDF2 algorithm
                user.password = hashers.make_password(
                    form.data['password'])
                user.is_admin = form.cleaned_data['is_admin']
                user.datetime_created = datetime.now()
                user.nickname = form.cleaned_data['nickname']
                user.save()
                return redirect('/login')
            else:
                error_messages.insert(0, 'There were issues registering:')
                pass
        else:
            error_messages.append(
                'There were issues registering:\r\n' + form.errors.as_text())

    else:
        return render(request, 'register.html', {'message': '\r\n'.join(error_messages)})


def login(request):
    # testtest
    # restrest1
    error_messages = []
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            try:
                user = __get_user_from_username(form.cleaned_data['username'])
                if hashers.check_password(form.cleaned_data['password'], user.password):
                    __set_session_vars(request, user, True)
                    return redirect('/categories')
                else:
                    error_messages.append('Invalid password')
            except User.DoesNotExist:
                error_messages.append('User does not exist, invalid username')
        else:
            error_messages.append(
                'There was an issue logging in: ' + form.errors.as_text())
    if __check_user_is_authenticated(request):
        return redirect('/categories')
    else:
        return render(request, 'login.html', {'message': '\r\n'.join(error_messages)})


def logout(request):
    if not __check_user_is_authenticated(request):
        return redirect('/login')

    if request.method == 'POST':
        __set_session_vars(request, None, False)
        return redirect('/')

    return render(request, 'logout_confirm.html')


def user_options(request):
    if not __check_user_is_authenticated(request):
        return redirect('/login')
    user = __get_user_from_request_user_id(request)
    return render(request, 'user_options.html', {'user': user})


def change_nickname(request):
    if not __check_user_is_authenticated(request):
        return redirect('/login')

    user = __get_user_from_request_user_id(request)
    messages = []
    if request.method == 'POST':
        form = forms.ChangeNicknameForm(request.POST)
        if form.is_valid():
            old_nickname = user.nickname
            if len(messages) == 0:
                user = __get_user_from_request_user_id(request)
                user.nickname = form.data['nickname']
                user.save()
                messages.append(
                    f'Nickname changed successfully from {old_nickname} to {user.nickname}.')
        else:
            messages.append(
                'There was an issue changing nickname: ' + form.errors.as_text())

    return render(request, 'change_nickname.html', {'user': user, 'message': '\r\n'.join(messages)})


def change_password(request):
    if not __check_user_is_authenticated(request):
        return redirect('/login')
    messages = []
    if request.method == 'POST':
        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            password_validation = __validate_password_secure(
                form.data['new_password'])
            if password_validation != None:
                messages.append(
                    'Password does not meet requirements: '+password_validation)
            if form.data['new_password'] != form.data['confirm_password']:
                messages.append('Passwords do not match.')
            if len(messages) == 0:
                user = __get_user_from_request_user_id(request)
                user.password = hashers.make_password(
                    form.data['new_password'])
                user.save()
                messages.append('Password changed successfully.')
        else:
            messages.append(
                'There was an issue changing password: ' + form.errors.as_text())

    return render(request, 'change_password.html', {'message': '\r\n'.join(messages)})


def users_list(request):
    if not __check_user_is_authenticated_admin(request):
        return redirect('/login')
    users = User.objects.all()
    return render(request, 'users_list.html', {'users': users})


def admin_update_user(request, user_id):
    if not __check_user_is_authenticated_admin(request):
        return redirect('/categories')

    messages = []
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    if request.method == 'POST':
        form = forms.AdminEditUserForm(request.POST)
        if form.is_valid():
            provided_username = form.data['username'] != ''
            provided_nickname = form.data['nickname'] != ''
            provided_password = form.data['password'] != ''
            provided_is_admin = form.cleaned_data['is_admin'] != user.is_admin
            if (not provided_username and not provided_nickname and
                    not provided_password and not provided_is_admin):
                messages.append('Error: No new changes submit.')

            if len(messages) == 0:
                if provided_password:
                    user.password = hashers.make_password(
                        form.data['password'])
                if provided_username:
                    user.username = form.data['username']
                if provided_nickname:
                    user.nickname = form.data['nickname']
                if provided_is_admin:
                    user.is_admin = form.data['is_admin']

                user.save()
                messages.append('User edited successfully.')
        else:
            messages.append(
                'There was an issue editing user: ' + form.errors.as_text())
    return render(request, 'admin_update_user.html', {'user': user, 'messages': '\r\n'.join(messages)})


def admin_delete_user(request, user_id):
    if not __check_user_is_authenticated_admin(request):
        return redirect('/login')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    if request.method == 'POST':
        user.delete()
        return redirect('/users')

    form_method = request.path
    return render(request, 'admin_delete_user.html', {'user': user, 'form_method': form_method})


def categories(request):
    if not __check_user_is_authenticated(request):
        return redirect('/login')
    categories = Category.objects.all()
    return render(request, 'view_categories.html', {'categories': categories})


def category(request, category_id):
    if not __check_user_is_authenticated(request):
        return redirect('/login')
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        raise Http404("Category does not exist")
    return render(request, 'category.html', {'category': category})


def create_category(request):
    if not __check_user_is_authenticated(request):
        return redirect('/login')
    if request.method == 'POST':
        form = forms.CreateCategoryForm(request.POST)
        if form.is_valid():
            Category.objects.create(name=form.data['title'], author=__get_user_from_request_user_id(request),
                                    datetime_created=datetime.now())
            return redirect('categories')
    return render(request, 'create_category.html')


def view_category(request, category_id):
    if not __check_user_is_authenticated(request):
        return redirect('/login')
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        raise Http404("Category does not exist")

    issues = Issue.objects.filter(parent_category_id=category_id)
    return render(request, 'view_category.html', {'category': category, 'issues': issues})


def delete_category_plus_children_plus_image_files(request, category_id):
    if not __check_user_is_authenticated_admin(request):
        return redirect('/login')
    try:
        category = Category.objects.get(pk=category_id)
    except User.DoesNotExist:
        raise Http404("Category does not exist")
    if request.method == 'POST':
        issues = Issue.objects.filter(parent_category_id=category_id)
        # Delete child issues manually to make sure delete images + comment images.
        # even though cascade FK constraint delete will delete child items, won't delete the images.
        for issue in issues:
            __delete_issue_plus_children_plus_image_files(issue)
        category.delete()
        return redirect('/categories')
# todo: add form
    form_method = request.path
    return render(request, 'admin_delete_category.html', {'category': category, 'form_method': form_method})


def create_issue(request, category_id):
    if request.method == 'POST':
        form = forms.CreateIssueForm(request.POST, request.FILES)
        if form.is_valid():
            # get filename from request.FILES
            image_filename = ''
            request_file = request.FILES.get('image')
            if request_file is not None:
                error = __check_for_image_errors(request_file)
                if error == '':
                    __handle_image_upload(request_file)
                    image_filename = request_file.name
                else:
                    return HttpResponse(status=500, content='Error 500 invalid image - ' + error)

            parent_category = Category.objects.get(pk=category_id)
            issue = Issue.objects.create(title=form.data['title'],
                                         description=form.data['text'],
                                         image_filename=image_filename,
                                         author=__get_user_from_request_user_id(
                                             request),
                                         parent_category=parent_category,
                                         datetime_created=datetime.now())

            issue_id = issue.id
            return redirect('view_issue', category_id=category_id, issue_id=issue_id)
        else:
            return HttpResponse(status=500, content='Error 500 invalid form - ' + form.errors.as_text())

    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        raise Http404("Category does not exist")

    return render(request, 'create_issue.html', {'category': category})


def update_issue(request, category_id, issue_id):
    try:
        issue = Issue.objects.get(pk=issue_id)
    except Issue.DoesNotExist:
        raise Http404("Issue does not exist")

    if not __check_user_has_update_permission(request, issue.author.id):
        return redirect('view_issue', category_id=category_id, issue_id=issue_id)

    messages = []
    if request.method == 'POST':
        form = forms.UpdateIssueForm(request.POST, request.FILES)
        if form.is_valid():
            # get filename from request.FILES
            image_filename = ''
            request_file = request.FILES.get('image')
            if request_file is not None:
                error = __check_for_image_errors(request_file)
                if error == '':
                    __handle_image_upload(request_file)
                    image_filename = request_file.name
                else:
                    messages.append('Error 500 invalid image - ' + error)

            provided_image = image_filename != ''
            provided_title = form.data['title'] != ''
            provided_text = form.data['text'] != ''

            if (not provided_image and not provided_text and
                    not provided_title):
                messages.append('Error: No new changes submit.')

            if len(messages) == 0:
                if provided_image:
                    # delete the old image
                    __delete_image(issue.image_filename)
                    issue.image_filename = image_filename
                if provided_title:
                    issue.title = form.data['title']
                if provided_text:
                    issue.description = form.data['text']

                issue.save()
                messages.append('User edited successfully.')

            issue_id = issue.id
            return redirect('view_issue', category_id=category_id, issue_id=issue_id)
        else:
            return HttpResponse(status=500, content='Error 500 invalid form - ' + form.errors.as_text())

    return render(request, 'update_issue.html', {'category_id': category_id, 'issue': issue, 'messages': messages})


def update_comment(request, category_id, issue_id, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        raise Http404("Comment does not exist")

    if not __check_user_has_update_permission(request, comment.author.id):
        return redirect('view_issue', category_id=category_id, issue_id=issue_id)

    messages = []
    if request.method == 'POST':
        form = forms.UpdateCommentForm(request.POST, request.FILES)
        if form.is_valid():
            # get filename from request.FILES
            image_filename = ''
            request_file = request.FILES.get('image')
            if request_file is not None:
                error = __check_for_image_errors(request_file)
                if error == '':
                    __handle_image_upload(request_file)
                    image_filename = request_file.name
                else:
                    messages.append('Error 500 invalid image - ' + error)

            provided_image = image_filename != ''
            provided_text = form.data['text'] != ''

            if (not provided_image and not provided_text):
                messages.append('Error: No new changes submit.')

            if len(messages) == 0:
                if provided_image:
                    # delete the old image
                    __delete_image(comment.image_filename)
                    comment.image_filename = image_filename
                if provided_text:
                    comment.text = form.data['text']

                comment.save()
                messages.append('User edited successfully.')

            return redirect('view_issue', category_id=category_id, issue_id=issue_id)
        else:
            return HttpResponse(status=500, content='Error 500 invalid form - ' + form.errors.as_text())

    return render(request, 'update_comment.html', {'category_id': category_id, 'issue_id': issue_id, 'comment': comment, 'messages': messages})


def update_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        raise Http404("Category does not exist")

    if not __check_user_has_update_permission(request, category.author.id):
        return redirect('view_category', category_id=category_id)

    messages = []
    if request.method == 'POST':
        form = forms.UpdateCategoryForm(request.POST, request.FILES)
        if form.is_valid():

            provided_title = form.data['title'] != ''

            if len(messages) == 0:
                if provided_title:
                    category.name = form.data['title']

                category.save()
                messages.append('User edited successfully.')

            return redirect('view_category', category_id=category_id)
        else:
            return HttpResponse(status=500, content='Error 500 invalid form - ' + form.errors.as_text())

    return render(request, 'update_category.html', {'category': category, 'messages': messages})


def view_issue(request, category_id, issue_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        raise Http404("Category does not exist")

    try:
        issue = Issue.objects.get(pk=issue_id)
    except Issue.DoesNotExist:
        raise Http404("Issue does not exist")
    # the issue might not have any comments, this is fine
    comments = Comment.objects.filter(parent_issue_id=issue_id)
    return render(request, 'view_issue.html', {'category': category, 'issue': issue, 'comments': comments})


def create_comment(request, category_id, issue_id):
    if request.method == 'POST':
        form = forms.CreateCommentForm(request.POST, request.FILES)
        if form.is_valid():
            # get filename from request.FILES
            image_filename = ''
            request_file = request.FILES.get('image')
            if request_file is not None:
                error = __check_for_image_errors(request_file)
                if error == '':
                    __handle_image_upload(request_file)
                    image_filename = request_file.name
                else:
                    return HttpResponse(status=500, content='Error 500 invalid image - ' + error)

            parent_issue = Issue.objects.get(pk=issue_id)
            Comment.objects.create(text=form.data['text'],
                                   image_filename=image_filename,
                                   author=__get_user_from_request_user_id(
                                       request),
                                   parent_issue=parent_issue,
                                   datetime_created=datetime.now())
            return redirect('view_issue', category_id=category_id, issue_id=issue_id)
        else:
            return HttpResponse(status=500, content='Error 500 Invalid form - ' + form.errors.as_text())

    return render(request, 'create_comment.html')


def delete_comment_image(request, category_id, issue_id, comment_id):
    # only admins have delete access
    if not __check_user_is_authenticated_admin(request):
        return redirect('/login')
    try:
        comment = Comment.objects.get(pk=comment_id)
    except User.DoesNotExist:
        raise Http404("Comment does not exist")
    if request.method == 'POST':
        # Delete image method to sure delete image files.
        __delete_image(comment.image_filename)
        comment.image_filename = ''
        comment.save()
        return redirect('view_issue', category_id=category_id, issue_id=issue_id)

    form_method = request.path
    return render(request, 'admin_delete_image.html', {'owner': comment, 'form_method': form_method})


def delete_issue_image(request, category_id, issue_id):
    if not __check_user_is_authenticated_admin(request):
        return redirect('/login')
    try:
        issue = Issue.objects.get(pk=issue_id)
    except User.DoesNotExist:
        raise Http404("Issue does not exist")
    if request.method == 'POST':
        # Delete image method to sure delete image files.
        __delete_image(issue.image_filename)
        issue.image_filename = ''
        issue.save()
        return redirect('view_issue', category_id=category_id, issue_id=issue_id)

    form_method = request.path
    return render(request, 'admin_delete_image.html', {'owner': issue, 'form_method': form_method})


def delete_comment(request, category_id, issue_id, comment_id):
    if not __check_user_is_authenticated_admin(request):
        return redirect('/login')
    try:
        comment = Comment.objects.get(pk=comment_id)
    except User.DoesNotExist:
        raise Http404("Comment does not exist")
    if request.method == 'POST':
        # Delete image method to sure delete image files.
        __delete_comment_plus_image_file(comment_id)
        return redirect('view_issue', category_id=category_id, issue_id=issue_id)
# todo: make use of delete form
    form_method = request.path
    return render(request, 'admin_delete_comment.html', {'comment': comment, 'form_method': form_method})


def delete_issue(request, category_id, issue_id):
    if not __check_user_is_authenticated_admin(request):
        return redirect('/login')
    try:
        issue = Issue.objects.get(pk=issue_id)
    except User.DoesNotExist:
        raise Http404("Issue does not exist")
    if request.method == 'POST':
        # Delete image method to sure delete image files.
        __delete_issue_plus_children_plus_image_files(issue)
        return redirect('view_category', category_id=category_id)
# todo: make use of delete form
    form_method = request.path
    return render(request, 'admin_delete_issue.html', {'issue': issue, 'form_method': form_method})


def create_example_rows(request):
    if request.method == 'POST':
        __set_session_vars(request, None, False)
        # delete all users
        User.objects.all().delete()

        # delete all other rows
        categories = Category.objects.all()
        for category in categories:
            issues = Issue.objects.filter(parent_category_id=category.id)
            for issue in issues:
                __delete_issue_plus_children_plus_image_files(issue)
            category.delete()

        # example admin user
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.password = hashers.make_password('Password1')
        admin_user.is_admin = True
        admin_user.datetime_created = datetime.now()
        admin_user.nickname = 'Administrator User'
        admin_user.save()

        # example regular user
        regular_user = User()
        regular_user.username = 'user'
        regular_user.password = hashers.make_password('Password1')
        regular_user.is_admin = False
        regular_user.datetime_created = datetime.now()
        regular_user.nickname = 'Regular User'
        regular_user.save()

        # example category 1
        category1 = Category()
        category1.name = 'Bug Reports'
        category1.author = admin_user
        category1.datetime_created = datetime.now()
        category1.save()

        # example issue 1
        issue1 = Issue()
        issue1.title = 'Cant login!!'
        issue1.description = 'I cant login to the application, it says my username or password is wrong.\r\nPlease help!'
        issue1.author = regular_user
        issue1.datetime_created = datetime.now()
        issue1.parent_category = category1
        issue1.save()

        # example comment 1
        comment1 = Comment()
        comment1.text = 'Try using the password "Password1" without the quotes.'
        comment1.author = regular_user
        comment1.datetime_created = datetime.now()
        comment1.parent_issue = issue1
        comment1.save()

        # example category 2
        category2 = Category()
        category2.name = 'Feature Requests'
        category2.author = admin_user
        category2.datetime_created = datetime.now()
        category2.save()

        # example issue 2
        issue2 = Issue()
        issue2.title = 'Phone number login'
        issue2.description = 'I would like to be able to login with a phone number instead of a username'
        issue2.author = regular_user
        issue2.datetime_created = datetime.now()
        issue2.parent_category = category2
        issue2.save()

        # example comment 2
        comment2 = Comment()
        comment2.text = 'This is a great idea, we will look into it. Thanks!\r\nhowever, we will not be able to implement it right now.'
        comment2.author = admin_user
        comment2.datetime_created = datetime.now()
        comment2.parent_issue = issue2
        comment2.save()

        # example comment 3
        comment3 = Comment()
        comment3.text = 'Thanks for the reply, I look forward to seeing this feature in the future.'
        comment3.author = regular_user
        comment3.datetime_created = datetime.now()
        comment3.parent_issue = issue2
        comment3.save()

        # example issue 3
        issue3 = Issue()
        issue3.title = 'Delete my account'
        issue3.description = 'I would like to have the ability to delete my account.\r\nIf this is not possible, please do it for me.'
        issue3.datetime_created = datetime.now()
        issue3.parent_category = category2
        issue3.save()

        # example comment 4
        comment4 = Comment()
        comment4.text = 'Unfortunately we cannot implement this at the moment. In the meantime I have deleted your account for you..'
        comment4.author = admin_user
        comment4.datetime_created = datetime.now()
        comment4.parent_issue = issue3
        comment4.save()

        return redirect('index')
    return render(request, 'create_example_rows.html')

# private methods


def __check_user_is_authenticated_admin(request):
    return __check_user_is_authenticated(request) and request.session['is_admin']


def __check_user_has_update_permission(request, author_id):
    return author_id == request.session['user_id'] or request.session['is_admin']


def __get_user_from_username(username):
    user = User.objects.get(username=username)
    return user


def __get_user_from_request_user_id(request):
    return User.objects.get(pk=request.session['user_id'])


def __validate_password_secure(password):
    try:
        validators.validate_password(
            password=password, password_validators=validators.get_password_validators(AUTH_PASSWORD_VALIDATORS))
        return None
    except BaseException as e:
        return '\r\n'.join(e.messages)


def __check_user_is_authenticated(request):
    if request.session.get('is_authenticated'):
        try:
            __get_user_from_request_user_id(request)
            return True
        except:
            pass

    return False


# Method to set session vars for user upon login.
# Use session vars, not cookie avoid storing sensitive
# data on client cookie where it is changeable.
def __set_session_vars(request, user, logging_in):
    if logging_in:
        request.session['is_authenticated'] = True
        request.session['user_id'] = user.id
        request.session['is_admin'] = user.is_admin
    else:
        del request.session['is_authenticated']
        del request.session['user_id']
        del request.session['is_admin']


def __delete_issue_plus_children_plus_image_files(issue):
    comments = Comment.objects.filter(parent_issue_id=issue.id)
    for comment in comments:
        __delete_comment_plus_image_file(comment.id)

    __delete_image(issue.image_filename)
    issue.delete()


def __delete_comment_plus_image_file(comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        raise Http404("Comment does not exist")

    __delete_image(comment.image_filename)
    comment.delete()


def __get_image_upload_path():
    return os.path.join(BASE_DIR, 'issuetracker\\static\\images\\')


def __check_for_image_errors(image):
    error = ''
    if image.size > 4194304:
        error += 'Image filesize too big, please upload an image smaller than 4MB. '
    return error


def __handle_image_upload(image):
    image.name = image.name.replace(' ', '_')
    # get next available filename
    image_upload_path = __get_image_upload_path()
    filepath = image_upload_path+image.name
    if os.path.isfile(filepath):
        # get next available filename and split it if necessary to get below 128 chars
        filename_only, file_extension_only = os.path.splitext(image.name)
        counter = str_counter_length = 1
        file_extension_length = len(file_extension_only)

        # algorithm to get next available filename as described above. basically just increment the counter until the filename is available
        while os.path.isfile(image_upload_path+filename_only[0:128-str_counter_length-file_extension_length]+str(counter)+file_extension_only):
            counter += 1
            str_counter_length = len(str(counter))

        image.name = filename_only[0:128-str_counter_length -
                                   file_extension_length]+str(counter)+file_extension_only
        filepath = image_upload_path+image.name

    with open(filepath, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)


def __delete_image(image_filename):
    image_upload_path = __get_image_upload_path()
    filepath = image_upload_path+image_filename
    if os.path.isfile(filepath):
        os.remove(filepath)
