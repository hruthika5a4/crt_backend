from django.db import models
import re
from django.core.exceptions import ValidationError

# Constants for choices
SEMESTER_CHOICES = [
    (1, 'I'), (2, 'II'), (3, 'III'), (4, 'IV'),
    (5, 'V'), (6, 'VI'), (7, 'VII'), (8, 'VIII'),
]

DEPT_CHOICES = [
    ('CSE', 'CSE'), ('ECE', 'ECE'), ("EEE", 'EEE'),
    ("MECH", "MECH"), ("CIVIL", "CIVIL"), ("x", "x"),
]

SECTION_CHOICES = [
    ('A', 'A'), ('B', 'B'), ('C', 'C'),
]

STATUS_CHOICES_LSP = [
    ('AC', 'Active'), ('IA', 'Inactive'),
]

GENDER_CHOICES = [
    ('M', 'Male'), ('F', 'Female'),
]

TYPE_CHOICES = [
    ('ST', 'Student'), ('FAC', 'Faculty'), ('HOD', 'HOD'),
]

STATUS_CHOICES = [
    ('NS', 'Not Started'), ('PENDING', 'Pending'), ('COMPLETED', 'Completed'),
]


# Validation function for password
def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True


class College(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly defining the id field
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    # branch = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    sem = models.IntegerField(choices=SEMESTER_CHOICES)
    dept = models.CharField(max_length=10, choices=DEPT_CHOICES, default='x')
    sec = models.CharField(max_length=1, choices=SECTION_CHOICES)
    clg_name = models.ForeignKey('College', on_delete=models.CASCADE,null=True, blank=True)  # ForeignKey for dropdown
    year=models.IntegerField(null=True,blank=True)
    class Meta:
        unique_together = ('sem', 'dept', 'sec')

    def __str__(self):
        return f'{self.sem} - {self.dept} - {self.sec}'
    def save(self, *args, **kwargs):
        # Automatically set the year based on the semester
        if self.sem in [1, 2]:
            self.year = 1
        elif self.sem in [3, 4]:
            self.year = 2
        elif self.sem in [5, 6]:
            self.year = 3
        elif self.sem in [7, 8]:
            self.year = 4

        super().save(*args, **kwargs)
    

class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=32)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    mobile_number = models.BigIntegerField()
    password = models.CharField(max_length=256)
    user_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default="ST")
    clg_name = models.ForeignKey('College', on_delete=models.CASCADE,null=True, blank=True) 
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE, null=True, blank=True) 
    roll_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    status = models.CharField(max_length=3, choices=[('NAC', 'Not Active'), ('AC', 'Active')], default='NAC')
    graduation_year = models.PositiveIntegerField(null=True, blank=True, default=2024)
    dept = models.CharField(max_length=10, choices=DEPT_CHOICES)
    
    
    # specialisation = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)

    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)  # Optional profile photo
    reset_password = models.CharField(max_length=10, null=True, blank=True)

    def has_phd(self):
        return self.qualification and 'phd' in self.qualification.lower()

    def __str__(self):
        return self.name + self.dept

    def clean(self, update_fields=None):
        """
        Custom validation logic for model fields.
        """
        if not validate_password(self.password):
            raise ValidationError('Password should have at least 8 characters, including uppercase, lowercase, and a number.')

        if self.user_type == 'ST':
            if not self.roll_number:
                raise ValidationError('Roll number is mandatory for students.')
            if not self.graduation_year:
                raise ValidationError('Graduation year is mandatory for students.')
            if not self.clg_name:
                raise ValidationError('clg_name is mandatory for students.')
            if not self.class_id:
                raise ValidationError('class_id is mandatory for students.')
                      
        else:
            # if not self.specialisation:
            #     raise ValidationError('Specialisation is mandatory.')
            # if not self.qualification:
            #     raise ValidationError('Qualification is mandatory.')
            # if not self.designation:
            #     raise ValidationError('Designation is mandatory.')
            # if not self.dept:
            #     raise ValidationError('dept is mandatory.')
            if not self.clg_name:
                raise ValidationError('clg_name is mandatory for faculty.')
            

    def save(self, *args, **kwargs):
        """
        Override the save method to include custom logic before saving the model.
        """
        self.clean()

        if self.user_type == 'HOD':
            self.status = 'AC'
        else:
            self.status = 'NAC'

        super().save(*args, **kwargs)


class Subject(models.Model):
    sub_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    faculty_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name




class LessonPlan(models.Model):
    name = models.CharField(max_length=255)
    subject_id = models.OneToOneField(Subject, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES_LSP, default='IA')

    def total_hours(self):
        return self.topic.aggregate(total=models.Sum('hours'))['total'] or 0
    

class Topic(models.Model):
    STATUS_CHOICES = [
        ('NS', 'Not Started'), ('C', 'Completed'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    LessonPlan_id=models.ForeignKey(LessonPlan, on_delete=models.CASCADE,blank=True, null=True)
    hours = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='NS')
    comments = models.TextField(blank=True, null=True)
    target_date = models.DateField()
    actual_completed_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name


class Approval(models.Model):
    approval_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=100,blank=True,null=True)
    user_email = models.EmailField()
    hod_id = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'HOD'}, related_name='hod_approvals')
    dept = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('rejected', 'Rejected'), ('approved', 'Approved')], default='pending')
    approval_type = models.CharField(max_length=50, choices=[
        ('new_stu_account', 'New Student Account'),
        ('new_fac_account', 'New Faculty Account'),
        ('new_lessonplan_approval', 'New Lesson Plan Approval')
    ], default='new_stu_account')
    old_data = models.TextField(null=True, blank=True)
    new_data = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_email} - {self.dept} - {self.status}"
