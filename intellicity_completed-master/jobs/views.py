from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JobPosting, JobApplication, Skill
from .forms import JobPostingForm, JobApplicationForm, JobApplicationStatusForm
from notifications.models import Notification
from users.models import Profile

@login_required
def user_job_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user)
    return render(request, 'jobs/job_application_list.html', {'applications': applications})

@login_required
def job_posting_list(request):
    if request.user.is_staff and hasattr(request.user, 'organization'):
        job_postings = JobPosting.objects.filter(organization=request.user.organization)
    else:
        job_postings = JobPosting.objects.none()
    return render(request, 'jobs/job_posting_list.html', {'job_postings': job_postings})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import JobPosting, Skill
from .forms import JobPostingForm
from notifications.models import Notification
from users.models import Profile

@login_required
def job_posting_create(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST, request.FILES)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.organization = request.user.organization  # Set the organization to the logged-in user's organization
            job_posting.save()
            form.save_m2m()  # Save the many-to-many field

            # Handle new skills
            new_skills = form.cleaned_data['new_skills']
            if new_skills:
                new_skills_list = [skill.strip() for skill in new_skills.split(',')]
                for skill_name in new_skills_list:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    job_posting.required_skills.add(skill)

            # Create notifications for users with matching skills
            required_skills_ids = list(job_posting.required_skills.values_list('id', flat=True))
            users = Profile.objects.filter(skills__id__in=required_skills_ids).distinct()
            for profile in users:
                matching_skills = profile.skills.filter(id__in=required_skills_ids)
                skill_names = ", ".join([skill.name for skill in matching_skills])
                Notification.objects.create(
                    user=profile.user,
                    message=f"A new job posting matches your skills: {job_posting.title}. Matching skills: {skill_names}."
                )

            return redirect('organization_dashboard')
    else:
        form = JobPostingForm()
    return render(request, 'jobs/job_posting_create.html', {'form': form})


@login_required
def job_posting_update(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, request.FILES, instance=job_posting)
        if form.is_valid():
            job_posting = form.save()

            # Handle new skills
            new_skills = form.cleaned_data['new_skills']
            if new_skills:
                new_skills_list = [skill.strip() for skill in new_skills.split(',')]
                for skill_name in new_skills_list:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    job_posting.required_skills.add(skill)

            return redirect('organization_dashboard')
    else:
        form = JobPostingForm(instance=job_posting)
    return render(request, 'jobs/job_posting_update.html', {'form': form})



@login_required
def job_posting_delete(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        job_posting.delete()
        return redirect('organization_dashboard')
    return render(request, 'jobs/job_posting_delete.html', {'job_posting': job_posting})

@login_required
def job_application_create(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job_application = form.save(commit=False)
            job_application.job = job_posting
            job_application.applicant = request.user
            job_application.cv = request.FILES['cv']  # Save the uploaded CV
            job_application.save()

            # Create a notification for the organization
            Notification.objects.create(
                user=job_posting.organization.user,
                message=f"{request.user.username} has applied for {job_posting.title}"
            )

            return redirect('job_application_success')
    else:
        form = JobApplicationForm()
    return render(request, 'jobs/job_application_create.html', {'form': form, 'job_posting': job_posting})

def job_application_success(request):
    return render(request, 'jobs/job_application_success.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import JobPosting, JobApplication
from .forms import JobApplicationStatusForm
from notifications.models import Notification

@login_required
def job_posting_detail(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    applications = JobApplication.objects.filter(job=job_posting)
    if request.user.is_staff and request.user.organization == job_posting.organization:
        if request.method == 'POST':
            form = JobApplicationStatusForm(request.POST)
            if form.is_valid():
                application = get_object_or_404(JobApplication, pk=request.POST.get('application_id'))
                application.status = form.cleaned_data['status']
                application.save()

                # Create a notification for the user
                Notification.objects.create(
                    user=application.applicant,
                    message=f"Your application status for {application.job.title} has been updated to {application.status}."
                )

                return redirect('job_posting_detail', pk=pk)
        else:
            form = JobApplicationStatusForm()
        return render(request, 'jobs/job_posting_detail.html', {'job_posting': job_posting, 'applications': applications, 'form': form})
    else:
        return render(request, 'jobs/job_posting_detail.html', {'job_posting': job_posting, 'applications': applications})
