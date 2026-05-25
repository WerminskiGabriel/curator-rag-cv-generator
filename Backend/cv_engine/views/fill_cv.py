import threading
import uuid

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.models import Profile
from cv_engine.models import GeneratedResume
from cv_engine.services import generate_cv_data_llm

# In-memory task store: task_id -> dict
_tasks: dict = {}
_tasks_lock = threading.Lock()

SECTION_LABELS = {
    'personal':   'Personal info',
    'skills':     'Skills',
    'education':  'Education',
    'experience': 'Experience',
    'projects':   'Projects',
}


def _run_generation(task_id: str, user, profile_id: int, offer: dict | None, profile_links: dict | None = None):
    def on_progress(done: int, total: int, section_name: str):
        with _tasks_lock:
            _tasks[task_id].update({
                'progress': int(done / total * 100),
                'current': SECTION_LABELS.get(section_name, section_name),
                'done_sections': done,
                'total_sections': total,
            })

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
        with _tasks_lock:
            _tasks[task_id].update({
                'status': 'done',
                'progress': 100,
                'generatedResume_id': doc.id,
                'resume': resume_json,
            })
    except Exception as exc:
        import traceback
        traceback.print_exc()
        with _tasks_lock:
            _tasks[task_id].update({'status': 'error', 'error': str(exc)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_and_fill_cv_to_model(request, profile_id):
    """
    Starts async CV generation. Returns task_id immediately.
    Optionally accepts offer data in request body to generate a tailored CV.
    """
    get_object_or_404(Profile, id=profile_id, user=request.user)

    offer = request.data.get('offer') or None
    profile_links = request.data.get('profile_links') or None

    task_id = str(uuid.uuid4())
    with _tasks_lock:
        _tasks[task_id] = {
            'status': 'running',
            'progress': 0,
            'current': 'Starting…',
            'done_sections': 0,
            'total_sections': 5,
        }

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
    with _tasks_lock:
        task = _tasks.get(task_id)

    if not task:
        return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(task, status=status.HTTP_200_OK)
