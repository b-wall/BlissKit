from django.forms import ModelForm, TextInput
from .models import Post


# Form for users to post comments

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {'content': TextInput(
            attrs={'class': 'form-control biscuit-form',
                   'placeholder': 'Biscuit-related thoughts?',
                   'autocomplete': 'off'})}
        labels = {
            'content': ''
        }
