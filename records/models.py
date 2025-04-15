from django.db import models

class StudentProfile(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    contact_number = models.CharField(max_length=15) 
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class StudentClassHistory(models.Model):
    ACADEMIC_YEAR_CHOICES = [
        (2022, '2022-2023'),
        (2023, '2023-2024'), 
        (2024, '2024-2025'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE,
                        related_name='class_history', to_field='student_id')
    academic_year = models.PositiveSmallIntegerField(
        help_text="The starting year of the academic year (e.g. 2022 for 2022-2023)",
        choices=ACADEMIC_YEAR_CHOICES
    )
    form_class = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'academic_year')
        ordering = ['student', '-academic_year']
        get_latest_by = 'academic_year'

    def __str__(self):
        return f"{self.student} - {self.academic_year}: {self.form_class} {'(Current)' if self.is_current else ''}"

    def academic_year_display(self):
        return f"{self.academic_year}-{self.academic_year + 1}"

class AcademicRecord(models.Model):
    ACADEMIC_YEAR_CHOICES = [
        (2022, '2022-2023'),
        (2023, '2023-2024'),
        (2024, '2024-2025'),
    ]
    
    SEMESTER_CHOICES = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
    ]

    CONDUCT_CHOICES = [
        ('A', 'Excellent'),
        ('B', 'Good'),
        ('C', 'Satisfactory'),
        ('D', 'Needs Improvement'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE,
                            related_name='academic_records', 
                            to_field='student_id')
    id = models.AutoField(primary_key=True)
    academic_year = models.PositiveSmallIntegerField(
        help_text="The starting year of the academic year (e.g. 2022 for 2022-2023)",
        choices=ACADEMIC_YEAR_CHOICES
    )
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    Chinese = models.PositiveSmallIntegerField(default=0)  # Score out of 100
    English = models.PositiveSmallIntegerField(default=0)  # Score out of 100
    Mathematics = models.PositiveSmallIntegerField(default=0)  # Score out of 100
    Science = models.PositiveSmallIntegerField(default=0)
    conduct = models.CharField(max_length=1, choices=CONDUCT_CHOICES)

    class Meta:
        unique_together = ('student', 'semester', 'academic_year')
        ordering = ['student', 'academic_year', 'semester']
        verbose_name = 'Academic Record'
        verbose_name_plural = 'Academic Records'
    
    def __str__(self):
        return f"{self.student} - Semester {self.get_semester_display()} ({self.academic_year})"

    def academic_year_display(self):
        return f"{self.academic_year}-{self.academic_year + 1}"    
