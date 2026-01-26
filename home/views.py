from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Program

def create_program(request):
    if request.method == 'POST':
        try:
            program_name = request.POST.get('program_name')
            requirements = request.POST.get('requirements')
            application_start_date = request.POST.get('application_start_date') or None
            application_end_date = request.POST.get('application_end_date') or None
            program_image = request.FILES.get('program_image')
            program_type = request.POST.get('program_type')
            
            print(f"Creating program: Name={program_name}, Type={program_type}") # Debug log

            if program_name:  # simple validation
                Program.objects.create(
                    program_name=program_name,
                    requirements=requirements,
                    application_start_date=application_start_date,
                    application_end_date=application_end_date,
                    program_image=program_image,
                    program_type=program_type
                )
                return JsonResponse({'success': True, 'message': 'Program created successfully'})
            else:
                return JsonResponse({'success': False, 'error': 'Program name is required'})
        except Exception as e:
            print(f"Error creating program: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_programs(request):
    programs = Program.objects.all().order_by('-program_id')
    data = [
        {
            'program_id': p.program_id,
            'program_name': p.program_name,
            'requirements': p.requirements or '',
            'application_start_date': p.application_start_date,
            'application_end_date': p.application_end_date,
            'program_image': p.program_image.url if p.program_image else None,
            'program_type': p.program_type
        }
        for p in programs
    ]
    return JsonResponse({'programs': data})
