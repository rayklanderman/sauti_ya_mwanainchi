from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.cache import cache
from .models import County, Bill, Comment, Vote, ContactMessage
from .forms import CommentForm, VoteForm, ContactForm
import json

def home(request):
    # Cache the counties and recent bills for better performance
    counties = cache.get('home_counties')
    if not counties:
        counties = County.objects.annotate(
            bill_count=Count('bill', filter=Q(bill__status='public')),
            participation_count=Count('bill__comments') + Count('bill__votes')
        ).order_by('-participation_count')
        cache.set('home_counties', counties, 3600)  # Cache for 1 hour

    recent_bills = cache.get('home_recent_bills')
    if not recent_bills:
        recent_bills = Bill.objects.filter(status='public')\
            .select_related('county')\
            .annotate(
                comment_count=Count('comments'),
                vote_count=Count('votes')
            ).order_by('-created_at')[:5]
        cache.set('home_recent_bills', recent_bills, 1800)  # Cache for 30 minutes

    trending_bills = Bill.objects.filter(
        status='public',
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).annotate(
        engagement=Count('comments') + Count('votes')
    ).order_by('-engagement')[:3]

    context = {
        'counties': counties,
        'recent_bills': recent_bills,
        'trending_bills': trending_bills,
    }
    return render(request, 'core/home.html', context)

def county_detail(request, county_id):
    county = get_object_or_404(County, id=county_id)
    
    # Get filter parameters
    status = request.GET.get('status', 'public')
    sort = request.GET.get('sort', '-created_at')
    search = request.GET.get('search', '')

    # Build query
    bills = Bill.objects.filter(county=county)
    if status != 'all':
        bills = bills.filter(status=status)
    if search:
        bills = bills.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # Apply sorting
    if sort == 'engagement':
        bills = bills.annotate(
            engagement=Count('comments') + Count('votes')
        ).order_by('-engagement')
    else:
        bills = bills.order_by(sort)

    # Add annotations for better display
    bills = bills.annotate(
        comment_count=Count('comments'),
        vote_count=Count('votes')
    )

    # Pagination
    paginator = Paginator(bills, 12)  # Show 12 bills per page
    page = request.GET.get('page')
    bills = paginator.get_page(page)

    context = {
        'county': county,
        'bills': bills,
        'current_status': status,
        'current_sort': sort,
        'search_query': search,
    }
    return render(request, 'core/county_detail.html', context)

def bill_detail(request, county_id, bill_slug):
    bill = get_object_or_404(
        Bill.objects.select_related('county').annotate(
            comment_count=Count('comments'),
            vote_count=Count('votes'),
            support_count=Count('votes', filter=Q(votes__choice='support')),
            oppose_count=Count('votes', filter=Q(votes__choice='oppose')),
            neutral_count=Count('votes', filter=Q(votes__choice='neutral'))
        ),
        county__id=county_id,
        slug=bill_slug
    )

    # Get comments with user info
    comments = bill.comments.select_related('user').order_by('-created_at')
    
    # Get user's vote if authenticated
    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(bill=bill, user=request.user).first()

    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'vote':
                choice = data.get('choice')
                if choice in dict(Vote.VOTE_CHOICES):
                    vote, created = Vote.objects.update_or_create(
                        bill=bill,
                        user=request.user,
                        defaults={'choice': choice}
                    )
                    return JsonResponse({'status': 'success'})
            
            elif action == 'comment':
                content = data.get('content')
                if content:
                    comment = Comment.objects.create(
                        bill=bill,
                        user=request.user,
                        content=content
                    )
                    return JsonResponse({
                        'status': 'success',
                        'comment': {
                            'user': comment.user.username,
                            'content': comment.content,
                            'created_at': comment.created_at.strftime('%B %d, %Y')
                        }
                    })
            
            return JsonResponse({'error': 'Invalid action'}, status=400)

    # Regular form handling
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to participate.')
            return redirect('account_login')
        
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.bill = bill
                comment.user = request.user
                comment.save()
                messages.success(request, 'Your comment has been posted.')
                return redirect('bill_detail', county_id=county_id, bill_slug=bill_slug)
        
        if 'vote' in request.POST:
            vote_form = VoteForm(request.POST)
            if vote_form.is_valid():
                vote, created = Vote.objects.update_or_create(
                    bill=bill,
                    user=request.user,
                    defaults={'choice': vote_form.cleaned_data['choice']}
                )
                messages.success(request, 'Your vote has been recorded.')
                return redirect('bill_detail', county_id=county_id, bill_slug=bill_slug)
    
    else:
        comment_form = CommentForm()
        vote_form = VoteForm(initial={'choice': user_vote.choice if user_vote else None})
    
    context = {
        'bill': bill,
        'comments': comments,
        'comment_form': comment_form,
        'vote_form': vote_form,
        'user_vote': user_vote,
    }
    return render(request, 'core/bill_detail.html', context)

@login_required
def user_dashboard(request):
    # Get user's recent activity
    recent_activities = []
    
    # Get comments
    comments = Comment.objects.filter(user=request.user)\
        .select_related('bill', 'bill__county')\
        .order_by('-created_at')[:5]
    for comment in comments:
        recent_activities.append({
            'type': 'comment',
            'description': 'Commented on',
            'target': comment.bill.title,
            'url': f'/counties/{comment.bill.county.id}/bills/{comment.bill.slug}/',
            'created_at': comment.created_at
        })

    # Get votes
    votes = Vote.objects.filter(user=request.user)\
        .select_related('bill', 'bill__county')\
        .order_by('-created_at')[:5]
    for vote in votes:
        recent_activities.append({
            'type': 'vote',
            'description': f'Voted {vote.choice} on',
            'target': vote.bill.title,
            'url': f'/counties/{vote.bill.county.id}/bills/{vote.bill.slug}/',
            'created_at': vote.created_at
        })

    # Sort activities by date
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)

    # Get followed counties
    followed_counties = County.objects.filter(
        bill__in=Bill.objects.filter(
            Q(comments__user=request.user) |
            Q(votes__user=request.user)
        )
    ).distinct()

    # Get participation stats
    stats = {
        'total_comments': Comment.objects.filter(user=request.user).count(),
        'total_votes': Vote.objects.filter(user=request.user).count(),
        'counties_engaged': followed_counties.count(),
        'recent_bills': Bill.objects.filter(
            Q(comments__user=request.user) |
            Q(votes__user=request.user)
        ).distinct().order_by('-created_at')[:5]
    }

    context = {
        'recent_activities': recent_activities,
        'followed_counties': followed_counties,
        'stats': stats,
    }
    return render(request, 'core/user_dashboard.html', context)

@require_POST
def contact_submit(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    # Handle regular POST request
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('home')
    
    messages.error(request, 'Please correct the errors below.')
    return redirect('contact')
