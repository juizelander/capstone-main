from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Program

def create_program(request):
    if request.method == 'POST':
        program_name = request.POST.get('program_name')
        requirements = request.POST.get('requirements')

        if program_name:  # simple validation
            Program.objects.create(
                program_name=program_name,
                requirements=requirements
            )
            return JsonResponse({'success': True, 'message': 'Program created successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Program name is required'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def get_programs(request):
    programs = Program.objects.all().order_by('-program_id')
    data = [
        {
            'program_id': p.program_id,
            'program_name': p.program_name,
            'requirements': p.requirements or ''
        }
        for p in programs
    ]
    return JsonResponse({'programs': data})
