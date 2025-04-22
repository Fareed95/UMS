from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Courses, Proffesor_Profile, Student_Profile, User
from .forms import ProffessorProfileForm, StudentProfileForm


def home(request):
    """Home page view showing available courses."""
    courses = Courses.objects.all()
    context = {'courses': courses}
    return render(request, 'home.html', context)


def about(request):
    """About page view."""
    return render(request, 'about.html')


def courses(request):
    """Courses listing page view."""
    courses = Courses.objects.all()
    context = {'courses': courses}
    return render(request, 'courses.html', context)


def login_user(request):
    """User login view handling both professors and students."""
    if request.user.is_authenticated:
        return redirect('page_of_teacher' if request.user.is_proffesor else 'page_of_student')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'student')  # Default to student

        if not email or not password:
            messages.error(request, 'Please provide both email and password')
            return render(request, 'login.html')

        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Check if user type matches
            if (user_type == 'professor' and not user.is_proffesor) or \
               (user_type == 'student' and user.is_proffesor):
                messages.error(request, 'Invalid login type for this account')
                return render(request, 'login.html')
                
            login(request, user)
            return redirect('page_of_teacher' if user.is_proffesor else 'page_of_student')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'login.html')


@login_required
def page_of_teacher(request):
    """Professor dashboard view."""
    if not request.user.is_proffesor:
        raise Http404("Page not found")
    
    try:
        profile = Proffesor_Profile.objects.get(user=request.user)
    except Proffesor_Profile.DoesNotExist:
        profile = None
        messages.info(request, "Please complete your profile information")

    context = {
        'profile': profile,
        'user': request.user,
        'email': request.user.email,
        'teacher': True,
    }
    return render(request, 'teacher_display/home.html', context)


@login_required
def page_of_student(request):
    """Student dashboard view."""
    if request.user.is_proffesor:
        raise Http404("Page not found")
    
    try:
        profile = Student_Profile.objects.get(user=request.user)
    except Student_Profile.DoesNotExist:
        profile = None
        messages.info(request, "Please complete your profile information")

    context = {
        'profile': profile,
        'user': request.user,
        'email': request.user.email,
        'teacher': False,
    }
    return render(request, 'student_display/home.html', context)


@login_required
def profile_view(request):
    """Profile viewing page for both professors and students."""
    if request.user.is_proffesor:
        profile = get_object_or_404(Proffesor_Profile, user=request.user)
        template = 'teacher_display/profile.html'
    else:
        profile = get_object_or_404(Student_Profile, user=request.user)
        template = 'student_display/profile.html'

    context = {
        'profile': profile,
        'editable': False,
        'project_color': 'rgb(185, 156, 118)',
    }
    return render(request, template, context)


@login_required
def profile_edit(request):
    """Profile editing page for both professors and students."""
    if request.user.is_proffesor:
        profile = get_object_or_404(Proffesor_Profile, user=request.user)
        form_class = ProffessorProfileForm
        template = 'teacher_display/profile.html'
    else:
        profile = get_object_or_404(Student_Profile, user=request.user)
        form_class = StudentProfileForm
        template = 'student_display/profile.html'

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
    else:
        form = form_class(instance=profile)

    context = {
        'form': form,
        'editable': True,
        'project_color': 'rgb(185, 156, 118)',
    }
    return render(request, template, context)


@login_required
def batch(request):
    """Batch/professor listing view depending on user type."""
    user = request.user
    
    if user.is_proffesor:
        professor_profile = get_object_or_404(Proffesor_Profile, user=user)
        students = Student_Profile.objects.filter(
            course=professor_profile.course,
            branch=professor_profile.branch,
            subjects__name=professor_profile.subject
        ).distinct()

        context = {
            'professor_profile': professor_profile,
            'students': students
        }
        return render(request, 'teacher_display/my_batch.html', context)
    else:
        student_profile = get_object_or_404(Student_Profile, user=user)
        professors = Proffesor_Profile.objects.filter(
            course=student_profile.course,
            branch=student_profile.branch
        )

        context = {
            'student_profile': student_profile,
            'professors': professors,
        }
        return render(request, 'student_display/my_proffesors.html', context)


def LogoutPage(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')