from django.shortcuts import render
from job.serializers import JobSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import Job
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.db.models import Avg, Min, Max, Count
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .filters import JobsFilter

# Create your views here.

def go(request):
  return HttpResponse('go now hey--')

@api_view(['GET'])
def get_all_jobs(request):

  try:
    filterset = JobsFilter(request.GET, queryset=Job.objects.all().order_by('id'))
    count = filterset.qs.count()

    res_per_page = 3
    paginator = PageNumberPagination()
    paginator.page_size = res_per_page
    print('====')

    queryset = paginator.paginate_queryset(filterset.qs, request)
    serializer = JobSerializer(queryset, many=True)
    return Response({"jobs": serializer.data, "results_per_page": res_per_page, "count": count})
  except Exception as e:
    print(e)

@api_view(['GET'])
def get_job(request, pk):
  job = get_object_or_404(Job, id=pk)

  serializer = JobSerializer(job, many=False)
  return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_job(request):
  request.data['user'] = request.user
  data = request.data

  job = Job.objects.create(**data)

  serializer = JobSerializer(job, many=False)
  return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_job(request, pk):
  job = get_object_or_404(Job, id=pk)

  if job.user != request.user:
    return Response({'message': 'You can not update this job'}, status=status.HTTP_403_FORBIDDEN)

  for i in [n.name for n in Job._meta.fields if n.name not in ['id']]:
    if request.data.get(i):
      setattr(job, i, request.data[i])
  job.save()


  serializer = JobSerializer(job, many=False)
  return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job(request, pk):
  job = get_object_or_404(Job, id=pk)

  if job.user != request.user:
    return Response({'message': 'You can not update this job'}, status=status.HTTP_403_FORBIDDEN)

  job.delete()

  return Response({'detail': 'success', 'message': 'Job Deleted'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_topic_stats(request, topic):
  args = {'title__icontains': topic}
  jobs = Job.objects.filter(**args)

  if jobs.count() == 0:
    return Response({'detail': 'failure', 'message': 'No results found'})
  
  stats = jobs.aggregate(
    total_jobs = Count('title'),
    avg_positions = Avg('positions'),
    avg_salary = Avg('salary'),
    min_salary = Min('salary'),
    max_salary = Max('salary'),
  )
  return Response(stats)
