from django import forms
from django.core.validators import MinLengthValidator
from .models import Comment, Bill, UserProfile
from django.utils import timezone

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

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['title', 'description', 'county', 'document', 'public_participation_deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Bill Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
                'rows': 6,
                'placeholder': 'Bill Description'
            }),
            'county': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md'
            }),
            'document': forms.FileInput(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md'
            }),
            'public_participation_deadline': forms.DateTimeInput(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
                'type': 'datetime-local'
            })
        }

    def clean_public_participation_deadline(self):
        deadline = self.cleaned_data.get('public_participation_deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past")
        return deadline

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'county', 'phone_number', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'county': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md',
                'placeholder': '+254...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'shadow-sm focus:ring-kenya-red focus:border-kenya-red block w-full sm:text-sm border-gray-300 rounded-md'
            })
        }

class BillFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('title', 'Title A-Z'),
        ('-title', 'Title Z-A'),
    ]
    
    STATUS_CHOICES = [
        ('all', 'All Status'),
        ('draft', 'Draft'),
        ('public_participation', 'Public Participation'),
        ('review', 'Under Review'),
        ('passed', 'Passed'),
        ('rejected', 'Rejected'),
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
