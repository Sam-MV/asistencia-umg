import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import *
from .models import *


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)
    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.staff.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.student.session = session
                user.student.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Manage Students'
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.course = course
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.address = address
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))





# =========================================================================================================================================
# ============================================================== CODIGO UMG ===============================================================
# =========================================================================================================================================

# =================================================================
# CENTRO UNIVERSITARIO (MANY_TO_MANY)
# =================================================================
def agregar_centro(request):
    form = CentroForm(request.POST or None) # It's like an xml but actually it's html
    context = {
        'form': form,
        'page_title': 'Agregar Centro'
    }
    if request.method == 'POST':
        if form.is_valid():
            nombre_nuevo = form.cleaned_data.get('nombre')
            try:
                centro = Centro()
                centro.nombre = nombre_nuevo
                centro.save()
                messages.success(request, "Centro agregado")
                return redirect(reverse('agregar_centro')) # reverse para el patron de dise??o DRY y evitar repetir codigo (Se reutiliza el nombre de la vista, definido en los urls)
            except:
                messages.error(request, "No se pudo agregar")
        else:
            messages.error(request, "No se pudo agregar")
    return render(request, 'hod_template/admin_template_umg/tmpl_agregar_centro.html', context)



def listar_centro(request):
    listado_centros = Centro.objects.all()
    context = {
        'listado_centros': listado_centros,
        'page_title': 'Listado de centros universitarios'
    }
    return render(request, "hod_template/admin_template_umg/tmpl_listar_centro.html", context)



def editar_centro(request, centro_id):
    instancia = get_object_or_404(Centro, id=centro_id)
    formObjeto = CentroForm(request.POST or None, instance=instancia)
    context = {
        'form': formObjeto,
        'course_id': centro_id,
        'page_title': 'Editar centro'
    }
    if request.method == 'POST':
        if formObjeto.is_valid():
            nombre_nuevo = formObjeto.cleaned_data.get('nombre')
            try:
                centro = Centro.objects.get(id=centro_id)
                centro.nombre = nombre_nuevo
                centro.save()
                messages.success(request, "Felicidades, se ha actualizado!")
            except:
                messages.error(request, "No se pudo actualizar")
        else:
            messages.error(request, "No se pudo actualizar")
    return render(request, 'hod_template/admin_template_umg/tmpl_editar_centro.html', context)



def borrar_centro(request, centro_id):
    centro = get_object_or_404(Centro, id=centro_id)
    try:
        centro.delete()
        messages.success(request, "Eliminado!")
    except Exception:
        messages.error(
            request, "Oops, no se pudo eliminar.")
    return redirect(reverse('listar_centro'))





# =================================================================
# Carrera (MANY_TO_MANY)
# =================================================================
def agregar_carrera(request):
    form = CarreraForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Agregar Carrera'
    }
    if request.method == 'POST':
        if form.is_valid():
            codigo_nuevo = form.cleaned_data.get('codigo')
            nombre_nuevo = form.cleaned_data.get('nombre')
            centros_nuevo = form.cleaned_data.get('centros')
            try:
                carrera = Carrera()
                carrera.codigo = codigo_nuevo
                carrera.nombre = nombre_nuevo
                carrera.save()
                for centro in centros_nuevo:
                    carrera.centros.add(centro.id)
                messages.success(request, "Carrera agregado")
                return redirect(reverse('agregar_carrera')) # reverse para el patron de dise??o DRY y evitar repetir codigo (Se reutiliza el nombre de la vista, definido en los urls)
            except Exception as error:
                messages.error(request, "No se pudo agregar")
        else:
            messages.error(request, "No se pudo agregar")
    return render(request, 'hod_template/admin_template_umg/tmpl_agregar_carrera.html', context)



def listar_carrera(request):
    listado_carreras = Carrera.objects.all()
    context = {
        'listado_carreras': listado_carreras,
        'page_title': 'Listado de carreras universitarios'
    }
    return render(request, "hod_template/admin_template_umg/tmpl_listar_carrera.html", context)



def editar_carrera(request, carrera_id):
    instancia = get_object_or_404(Carrera, id=carrera_id)
    formObjeto = CarreraForm(request.POST or None, instance=instancia)
    context = {
        'form': formObjeto,
        'course_id': carrera_id,
        'page_title': 'Editar carrera'
    }
    if request.method == 'POST':
        if formObjeto.is_valid():
            codigo_edicion = formObjeto.cleaned_data.get('codigo')
            nombre_edicion = formObjeto.cleaned_data.get('nombre')
            centros_edicion = formObjeto.cleaned_data.get('centros')
            try:
                carrera = Carrera.objects.get(id=carrera_id)
                carrera.codigo = codigo_edicion
                carrera.nombre = nombre_edicion
                carrera.save()
                # Elimina los registros previamente asociados
                # Removes all prev associated records
                centros_en_db = carrera.centros.all()
                for centro_db in centros_en_db:
                    carrera.centros.remove(centro_db)
                for nuevo_centro in centros_edicion:
                    carrera.centros.add(nuevo_centro.id)
                messages.success(request, "Felicidades, se ha actualizado!")
            except Exception as error:
                messages.error(request, "No se pudo actualizar. Error: ", error)
        else:
            messages.error(request, "No se pudo actualizar")
    return render(request, 'hod_template/admin_template_umg/tmpl_editar_carrera.html', context)



