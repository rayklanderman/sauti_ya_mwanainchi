from django import forms
from django.core.validators import MinLengthValidator
from .models import Comment, Vote, ContactMessage

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        validators=[MinLengthValidator(10, message="Comment must be at least 10 characters long")],
        widget=forms.Textarea(attrs={
            'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
            'rows': 4,
            'placeholder': 'Share your thoughts on this bill...',
            'data-comment-input': 'true'
        }),
        help_text='Minimum 10 characters'
    )

    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            # Remove excessive whitespace
            content = ' '.join(content.split())
            # Ensure first character is uppercase
            content = content[0].upper() + content[1:] if content else content
        return content

class VoteForm(forms.ModelForm):
    choice = forms.ChoiceField(
        choices=Vote.VOTE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio h-4 w-4 text-kenya-red focus:ring-kenya-red border-gray-300'
        }),
        help_text='Your stance on this bill'
    )

    class Meta:
        model = Vote
        fields = ['choice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choice'].label_suffix = ''
        self.fields['choice'].error_messages = {
            'required': 'Please select your stance on this bill'
        }

class ContactForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Your Name',
            'data-contact-input': 'true'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Your Email',
            'data-contact-input': 'true'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Subject',
            'data-contact-input': 'true'
        })
    )
    
    message = forms.CharField(
        validators=[MinLengthValidator(20, message="Message must be at least 20 characters long")],
        widget=forms.Textarea(attrs={
            'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Your Message',
            'rows': 5,
            'data-contact-input': 'true'
        }),
        help_text='Minimum 20 characters'
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].error_messages = {
                'required': f'Please enter your {field}',
                'invalid': f'Please enter a valid {field}'
            }

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message:
            # Remove excessive whitespace
            message = ' '.join(message.split())
            # Ensure first character is uppercase
            message = message[0].upper() + message[1:] if message else message
        return message

class BillFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('engagement', 'Most Engaged'),
        ('title', 'Title A-Z'),
        ('-title', 'Title Z-A'),
    ]

    STATUS_CHOICES = [
        ('all', 'All Status'),
        ('draft', 'Draft'),
        ('public', 'Public'),
        ('closed', 'Closed'),
    ]

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Search bills...',
            'data-search-input': 'true'
        })
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-kenya-red focus:border-kenya-red sm:text-sm rounded-md',
            'data-filter-select': 'true'
        })
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-kenya-red focus:border-kenya-red sm:text-sm rounded-md',
            'data-sort-select': 'true'
        })
    )
