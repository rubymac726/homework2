from django.contrib import admin
from .models import StudentProfile, AcademicRecord, StudentClassHistory

class StudentClassHistoryInline(admin.TabularInline):
    model = StudentClassHistory
    extra = 1
    fields = ('academic_year', 'form_class', 'is_current')
    ordering = ('-academic_year',)

class CurrentClassFilter(admin.SimpleListFilter):
    title = 'current class'
    parameter_name = 'current_class'

    def lookups(self, request, model_admin):
        return StudentClassHistory.objects.filter(
            is_current=True
        ).values_list('form_class', 'form_class').distinct()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                class_history__form_class=self.value(),
                class_history__is_current=True
            )

class AcademicYearFilter(admin.SimpleListFilter):
    title = 'academic year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        return StudentClassHistory.objects.values_list(
            'academic_year', 'academic_year'
        ).distinct()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                class_history__academic_year=self.value()
            )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    inlines = [StudentClassHistoryInline]
    list_display = ('student_id', 'first_name', 'last_name', 'current_class_display')
    list_filter = (CurrentClassFilter, AcademicYearFilter)
    search_fields = ('student_id', 'first_name', 'last_name')

    def current_class_display(self, obj):
        current = obj.class_history.filter(is_current=True).first()
        return f"{current.form_class} ({current.academic_year})" if current else "N/A"
    current_class_display.short_description = 'Current Class'

@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'semester', 'Chinese', 'English', 'Mathematics', 'Science', 'conduct')
    list_filter = ('semester', 'conduct', 'academic_year')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name')