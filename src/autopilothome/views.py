from datetime import date
import json, boto3, time
import os
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from accounts.models import Company, CustomUser, Licence
from django.conf import settings
from autopilothome.aws_utils import create_empty_folder, get_bucket_list, get_pdf_from_aws, read_file_from_s3_bucket
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from main.models import Elaborat, ElaboratDocument, ElaboratSubjectDocument, Subject


def home_view(request):
    context = {
        'og_description': 'Softver za povezivanje predmeta,parcela i objekata pruža laku pretragu centraliziranu bazu,automatizaciju elaborata,     transparentnost klijentima te brzu podršku.',
        'og_image': request.build_absolute_uri('/static/img/autopilot.png'),
        'og_url': request.build_absolute_uri(),
        'twitter_image': 'static/img/Autopilot.png',
        'twitter_description': 'Softver za povezivanje predmeta,parcela i objekata pruža laku pretragu centraliziranu bazu,automatizaciju elaborata, transparentnost klijentima te brzu podršku.'
    }
    return render(request, "pages/home.html", context)


def error_view(request):
    return render(request, "pages/error.html", {})


def editor(request, id, pk, assemble=None):
    subject = get_object_or_404(Subject, pk=pk)
    if assemble == 'faktura':
        aws_name = 'faktura.pdf'
        return render(request, "pages/editor.html", {'id': id, 'subject': subject, 'aws_name': aws_name, })
    elif assemble == 'root':
        document = ElaboratDocument.objects.get(template_number = id)
        aws_name = document.aws_name
        return render(request, "pages/editor.html", {'id': id, 'aws_name': aws_name, 'subject': subject })
    # only on assembling elaborat
    if assemble is not None:
        elaborat = Elaborat.objects.get(subject=subject)
        docs = elaborat.elaboratsubjectdocument_set.all().order_by('order')
        try:
            document = ElaboratDocument.objects.get(template_number = id)
            aws_name = document.aws_name
            return render(request, "pages/editor.html", {'id': id, 'aws_name': aws_name, 'subject': subject, 'assemble': assemble, 'docs': docs})
        except:
            return render(request, "pages/editor.html", {'id': id, 'subject': subject, 'assemble': assemble, 'docs': docs})
    # not assembling elaborat
    else:
        try:
            elaborat = Elaborat.objects.get(subject=subject)
            docs = elaborat.elaboratsubjectdocument_set.all().order_by('order')
            try:
                document = ElaboratDocument.objects.get(template_number = id)
                aws_name = document.aws_name
                return render(request, "pages/editor.html", {'id': id, 'aws_name': aws_name, 'subject': subject, 'docs': docs})
            except:
                return render(request, "pages/editor.html", {'id': id, 'subject': subject, 'docs': docs})
        except:
            return render(request, "pages/editor.html", {'id': id, 'subject': subject })


@csrf_exempt
def login_autocad_user(request):
    if request.method == 'POST':
        # check incoming data
        try:
            data = json.loads(request.body)
            email = data.get("email")
            pin = data.get("pin")
            module = data.get("module")
            user_time = data.get("time")
        except:
            response_data = {
            'message': 'hacking not allowed'
            }
        # check user existance
        try:
            user = CustomUser.objects.get(email=email)
            # check if user have licence
            try:
                licence = Licence.objects.get(user=user)
                if pin != licence.pin:
                    response_data = {
                    'message': 'No email'
                    }
                    return JsonResponse(response_data)
            except CustomUser.DoesNotHaveLicence:
                response_data = {
                "Message": "No email"
                }
                return JsonResponse(response_data)
            # check licence date
            try:
                if licence.valid <= date.today():
                    response_data = {
                        "Message": "No date",
                        "Date": licence.valid
                    }
                    return JsonResponse(response_data)
            except:
                response_data = {
                "Message": "No date"
                }
                return JsonResponse(response_data)
            # check module
            if licence.modul.name != module:
                response_data = {
                        "Message": "No module"
                    }
                return JsonResponse(response_data)
            # check time
            if user_time != "":
                if licence.server_time is None:
                    response_data = {
                        "Message": "Need Login"
                    }
                    return JsonResponse(response_data)
                elif str(licence.server_time) != user_time:
                    response_data = {
                        "Message": "Used Module"
                    }
                    return JsonResponse(response_data)
                elif str(licence.server_time) == user_time:
                    response_data = {
                        "Message": "OK"
                    }
                    return JsonResponse(response_data)
            # elif licence.server_time is not None:
            #     response_data = {
            #         "Message": "Used Module"
            #     }
            #     return JsonResponse(response_data)

            current_time = time.time()
            licence.server_time = current_time
            licence.save()
            response_data = {
                "Message": "OK",
                'Ime': user.first_name,
                'Prezime': user.last_name,
                'Email': email,
                'PIN': licence.pin,
                'Modul': licence.modul.name,
                'Date': licence.valid,
                'Company': user.company.full_name,
                'Time': current_time
            }
            # return valid data
        except CustomUser.DoesNotExist:
            response_data = {
                "Message": "No email"
            }
        return JsonResponse(response_data)
    