def borrar_carrera(request, carrera_id):
    carrera = get_object_or_404(Carrera, id=carrera_id)
    try:
        carrera.delete()
        messages.success(request, "Eliminado!")
    except Exception:
        messages.error(
            request, "Oops, no se pudo eliminar.")
    return redirect(reverse('listar_carrera'))





# =================================================================
# Semestre (ONE_TO_MANY)
# =================================================================
def agregar_semestre(request):
    form = SemestreForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Agregar Semestre'
    }
    if request.method == 'POST':
        if form.is_valid():
            codigo_nuevo = form.cleaned_data.get('codigo')
            nombre_nuevo = form.cleaned_data.get('nombre')
            carrera_id_nuevo = form.cleaned_data.get('carrera_id')
            try:
                semestre = Semestre()
                semestre.codigo = codigo_nuevo
                semestre.nombre = nombre_nuevo
                semestre.carrera_id = carrera_id_nuevo
                semestre.save()
                messages.success(request, "Semestre agregado")
                return redirect(reverse('agregar_semestre')) # reverse para el patron de dise??o DRY y evitar repetir codigo (Se reutiliza el nombre de la vista, definido en los urls)
            except Exception as error:
                messages.error(request, "No se pudo agregar: ", error)
        else:
            messages.error(request, "No se pudo agregar")
    return render(request, 'hod_template/admin_template_umg/tmpl_agregar_semestre.html', context)



def listar_semestre(request):
    listado_semestres = Semestre.objects.all()
    context = {
        'listado_semestres': listado_semestres,
        'page_title': 'Listado de semestres universitarios'
    }
    return render(request, "hod_template/admin_template_umg/tmpl_listar_semestre.html", context)



def editar_semestre(request, semestre_id):
    instancia = get_object_or_404(Semestre, id=semestre_id)
    formObjeto = SemestreForm(request.POST or None, instance=instancia)
    context = {
        'form': formObjeto,
        'course_id': semestre_id,
        'page_title': 'Editar semestre'
    }
    if request.method == 'POST':
        if formObjeto.is_valid():
            codigo_edicion = formObjeto.cleaned_data.get('codigo')
            nombre_edicion = formObjeto.cleaned_data.get('nombre')
            carrera_id_edicion = formObjeto.cleaned_data.get('carrera_id')
            try:
                semestre = Semestre.objects.get(id=semestre_id)
                semestre.codigo = codigo_edicion
                semestre.nombre = nombre_edicion
                semestre.carrera_id = carrera_id_edicion
                semestre.save()
                messages.success(request, "Felicidades, se ha actualizado!")
            except Exception as error:
                messages.error(request, "No se pudo actualizar. Error: ", error)
        else:
            messages.error(request, "No se pudo actualizar")
    return render(request, 'hod_template/admin_template_umg/tmpl_editar_semestre.html', context)



def borrar_semestre(request, semestre_id):
    semestre = get_object_or_404(Semestre, id=semestre_id)
    try:
        semestre.delete()
        messages.success(request, "Eliminado!")
    except Exception:
        messages.error(
            request, "Oops, no se pudo eliminar.")
    return redirect(reverse('listar_semestre'))





# =================================================================
# Curso (ONE_TO_MANY)
# =================================================================
def agregar_curso(request):
    form = CursoForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Agregar Curso'
    }
    if request.method == 'POST':
        if form.is_valid():
            codigo_nuevo = form.cleaned_data.get('codigo')
            nombre_nuevo = form.cleaned_data.get('nombre')
            semestre_id_nuevo = form.cleaned_data.get('semestre_id')
            try:
                curso = Curso()
                curso.codigo = codigo_nuevo
                curso.nombre = nombre_nuevo
                curso.semestre_id = semestre_id_nuevo
                curso.save()
                messages.success(request, "Curso agregado")
                return redirect(reverse('agregar_curso')) # reverse para el patron de dise??o DRY y evitar repetir codigo (Se reutiliza el nombre de la vista, definido en los urls)
            except Exception as error:
                messages.error(request, "No se pudo agregar: ", error)
        else:
            messages.error(request, "No se pudo agregar")
    return render(request, 'hod_template/admin_template_umg/tmpl_agregar_curso.html', context)



