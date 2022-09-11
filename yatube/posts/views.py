from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

POSTS_PER_PAGE = 10
CACHE_SECONDS_DELAY = 20


def get_page_objects(queryset, request):
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {'page_obj': page_obj}


@cache_page(CACHE_SECONDS_DELAY, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related('author')
    context = get_page_objects(posts, request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
    }
    context.update(get_page_objects(post_list, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author_id=author.id)
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_objects(post_list, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    group = post.group
    title_text = post.text[:30]
    author = post.author
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'title_text': title_text,
        'author': author,
        'group': group,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None,)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
        return render(request, 'posts/post_create.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/post_create.html',
                  {'form': form, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    context = get_page_objects(posts, request)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    follower = request.user
    fav_author = User.objects.get(username=username)
    if not Follow.objects.filter(user=follower, author=fav_author).exists():
        if follower.id != fav_author.id:
            Follow.objects.get_or_create(user=follower, author=fav_author)
            return redirect('posts:follow_index')
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = User.objects.get(username=username)
    Follow.objects.filter(user=follower,
                          author=following).delete()
    return profile(request, username)
