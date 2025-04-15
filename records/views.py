from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, F
from .models import StudentProfile, AcademicRecord, StudentClassHistory
from django.contrib import messages
from datetime import datetime


def student_profiles(request):
    query = request.GET.get('q', '')
    selected_year = request.GET.get('year', '')
    
    students = StudentProfile.objects.prefetch_related('class_history').all()
    
    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    if selected_year:
        try:
            selected_year_int = int(selected_year)
            students = students.filter(
                class_history__academic_year=selected_year_int
            ).distinct()
        except (ValueError, TypeError):
            # Handle invalid year input
            pass

    year_choices = StudentClassHistory.objects.values_list(
        'academic_year', flat=True
    ).distinct().order_by('academic_year')
    
    return render(request, 'records/student_profiles.html', {
        'students': students,
        'year_choices': year_choices,
        'selected_year': selected_year
    })

def academic_results(request):
    # Get distinct values for filters
    year_choices = [
        (year, f"{year}-{year+1}") 
        for year in AcademicRecord.objects.order_by('academic_year')
            .values_list('academic_year', flat=True)
            .distinct()
    ]
    
    class_choices = StudentClassHistory.objects.values_list(
        'form_class', flat=True
    ).distinct().order_by('form_class')
    
    # Base query with prefetch
    results = AcademicRecord.objects.select_related(
        'student'
    ).prefetch_related(
        'student__class_history'
    ).order_by('student__student_id', 'academic_year', 'semester')
    
    # Filtering logic
    year = request.GET.get('year')
    form_class = request.GET.get('form_class')
    student_name = request.GET.get('student_name')
    
    if year:
        results = results.filter(academic_year=int(year))
    if form_class:
        results = results.filter(
            student__class_history__form_class=form_class,
            student__class_history__academic_year=F('academic_year')
        ).distinct()
    if student_name:
        results = results.filter(
            Q(student__first_name__icontains=student_name) |
            Q(student__last_name__icontains=student_name)
        )
    
    return render(request, 'records/academic_results.html', {
        'results': results,
        'year_choices': year_choices,
        'class_choices': class_choices,
        'subjects': ['Chinese', 'English', 'Mathematics', 'Science', 'conduct']
    })

def student_report(request, student_id):
    try:
        student = StudentProfile.objects.get(student_id=student_id)
        academic_records = AcademicRecord.objects.filter(student=student).order_by('academic_year', 'semester')
        
        return render(request, 'records/student_report.html', {
            'student': student,
            'academic_records': academic_records,
            'subjects': ['Chinese', 'English', 'Mathematics', 'Science', 'conduct']
        })
    except StudentProfile.DoesNotExist:
        return render(request, 'records/404.html', {'message': 'Student not found'}, status=404)

def manage_promotions(request):
    if request.method == 'POST':
        to_year = request.POST.get('to_year')
        for student in StudentProfile.objects.all():
            new_class = request.POST.get(f'new_class_{student.student_id}')
            if new_class:
                # Create new class history record
                StudentClassHistory.objects.create(
                    student=student,
                    academic_year=to_year,
                    form_class=new_class,
                    is_current=True
                )
                # Mark previous records as not current
                StudentClassHistory.objects.filter(
                    student=student
                ).exclude(
                    academic_year=to_year
                ).update(is_current=False)
        
        messages.success(request, 'Promotions applied successfully!')
        return redirect('manage_promotions')
    
    # Get distinct years from class history
    year_choices = StudentClassHistory.objects.values_list(
        'academic_year', flat=True
    ).distinct().order_by('academic_year')
    
    # Get students with their current class info
    students = StudentProfile.objects.prefetch_related(
        'class_history'
    ).annotate(
        current_class=F('class_history__form_class'),
        current_year=F('class_history__academic_year')
    ).filter(
        class_history__is_current=True
    ).distinct()
    
    return render(request, 'records/manage_promotion.html', {
        'students': students,
        'year_choices': year_choices,
        'next_year': datetime.now().year + 1
    })