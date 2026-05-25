import threading

from django.db import close_old_connections
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.models import Profile
from cv_engine.models import GeneratedResume, GenerationTask
from cv_engine.services import generate_cv_data_llm

SECTION_LABELS = {
    'personal':   'Personal info',
    'skills':     'Skills',
    'education':  'Education',
    'experience': 'Experience',
    'projects':   'Projects',
}


def _run_generation(task_id: str, user, profile_id: int, offer: dict | None, profile_links: dict | None = None):
    close_old_connections()

    def on_progress(done: int, total: int, section_name: str):
        GenerationTask.objects.filter(task_id=task_id).update(
            progress=int(done / total * 100),
            current=SECTION_LABELS.get(section_name, section_name),
            done_sections=done,
            total_sections=total,
        )

    try:
        resume_json = generate_cv_data_llm.generate_cv_data_llm(
            profile_id, offer=offer, progress_callback=on_progress
        )

        if profile_links and isinstance(resume_json.get('personal'), dict):
            info = resume_json['personal'].setdefault('info', {})
            gh = (profile_links.get('github_url') or '').strip()
            li = (profile_links.get('linkedin_url') or '').strip()
            if gh:
                info['github_link'] = gh
                info['github_label'] = gh.replace('https://', '').replace('http://', '').rstrip('/')
            if li:
                info['linkedin_link'] = li
                info['linkedin_label'] = li.replace('https://', '').replace('http://', '').rstrip('/')

        doc = GeneratedResume.objects.create(user=user, generatedJson=resume_json)
        GenerationTask.objects.filter(task_id=task_id).update(
            status=GenerationTask.STATUS_DONE,
            progress=100,
            generated_resume=doc,
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        GenerationTask.objects.filter(task_id=task_id).update(
            status=GenerationTask.STATUS_ERROR,
            error_message=str(exc),
        )
    finally:
        close_old_connections()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_and_fill_cv_to_model(request, profile_id):
    """
    Starts async CV generation. Returns task_id immediately.
    Optionally accepts offer data and profile_links in request body.
    """
    get_object_or_404(Profile, id=profile_id, user=request.user)

    offer = request.data.get('offer') or None
    profile_links = request.data.get('profile_links') or None

    task = GenerationTask.objects.create(user=request.user)
    task_id = str(task.task_id)

    thread = threading.Thread(
        target=_run_generation,
        args=(task_id, request.user, profile_id, offer, profile_links),
        daemon=True,
    )
    thread.start()

    return Response({'task_id': task_id}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generation_status(request, task_id):
    """
    Returns current progress of a CV generation task.
    status: 'running' | 'done' | 'error'
    """
    try:
        task = GenerationTask.objects.get(task_id=task_id, user=request.user)
    except GenerationTask.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

    data = {
        'status': task.status,
        'progress': task.progress,
        'current': task.current,
        'done_sections': task.done_sections,
        'total_sections': task.total_sections,
    }
    if task.status == GenerationTask.STATUS_DONE:
        data['generatedResume_id'] = task.generated_resume_id
        # Include resume JSON for populateSections()
        if task.generated_resume:
            data['resume'] = task.generated_resume.generatedJson
    if task.status == GenerationTask.STATUS_ERROR:
        data['error'] = task.error_message

    return Response(data, status=status.HTTP_200_OK)
