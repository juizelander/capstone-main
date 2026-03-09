from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Program

def create_program(request):
    if request.method == 'POST':
        try:
            program_name = request.POST.get('program_name')
            requirements = request.POST.get('requirements')
            # Handle document_requirements as comma-separated string
            doc_req_raw = request.POST.get('document_requirements', '')
            document_requirements = [d.strip() for d in doc_req_raw.split(',')] if doc_req_raw else []
            
            application_start_date = request.POST.get('application_start_date') or None
            application_end_date = request.POST.get('application_end_date') or None
            program_image = request.FILES.get('program_image')
            program_type = request.POST.get('program_type')
            target_student_types = request.POST.getlist('target_student_types')
            max_slots = request.POST.get('max_slots', 0)
            
            print(f"Creating program: Name={program_name}, Type={program_type}, Targets={target_student_types}, Slots={max_slots}") # Debug log

            if program_name:  # simple validation
                Program.objects.create(
                    program_name=program_name,
                    requirements=requirements,
                    document_requirements=document_requirements,
                    application_start_date=application_start_date,
                    application_end_date=application_end_date,
                    program_image=program_image,
                    program_type=program_type,
                    target_student_types=target_student_types,
                    max_slots=int(max_slots) if max_slots else 0
                )
                return JsonResponse({'success': True, 'message': 'Program created successfully'})
            else:
                return JsonResponse({'success': False, 'error': 'Program name is required'})
        except Exception as e:
            print(f"Error creating program: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_programs(request):
    from .models import Application
    programs = Program.objects.all().order_by('-program_id')
    student_id = request.session.get('user_id')
    
    data = []
    for p in programs:
        item = {
            'program_id': p.program_id,
            'program_name': p.program_name,
            'requirements': p.requirements or '',
            'document_requirements': p.document_requirements or [],
            'application_start_date': p.application_start_date,
            'application_end_date': p.application_end_date,
            'program_image': p.program_image.url if p.program_image else None,
            'program_type': p.program_type,
            'target_student_types': p.target_student_types or [],
            'max_slots': p.max_slots,
            'current_apps': Application.objects.filter(program=p, requirement_status='approved').count(),
            'user_app_status': None
        }
        
        if student_id:
            # Check for existing application for this student
            user_app = Application.objects.filter(student_id=student_id, program=p).first()
            if user_app:
                item['user_app_status'] = user_app.requirement_status
        
        data.append(item)
        
    return JsonResponse({'programs': data})


def edit_program(request, program_id):
    if request.method == 'POST':
        try:
            program = Program.objects.get(program_id=program_id)
            
            program.program_name = request.POST.get('program_name', program.program_name)
            program.requirements = request.POST.get('requirements', program.requirements)
            program.program_type = request.POST.get('program_type', program.program_type)
            program.max_slots = int(request.POST.get('max_slots', program.max_slots))
            
            if 'document_requirements' in request.POST:
                doc_req_raw = request.POST.get('document_requirements', '')
                program.document_requirements = [d.strip() for d in doc_req_raw.split(',')] if doc_req_raw else []
            
            if 'target_student_types' in request.POST:
                program.target_student_types = request.POST.getlist('target_student_types')
            
            start_date = request.POST.get('application_start_date')
            if start_date: 
                program.application_start_date = start_date
            
            end_date = request.POST.get('application_end_date')
            if end_date:
                program.application_end_date = end_date
                
            if 'program_image' in request.FILES:
                program.program_image = request.FILES['program_image']
                
            program.save()
            
            return JsonResponse({'success': True, 'message': 'Program updated successfully'})
        except Program.DoesNotExist:
             return JsonResponse({'success': False, 'error': 'Program not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def delete_program(request, program_id):
    if request.method == 'POST':
        try:
            program = Program.objects.get(program_id=program_id)
            program.delete()
            return JsonResponse({'success': True, 'message': 'Program deleted successfully'})
        except Program.DoesNotExist:
             return JsonResponse({'success': False, 'error': 'Program not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
