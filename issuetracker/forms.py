from django import forms


# base forms
class __ImageForm(forms.Form):
    image = forms.ImageField(label='Image', max_length=128, required=False)


class __TextForm(forms.Form):
    text = forms.CharField(label='Description', max_length=512, required=True)


class __TitleForm(forms.Form):
    title = forms.CharField(label='Title', max_length=128, required=True)


# actual forms
class LoginForm(forms.Form):
    username = forms.CharField(max_length=128, required=True)
    password = forms.CharField(
        max_length=128, widget=forms.PasswordInput, required=True)


class ChangeNicknameForm(forms.Form):
    nickname = forms.CharField(max_length=256, required=True)


class RegisterForm(LoginForm, ChangeNicknameForm):
    # inherit from LoginForm and ChangeNicknameForm to get nickname and username and password fields
    confirm_password = forms.CharField(
        max_length=128, widget=forms.PasswordInput, required=True)
    is_admin = forms.BooleanField(required=False)


class AdminEditUserForm(forms.Form):
    username = forms.CharField(max_length=128, required=False)
    nickname = forms.CharField(max_length=256, required=False)
    password = forms.CharField(max_length=128, required=False)
    is_admin = forms.BooleanField(required=False)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        max_length=128, widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(
        max_length=128, widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(
        max_length=128, widget=forms.PasswordInput, required=True)


class SetUserImageForm(__ImageForm):
    pass


class CreateCategoryForm(__TitleForm):
    pass


class CreateIssueForm(__TitleForm,  __ImageForm, __TextForm):
    pass


class CreateCommentForm(__TextForm, __ImageForm):
    pass


class UpdateCategoryForm(__TitleForm):
    pass


class UpdateIssueForm(__ImageForm):
    text = forms.CharField(label='Description', max_length=512, required=False)
    title = forms.CharField(label='Title', max_length=128, required=False)


class UpdateCommentForm(__ImageForm):
    text = forms.CharField(label='Description', max_length=512, required=False)