@csrf_exempt
def logout_autocad_user(request):
    if request.method == 'POST':
        # check incoming data
        try:
            data = json.loads(request.body)
            print(data)
            email = data.get("email")
            pin = data.get("pin")
            module = data.get("module")
        except:
            response_data = {
            'message': 'podaci nisu stigli'
            }
        # check user existance
        try:
            user = CustomUser.objects.get(email=email)
            try:
                licence = Licence.objects.get(user=user)
                if pin != licence.pin:
                    response_data = {
                    'message': 'No email'
                    }
                    return JsonResponse(response_data)
            except CustomUser.DoesNotHaveLicence:
                response_data = {
                "Message": "No email"
                }
                return JsonResponse(response_data)
            # check licence date
            try:
                if licence.valid <= date.today():
                    response_data = {
                        "Message": "No date",
                        "Date": licence.valid
                    }
                    return JsonResponse(response_data)
            except:
                response_data = {
                "Message": "No date"
                }
                return JsonResponse(response_data)
            # check module
            if licence.modul.name != module:
                response_data = {
                        "Message": "No module"
                    }
                return JsonResponse(response_data)
            licence.server_time = None
            licence.save()
            response_data = {
                "Message": "OK",
            }
            # return valid data
        except CustomUser.DoesNotExist:
            response_data = {
                "Message": "No email"
            }
        return JsonResponse(response_data)
    

@csrf_exempt
def check_autocad_user(request):
    if request.method == 'POST':
        # check incoming data
        try:
            data = json.loads(request.body)
            print(data)
            email = data.get("email")
            pin = data.get("pin")
        except:
            response_data = {
            'message': 'podaci nisu stigli'
            }
        # check user existance
        try:
            user = CustomUser.objects.get(email=email)
            try:
                licence = Licence.objects.get(user=user)
                if pin != licence.pin:
                    response_data = {
                    'message': 'No email'
                    }
                    return JsonResponse(response_data)
            except CustomUser.DoesNotHaveLicence:
                response_data = {
                "Message": "No email"
                }
                return JsonResponse(response_data)
            # check licence date
            try:
                if licence.valid <= date.today():
                    response_data = {
                        "Message": "No date",
                        'Ime': user.first_name,
                        'Prezime': user.last_name,
                        'Email': email,
                        'PIN': licence.pin,
                        'Modul': licence.modul.name,
                        'Date': licence.valid,
                        'Company': user.company.full_name,
                    }
                    return JsonResponse(response_data)
                else:
                    response_data = {
                        'Message': 'OK',
                        'Ime': user.first_name,
                        'Prezime': user.last_name,
                        'Email': email,
                        'PIN': licence.pin,
                        'Modul': licence.modul.name,
                        'Date': licence.valid,
                        'Company': user.company.full_name,
                    }
            except:
                response_data = {
                "Message": "No date"
                }
                return JsonResponse(response_data)
        except CustomUser.DoesNotExist:
            response_data = {
                "Message": "No email"
            }
        return JsonResponse(response_data)


def bucket_list_view(request):
    # buckets = get_bucket_list()
    return render(request, 'pages/buckets_list.html')


def send_file(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        file = read_file_from_s3_bucket(data.get('bucket'), data.get('folder'), data.get('file'))
        response_data = {
            'text': file
        }
        return JsonResponse(response_data)
    

def accept_pdf(request):
    # Get the uploaded PDF file
    # pdf_file = request.FILES['pdf']
    # bucket_name = 'autopilot-kancelarija-27'
    # key = 'Predmet-60/output2.pdf'
    # s3 = boto3.client('s3')
    # s3.upload_fileobj(pdf_file, bucket_name, key)
    # Process the uploaded PDF as needed (e.g., save it to disk, extract data, etc.)
    # ...
    my_file = request.FILES['my_file']  # Assuming you have a file input named 'my_file' in your HTML form

    # Create a file storage instance
    fs = FileSystemStorage()

    # Save the my_file file locally
    filename = fs.save(my_file.name, my_file)

    # Get the file URL
    file_url = fs.url(filename)

    # You can also access other properties like the file path
    file_path = fs.path(filename)
    print(file_path)

    # Do something with the file URL or file path, such as storing it in your model or displaying it to the user

    return HttpResponse(f'File saved. URL: {file_url}, Path: {file_path}')
    # return HttpResponse('PDF received successfully!')


def download_elaborat_primer(request):
    bucket = '369-root'
    file_name = 'elaborat-primer.pdf'
    file = get_pdf_from_aws(bucket, file_name)
    response = HttpResponse(content_type='application/pdf')
    response.write(file)
    return response


def user_files(request):
    company = get_object_or_404(Company, pk=27)
    users = CustomUser.objects.filter(company=company).all()
    s3 = boto3.client('s3')
    for user in users:
        try:
            s3.head_object(Bucket=f'autopilot-kancelarija-{company.id}', Key=f'zaposleni-{user.id}/profile.png')
            print(user, 'profile picture exists')
        except:
            print(user, 'profile picture does not exists')
        # try:
        #    s3.head_object(Bucket=f'autopilot-kancelarija-{company.id}', Key=(f'zaposleni-{user.id}/'))
        #    print('folder postoji') 
        # except:
        #     s3.put_object(Bucket=f'autopilot-kancelarija-{company.id}', Key=f'zaposleni-{user.id}/')
        #     print('folder ne postoji')
        # response = s3.list_objects_v2(Bucket=f'autopilot-kancelarija-{company.id}', Prefix=f'{user.email}/')
        # for obj in response.get('Contents', []):
        #     source_key = obj['Key']
        #     destination_key = source_key.replace(f'{user.email}/', f'zaposleni-{user.id}/', 1)
        #     s3.copy_object(Bucket=f'autopilot-kancelarija-{company.id}', CopySource={'Bucket': f'autopilot-kancelarija-{company.id}', 'Key': source_key}, Key=destination_key)
    return HttpResponse('ok')


def subject_files():
    subjects = Subject.objects.all()
    print(subjects.count())
    for subject in subjects:
        print(subject.service_type)
        print(subject.service_type.elaborat)
        print(subject.elaborat_set.all())
        print('-----------------------------------')