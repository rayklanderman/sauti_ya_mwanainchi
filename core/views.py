from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from .models import County, Bill, Comment, UserProfile, Notification
from .forms import CommentForm, BillForm, UserProfileForm

class HomeView(ListView):
    model = Bill
    template_name = 'core/home.html'
    context_object_name = 'bills'
    paginate_by = 10

    def get_queryset(self):
        queryset = Bill.objects.filter(
            status='public_participation'
        ).select_related('county').order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['counties'] = County.objects.annotate(
            active_bills=Count('bills', filter=Q(bills__status='public_participation'))
        )
        return context

class CountyDetailView(DetailView):
    model = County
    template_name = 'core/county_detail.html'
    context_object_name = 'county'
    slug_field = 'code'
    slug_url_kwarg = 'code'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_bills'] = self.object.bills.filter(
            status='public_participation'
        ).order_by('-created_at')
        return context

class BillDetailView(DetailView):
    model = Bill
    template_name = 'core/bill_detail.html'
    context_object_name = 'bill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(
            is_approved=True
        ).select_related('user').order_by('-created_at')
        context['comment_form'] = CommentForm()
        return context

@login_required
def add_comment(request, slug):
    bill = get_object_or_404(Bill, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.bill = bill
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been submitted for review.')
            
            # Create notification for county admin
            if bill.county.residents.filter(is_county_admin=True).exists():
                for admin in bill.county.residents.filter(is_county_admin=True):
                    Notification.objects.create(
                        user=admin.user,
                        notification_type='comment',
                        title=f'New comment on {bill.title}',
                        message=f'{request.user.username} commented on {bill.title}',
                        related_bill=bill
                    )
            
            return redirect('bill_detail', slug=slug)
    return redirect('bill_detail', slug=slug)

@login_required
def reply_to_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.bill = parent_comment.bill
            reply.user = request.user
            reply.parent = parent_comment
            reply.save()
            
            # Notify the parent comment author
            Notification.objects.create(
                user=parent_comment.user,
                notification_type='reply',
                title=f'Reply to your comment',
                message=f'{request.user.username} replied to your comment on {parent_comment.bill.title}',
                related_bill=parent_comment.bill
            )
            
            messages.success(request, 'Your reply has been submitted for review.')
    return redirect('bill_detail', slug=parent_comment.bill.slug)

class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'core/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(UserProfile, user__username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            user=self.object.user
        ).select_related('bill').order_by('-created_at')
        return context

@login_required
def edit_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'core/edit_profile.html', {'form': form})

@login_required
def notifications(request):
    notifications = request.user.notifications.order_by('-created_at')[:20]
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    return render(request, 'core/notifications.html', {
        'notifications': notifications
    })

class BillCreateView(LoginRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = 'core/bill_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Bill has been created successfully.')
        return response

class BillUpdateView(LoginRequiredMixin, UpdateView):
    model = Bill
    form_class = BillForm
    template_name = 'core/bill_form.html'

    def get_success_url(self):
        return reverse_lazy('bill_detail', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Bill has been updated successfully.')
        return response

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['bills'] = Bill.objects.filter(author=user)
        context['comments'] = Comment.objects.filter(author=user)
        return context