def listar_curso(request):
    listado_cursos = Curso.objects.all()
    context = {
        'listado_cursos': listado_cursos,
        'page_title': 'Listado de cursos universitarios'
    }
    return render(request, "hod_template/admin_template_umg/tmpl_listar_curso.html", context)



def editar_curso(request, curso_id):
    instancia = get_object_or_404(Curso, id=curso_id)
    formObjeto = CursoForm(request.POST or None, instance=instancia)
    context = {
        'form': formObjeto,
        'course_id': curso_id,
        'page_title': 'Editar curso'
    }
    if request.method == 'POST':
        if formObjeto.is_valid():
            codigo_edicion = formObjeto.cleaned_data.get('codigo')
            nombre_edicion = formObjeto.cleaned_data.get('nombre')
            semestre_id_edicion = formObjeto.cleaned_data.get('semestre_id')
            try:
                curso = Curso.objects.get(id=curso_id)
                curso.codigo = codigo_edicion
                curso.nombre = nombre_edicion
                curso.semestre_id = semestre_id_edicion
                curso.save()
                messages.success(request, "Felicidades, se ha actualizado!")
            except Exception as error:
                messages.error(request, "No se pudo actualizar. Error: ", error)
        else:
            messages.error(request, "No se pudo actualizar")
    return render(request, 'hod_template/admin_template_umg/tmpl_editar_curso.html', context)



def borrar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    try:
        curso.delete()
        messages.success(request, "Eliminado!")
    except Exception:
        messages.error(
            request, "Oops, no se pudo eliminar.")
    return redirect(reverse('listar_curso'))





# =================================================================
# Seccion (MANY_TO_MANY)
# =================================================================
def agregar_seccion(request):
    form = SeccionForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Agregar Seccion'
    }
    if request.method == 'POST':
        if form.is_valid():
            codigo_nuevo = form.cleaned_data.get('codigo')
            nombre_nuevo = form.cleaned_data.get('nombre')
            cursos_nuevo = form.cleaned_data.get('cursos')
            try:
                seccion = Seccion()
                seccion.codigo = codigo_nuevo
                seccion.nombre = nombre_nuevo
                seccion.save()
                for centro in cursos_nuevo:
                    seccion.cursos.add(centro.id)
                messages.success(request, "Seccion agregado")
                return redirect(reverse('agregar_seccion')) # reverse para el patron de dise??o DRY y evitar repetir codigo (Se reutiliza el nombre de la vista, definido en los urls)
            except Exception as error:
                messages.error(request, "No se pudo agregar")
        else:
            messages.error(request, "No se pudo agregar")
    return render(request, 'hod_template/admin_template_umg/tmpl_agregar_seccion.html', context)



def listar_seccion(request):
    listado_seccions = Seccion.objects.all()
    context = {
        'listado_seccions': listado_seccions,
        'page_title': 'Listado de seccions universitarios'
    }
    return render(request, "hod_template/admin_template_umg/tmpl_listar_seccion.html", context)



def editar_seccion(request, seccion_id):
    instancia = get_object_or_404(Seccion, id=seccion_id)
    formObjeto = SeccionForm(request.POST or None, instance=instancia)
    context = {
        'form': formObjeto,
        'course_id': seccion_id,
        'page_title': 'Editar seccion'
    }
    if request.method == 'POST':
        if formObjeto.is_valid():
            codigo_edicion = formObjeto.cleaned_data.get('codigo')
            nombre_edicion = formObjeto.cleaned_data.get('nombre')
            cursos_edicion = formObjeto.cleaned_data.get('cursos')
            try:
                seccion = Seccion.objects.get(id=seccion_id)
                seccion.codigo = codigo_edicion
                seccion.nombre = nombre_edicion
                seccion.save()
                # Elimina los registros previamente asociados
                # Removes all prev associated records
                cursos_en_db = seccion.cursos.all()
                for centro_db in cursos_en_db:
                    seccion.cursos.remove(centro_db)
                for nuevo_centro in cursos_edicion:
                    seccion.cursos.add(nuevo_centro.id)
                messages.success(request, "Felicidades, se ha actualizado!")
            except Exception as error:
                messages.error(request, "No se pudo actualizar. Error: ", error)
        else:
            messages.error(request, "No se pudo actualizar")
    return render(request, 'hod_template/admin_template_umg/tmpl_editar_seccion.html', context)



def borrar_seccion(request, seccion_id):
    seccion = get_object_or_404(Seccion, id=seccion_id)
    try:
        seccion.delete()
        messages.success(request, "Eliminado!")
    except Exception:
        messages.error(
            request, "Oops, no se pudo eliminar.")
    return redirect(reverse('listar_seccion'))