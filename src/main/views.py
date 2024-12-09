import calendar
import datetime
import io
import json
import os
import boto3
from botocore.exceptions import ClientError
import tempfile
from bs4 import BeautifulSoup
from django.core import serializers
from django.forms import formset_factory
from django.http import FileResponse, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import mechanicalsoup
from accounts.models import CustomUser, Assosiate, Company
from autopilothome.decorators import work_with_users, work_with_assosiates, work_with_subjects, work_with_clients
from autopilothome.aws_utils import create_empty_folder, delete_object, get_file_from_aws, get_png_from_aws, upload_file_to_s3, get_folders_in_folder, get_pdf_from_aws, read_file_from_s3_bucket, read_files_in_folder
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .forms import AddCommentForm, AddLotForm, AddLotObjectForm, EditGpsDeviceForm, RegisterSubjectForm, EditSubjectForm
from .models import Comment, Elaborat, ElaboratDocument, ElaboratSubjectDocument, GpsDevice, Lot, LotObject, Subject, Client, Katastar, ElaboratType

@login_required
def index(request):
    return render(request, 'main/index.html', {})


def companies(request):
    companies = Company.objects.all()
    return render(request, 'main/companies.html', {'companies': companies})


@login_required
@work_with_users()
def users(request):
    comp = request.user.company
    users = CustomUser.objects.filter(company=comp)
    return render(request, 'main/users.html', {'users': users})


@login_required
@work_with_assosiates()
def assosiates(request):
    comp = request.user.company
    assosiates = Assosiate.objects.filter(company=comp)
    return render(request, 'main/assosiates.html', {'assosiates': assosiates})


@login_required
@work_with_clients()
def clients(request):
    comp = request.user.company
    clients = Client.objects.filter(company=comp)
    return render(request, 'main/clients.html', {'clients': clients})


@login_required
def subject(request, pk, message=None):
    subject = get_object_or_404(Subject, pk=pk)
    if request.user.company != subject.company:
        return HttpResponse('Vi nemate pravo da vidite ovaj predmet')
    if message:
        message = message
    company_id = subject.company.id
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=f"autopilot-kancelarija-{company_id}", Key=f'Predmet-{subject.id}/CAD/')
    except ClientError as e:
            create_empty_folder(f"autopilot-kancelarija-{company_id}", f'Predmet-{subject.id}/CAD')
    received_files = read_files_in_folder(f'autopilot-kancelarija-{company_id}', f'Predmet-{pk}')
    root_files = [rf for rf in received_files if rf.count('/') == 1]
    files = [rf for rf in received_files if rf.count('/') != 1]
    return render(request, 'main/subject.html', {'subject': subject, 'root_files': root_files, 'files': files, 'message': message})


@login_required
def subjects(request):
    if request.user.has_full_access:
        subjects = Subject.objects.filter(company=request.user.company).order_by('-id')
    else:
        subjects = Subject.objects.filter(users__id=request.user.id).order_by('-id')
    return render(request, 'main/subjects.html', {'subjects': subjects})


@login_required
def company_stats(request):
    company = request.user.company

    # get users and their subjects
    users = [f'{user.first_name} {user.last_name}' for user in company.customuser_set.all()]
    user_subjects = [customuser.subject_set.all().count() for customuser in company.customuser_set.all()]

    # get current month and previous 5 in the list
    month_list = []
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    month_list.append((current_month, current_year))
    for previous_five in range(5):
        current_month -= 1
        if current_month == 0:
            current_month = 12
            current_year -= 1
        month_list.append((current_month, current_year))
    month_names = []
    month_values = []
    for month in month_list:
        subjects_in_month = Subject.objects.filter(start_date__year=month[1], start_date__month=month[0]).count()
        month_names.append(calendar.month_name[month[0]])
        month_values.append(subjects_in_month)

    # get 10 longest subject
    today = datetime.date.today()
    all_subjects = Subject.objects.annotate(date_difference=today - F('start_date'))
    sorted_subjects = all_subjects.order_by('start_date')[:10]
    subjects_lengths = [subject.date_difference.days for subject in sorted_subjects]
    subjects_ids = [subject.id for subject in sorted_subjects]

    # get subject types
    subjects = Subject.objects.all().order_by('id')
    subject_types = []
    types_number = []
    for subject in subjects:
        if subject.service_type.name not in subject_types:
            subject_types.append(subject.service_type.name)
            types_number.append(Subject.objects.filter(service_type=subject.service_type).count())

    return render(request, 'main/company_stats.html', { 'users': json.dumps(users),
                                                        'user_subjects': json.dumps(user_subjects),
                                                        'month_names': json.dumps(month_names),
                                                        'month_values': json.dumps(month_values),
                                                        'subjects_lengths': json.dumps(subjects_lengths),
                                                        'subjects_ids': json.dumps(subjects_ids),
                                                        'subject_types': json.dumps(subject_types),
                                                        'types_number': json.dumps(types_number) })


@login_required
@work_with_subjects()
def open_subject(request):
    form = RegisterSubjectForm()
    if request.method == "POST":
        form = RegisterSubjectForm(request.POST or None)
        if form.is_valid():
            selected_object = form.cleaned_data['tip_posla']
            new_subject = Subject.objects.create()
            new_subject.company = request.user.company
            new_subject.service_type = selected_object
            new_subject.users.add(request.user)
            new_subject.save()
            if new_subject.service_type.elaborat:
                # create elaborat
                new_elaborat = Elaborat.objects.create()
                new_elaborat.name = 'Elaborat1'
                new_elaborat.subject = new_subject
                new_elaborat.save()
                create_empty_folder(f'autopilot-kancelarija-{new_subject.company.id}', f'Predmet-{new_subject.id}')
                create_empty_folder(f"autopilot-kancelarija-{new_subject.company.id}", f'Predmet-{new_subject.id}/Elaborati')
                create_empty_folder(f"autopilot-kancelarija-{new_subject.company.id}", f'Predmet-{new_subject.id}/Elaborati/Elaborat1')
            redirect_url = reverse('main:edit-subject', args=[new_subject.id])
            return redirect(redirect_url)
    return render(request, 'main/open_subject.html', { 'form': form })


@login_required
@work_with_subjects()
def edit_subject(request, pk):
    instance = get_object_or_404(Subject, pk=pk)
    cadastrals = serializers.serialize("json", Katastar.objects.all())
    clients = instance.clients.all()
    if request.method == "POST":
        form = EditSubjectForm(request.POST or None, instance=instance, current_user=request.user)
        if form.is_valid():
            returned_subject = form.save(commit=False)
            if form.cleaned_data['field_worker']:
                returned_subject.users.add(form.cleaned_data['field_worker'])
            returned_subject.field_worker = form.cleaned_data['field_worker']
            if form.cleaned_data['office_worker']:
                returned_subject.users.add(form.cleaned_data['office_worker'])
            returned_subject.office_worker = form.cleaned_data['office_worker']
            if form.cleaned_data['responsible_worker']:
                returned_subject.users.add(form.cleaned_data['responsible_worker'])
            returned_subject.responsible_worker = form.cleaned_data['responsible_worker']
            if form.cleaned_data['assosiate']:
                returned_subject.assosiate = form.cleaned_data['assosiate']
            returned_subject.save()
        return redirect('main:subject', pk=pk)
    else:
        form = EditSubjectForm(instance=instance, current_user=request.user)
    return render(request, 'main/edit_subject.html', { 'form': form,
                                                       'instance': instance,
                                                       'clients': clients,
                                                       'cadastrals': cadastrals })


def js_submit_subject_form(request, pk):
    if request.method == 'POST':
        print('submitted')
        print(pk)
        instance = get_object_or_404(Subject, pk=pk)
        form = EditSubjectForm(request.POST or None, instance=instance, current_user=request.user)
        print(form)
        # if form.is_valid():
        #     form.save()
        return JsonResponse({'message': 'ok'})


# text files
def return_aws_preview(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        bucket = data['bucket']
        file_name = data['link']
        file = get_file_from_aws(bucket, file_name)
        response_data = { 'returned': file }
        return JsonResponse(response_data)
    

# pdf files
def return_aws_pdf(request):
    if request.method =='POST':
        data = json.loads(request.body)
        print(data)
        bucket = data['bucket']
        file_name = data['link']
        file = get_pdf_from_aws(bucket, file_name)
        response = HttpResponse(content_type='application/pdf')
        response.write(file)
        return response
    

# png files
def return_aws_png(request):
    if request.method =='POST':
        data = json.loads(request.body)
        bucket = data['bucket']
        file_name = data['link']
        file = get_png_from_aws(bucket, file_name)
        response = HttpResponse(content_type='image/png')
        response.write(file)
        return response


def register_lot(request, pk):
    #ObjectFormSet = formset_factory(AddLotObjectForm, extra=1)
    if request.method == 'POST':
        form = AddLotForm(request.POST or None)
        #formset = ObjectFormSet(request.POST, prefix='object_formset')
        subject = get_object_or_404(Subject, pk=pk)
        if form.is_valid():
            new_lot = Lot.objects.create()
            new_lot.lot_number = form.cleaned_data['lot_number']
            new_lot.subject = subject
            new_lot.save()
            return redirect('main:edit-subject', pk=pk)
    else:
        form = AddLotForm()
        #formset = ObjectFormSet(prefix='object_formset')
        return render(request, 'main/add_lot.html', {'form': form, 'pk': pk})
    

def add_lot_object(request, lotNumber, pk):
    lotNumber = lotNumber.replace("-", "/")
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = AddLotObjectForm(request.POST or None)
        if Lot.objects.filter(lot_number=lotNumber, subject=subject):
            new_lot = get_object_or_404(Lot, lot_number=lotNumber, subject=subject)
        else:
            new_lot = Lot.objects.create()
            new_lot.lot_number = lotNumber
            new_lot.subject = subject
            new_lot.save()
        if form.is_valid():
            new_lot_object = form.save(commit=False)
            new_lot_object.lot = new_lot
            new_lot_object.save()
        return redirect('main:subject', pk=pk)
    else:
        form = AddLotObjectForm()
        return render(request, 'main/add_lot_object.html', {'form': form, 'lotNumber': lotNumber, 'pk': pk})


def grider_etrf2000_gk7(request):
    if request.method == 'POST':
        uploaded_file = request.POST.get("file")
        print(uploaded_file)
        pk = request.POST.get("pk")
        tip = request.POST.get("tip")
    browser = mechanicalsoup.StatefulBrowser()
    subject = get_object_or_404(Subject, pk=pk)
    user_name = subject.company.grider_login_name
    password = subject.company.grider_password
    if user_name == None or password == None:
        browser.close()
        data = {'message': 'Podaci za prijavljivanje nisu uneti ili su netačni'}
        return JsonResponse(data)
    try:
        input_file = get_file_from_aws(f'autopilot-kancelarija-{subject.company.id}', f'{uploaded_file}')
    except:
        browser.close()
        data = {'message': 'Fajl nije pronađen na AWS-u'}
        return JsonResponse(data)
    dot_position = uploaded_file.find('.')
    output_txt_file = f'Predmet-{pk}/Grider/gk.txt'
    output_pdf_file = f'Predmet-{pk}/Grider/gk.pdf'
    output_lista_file = f'Predmet-{pk}/Grider/gklista.txt'

    real_headers = {
    "Host" : "grider.rgz.gov.rs",
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language" : "en-US,en;q=0.5",
    "Accept-Encoding" : "gzip, deflate, br",
    "Referer" : "https://google.com/",
    "DNT" : "1",
    "Connection" : "close",
    "Upgrade-Insecure-Requests" : "1",
    "Sec-Fetch-Dest" : "document",
    "Sec-Fetch-Mode" : "navigate",
    "Sec-Fetch-Site" : "cross-site",
    }
    browser.session.headers = real_headers
    try:
        # step 1 - openning portal
        browser.open("https://grider.rgz.gov.rs/login_lg.php?")
    except:
        browser.close()
        data = {'message': 'Grider server trenutno ne radi'}
        return JsonResponse(data)

    # step 2 - loging in
    browser.select_form('form[name="pristupnaForma"]')
    browser["username"] = user_name
    browser["password"] = password
    resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/grider_w.php':
        browser.close()
        data = {'message': 'Neuspešno prijavljivanje \n proverite username i password'}
        return JsonResponse(data)

    # getting expire date
    soup_date = BeautifulSoup(resp.text, 'lxml')
    datum = soup_date.find("input", attrs={"name": "datum"})
    print(datum['value'])

    # step 3 - selecting job
    browser.select_form('form[action="maska1.php"]')
    resp = browser.submit_selected()


    # step 4 - uploading input file
    form = browser.select_form('form[action="wgs2gk_1.php"]')
    form.set("ULAZ1", tip)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(input_file.encode())
        temp_file.seek(0)
        form["ime_fajla"] = open(temp_file.name, "rb")
        resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/wgs2gk_1.php':
        browser.close()
        data = {'message': 'Fajl nije učitan na grider'}
        return JsonResponse(data)


    # # step 5 - executing conversion
    browser.select_form('form[action="wgs2gk_2.php"]')
    resp = browser.submit_selected()
    soup = BeautifulSoup(resp.text, 'lxml')
    text_output = soup.find("textarea", attrs={"name": "kor2"}).text
    if '***' in text_output:
        browser.close()
        data = {'message': text_output}
        return JsonResponse(data)


    # step 6 - downloading .txt and .pdf output files
    browser.select_form('form[action="dload1.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao fajl sa listom'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_lista_file, resp.content)

    browser.select_form('form[action="dload2.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao text fajl'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_txt_file, resp.content)

    browser.select_form('form[action="izlaz_pdf.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao pdf fajl'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_pdf_file, resp.content)

    browser.close()
    os.remove(temp_file.name)
    data = {'message': 'ok'}
    return JsonResponse(data)


def grider_gk7_etrf2000(request):
    if request.method == 'POST':
        uploaded_file = request.POST.get("file")
        pk = request.POST.get("pk")
        tip = request.POST.get("tip")
    browser = mechanicalsoup.StatefulBrowser()
    subject = get_object_or_404(Subject, pk=pk)  
    user_name = subject.company.grider_login_name
    password = subject.company.grider_password
    if user_name == None or password == None:
        browser.close()
        data = {'message': 'Podaci za prijavljivanje nisu uneti ili su netačni'}
        return JsonResponse(data)
    try:
        input_file = get_file_from_aws(f'autopilot-kancelarija-{subject.company.id}', f'{uploaded_file}')
    except:
        browser.close()
        data = {'message': 'Fajl nije pronađen na AWS-u'}
        return JsonResponse(data)
    dot_position = uploaded_file.find('.')
    # output_txt_file = f'{uploaded_file[:dot_position]}-etrf{uploaded_file[dot_position:]}'
    # output_pdf_file = f'{uploaded_file[:dot_position]}-etrf.pdf'
    output_lista_file = f'{uploaded_file[:dot_position]}-etrflista.txt'

    real_headers = {
    "Host" : "grider.rgz.gov.rs",
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language" : "en-US,en;q=0.5",
    "Accept-Encoding" : "gzip, deflate, br",
    "Referer" : "https://google.com/",
    "DNT" : "1",
    "Connection" : "close",
    "Upgrade-Insecure-Requests" : "1",
    "Sec-Fetch-Dest" : "document",
    "Sec-Fetch-Mode" : "navigate",
    "Sec-Fetch-Site" : "cross-site",
    }
    browser.session.headers = real_headers
    try:
        # step 1 - openning portal
        browser.open("https://grider.rgz.gov.rs/login_lg.php?")
    except:
        browser.close()
        data = {'message': 'Grider server trenutno ne radi'}
        return JsonResponse(data)

    # step 2 - loging in
    browser.select_form('form[name="pristupnaForma"]')
    browser["username"] = user_name
    browser["password"] = password
    resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/grider_w.php':
        browser.close()
        data = {'message': 'Neuspešno prijavljivanje \n proverite username i password'}
        return JsonResponse(data)

    # step 3 - selecting job
    browser.select_form('form[action="maska2.php"]')
    resp = browser.submit_selected()

    # step 4 - uploading input file
    form = browser.select_form('form[action="gk2wgs_1.php"]')
    form.set("IZLAZ1", tip)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(input_file.encode())
        temp_file.seek(0)
        form["ime_fajla"] = open(temp_file.name, "rb")
        resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/gk2wgs_1.php':
        browser.close()
        data = {'message': 'Fajl nije učitan na grider'}
        return JsonResponse(data)

    # # step 5 - executing conversion
    browser.select_form('form[action="gk2wgs_2.php"]')
    resp = browser.submit_selected()
    soup = BeautifulSoup(resp.text, 'lxml')
    text_output = soup.find("textarea", attrs={"name": "kor2"}).text
    if '***' in text_output:
        browser.close()
        data = {'message': text_output}
        return JsonResponse(data)

    # step 6 - downloading .txt and .pdf output files
    browser.select_form('form[action="dload1.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao fajl sa listom'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_lista_file, resp.content)

    browser.close()
    os.remove(temp_file.name)
    data = {'message': 'ok'}
    return JsonResponse(data)


def grider_trst_nvt2(request):
    if request.method == 'POST':
        uploaded_file = request.POST.get("file")
        pk = request.POST.get("pk")
    browser = mechanicalsoup.StatefulBrowser()
    subject = get_object_or_404(Subject, pk=pk)
    user_name = subject.company.grider_login_name
    password = subject.company.grider_password
    if user_name == None or password == None:
        browser.close()
        data = {'message': 'Podaci za prijavljivanje nisu uneti ili su netačni'}
        return JsonResponse(data) 
    try:
        input_file = get_file_from_aws(f'autopilot-kancelarija-{subject.company.id}', f'{uploaded_file}')
        print(input_file)
    except:
        browser.close()
        data = {'message': 'Fajl nije pronađen na AWS-u'}
        return JsonResponse(data)

    dot_position = uploaded_file.find('.')
    # output_txt_file = f'{uploaded_file[:dot_position]}-nvt{uploaded_file[dot_position:]}'
    # output_pdf_file = f'{uploaded_file[:dot_position]}-nvt.pdf'
    output_lista_file = f'{uploaded_file[:dot_position]}-nvtlista.txt'

    real_headers = {
    "Host" : "grider.rgz.gov.rs",
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language" : "en-US,en;q=0.5",
    "Accept-Encoding" : "gzip, deflate, br",
    "Referer" : "https://google.com/",
    "DNT" : "1",
    "Connection" : "close",
    "Upgrade-Insecure-Requests" : "1",
    "Sec-Fetch-Dest" : "document",
    "Sec-Fetch-Mode" : "navigate",
    "Sec-Fetch-Site" : "cross-site",
    }
    browser.session.headers = real_headers

    try:
        # step 1 - openning portal
        browser.open("https://grider.rgz.gov.rs/login_lg.php?")
    except:
        browser.close()
        data = {'message': 'Grider server trenutno ne radi'}
        return JsonResponse(data)

    # step 2 - loging in
    browser.select_form('form[name="pristupnaForma"]')
    browser["username"] = user_name
    browser["password"] = password
    resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/grider_w.php':
        browser.close()
        data = {'message': 'Neuspešno prijavljivanje, proverite username i password'}
        return JsonResponse(data)

    browser.select_form('form[action="maska4.php"]')
    resp = browser.submit_selected()

    form = browser.select_form('form[action="pn2nvt_1.php"]')
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(input_file.encode())
        temp_file.seek(0)
        form["ime_fajla"] = open(temp_file.name, "rb")
        resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/pn2nvt_1.php':
        browser.close()
        data = {'message': 'Fajl nije učitan na grider'}
        return JsonResponse(data)

    browser.select_form('form[action="pn2nvt_2.php"]')
    resp = browser.submit_selected()
    soup = BeautifulSoup(resp.text, 'lxml')
    text_output = soup.find("textarea", attrs={"name": "kor2"}).text
    if '***' in text_output:
        browser.close()
        data = {'message': text_output}
        return JsonResponse(data)

    browser.select_form('form[action="dload1.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao fajl sa listom'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_lista_file, resp.content)

    browser.close()
    os.remove(temp_file.name)
    data = {'message': 'ok'}
    return JsonResponse(data)



def grider_nvt2_trst(request):
    if request.method == 'POST':
        uploaded_file = request.POST.get("file")
        pk = request.POST.get("pk")
    browser = mechanicalsoup.StatefulBrowser()
    subject = get_object_or_404(Subject, pk=pk)
    user_name = subject.company.grider_login_name
    password = subject.company.grider_password
    if user_name == None or password == None:
        browser.close()
        data = {'message': 'Podaci za prijavljivanje nisu uneti ili su netačni'}
        return JsonResponse(data) 
    try:
        input_file = get_file_from_aws(f'autopilot-kancelarija-{subject.company.id}', f'{uploaded_file}')
        print(input_file)
    except:
        browser.close()
        data = {'message': 'Fajl nije pronađen na AWS-u'}
        return JsonResponse(data)
    dot_position = uploaded_file.find('.')
    output_txt_file = f'Predmet-{pk}/Grider/gk-trst.txt'
    output_pdf_file = f'Predmet-{pk}/Grider/gk-trst.pdf'
    output_lista_file = f'Predmet-{pk}/Grider/gk-trstlista.txt'
    real_headers = {
    "Host" : "grider.rgz.gov.rs",
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language" : "en-US,en;q=0.5",
    "Accept-Encoding" : "gzip, deflate, br",
    "Referer" : "https://google.com/",
    "DNT" : "1",
    "Connection" : "close",
    "Upgrade-Insecure-Requests" : "1",
    "Sec-Fetch-Dest" : "document",
    "Sec-Fetch-Mode" : "navigate",
    "Sec-Fetch-Site" : "cross-site",
    }
    browser.session.headers = real_headers
    try:
        # step 1 - openning portal
        browser.open("https://grider.rgz.gov.rs/login_lg.php?")
    except:
        browser.close()
        data = {'message': 'Grider server trenutno ne radi'}
        return JsonResponse(data)

    # step 2 - loging in
    browser.select_form('form[name="pristupnaForma"]')
    browser["username"] = user_name
    browser["password"] = password
    resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/grider_w.php':
        browser.close()
        data = {'message': 'Neuspešno prijavljivanje, proverite username i password'}
        return JsonResponse(data)

    browser.select_form('form[action="maska5.php"]')
    resp = browser.submit_selected()

    form = browser.select_form('form[action="nvt2pn_1.php"]')
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(input_file.encode())
        temp_file.seek(0)
        form["ime_fajla"] = open(temp_file.name, "rb")
        resp = browser.submit_selected()
    if browser.url != 'https://grider.rgz.gov.rs/nvt2pn_1.php':
        browser.close()
        data = {'message': 'Fajl nije učitan na grider'}
        return JsonResponse(data)

    browser.select_form('form[action="nvt2pn_2.php"]')
    resp = browser.submit_selected()
    soup = BeautifulSoup(resp.text, 'lxml')
    text_output = soup.find("textarea", attrs={"name": "kor2"}).text
    if '***' in text_output:
        browser.close()
        data = {'message': text_output}
        return JsonResponse(data)

    browser.select_form('form[action="dload1.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao fajl sa listom'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_lista_file, resp.content)

    browser.select_form('form[action="dload2.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao text fajl'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_txt_file, resp.content)

    browser.select_form('form[action="izlaz_pdf_p.php"]')
    resp = browser.submit_selected(update_state=False)
    if resp.status_code != 200:
        browser.close()
        data = {'message': 'Grider nije generisao pdf fajl'}
        return JsonResponse(data)
    upload_file_to_s3(f'autopilot-kancelarija-{subject.company.id}', output_pdf_file, resp.content)

    browser.close()
    os.remove(temp_file.name)
    data = {'message': 'ok'}
    return JsonResponse(data)


def add_comment(request, pk):
    if request.method == 'POST':
        form = AddCommentForm(request.POST or None)
        subject = get_object_or_404(Subject, pk=pk)
        if form.is_valid():
            new_comment = Comment.objects.create()
            new_comment.author = request.user
            new_comment.subject = subject
            new_comment.text = form.cleaned_data['text']
            new_comment.save()
        return redirect('main:subject', pk=pk)
    else:
        form = AddCommentForm()
        return render(request, 'main/add_comment.html', {'form': form})
    

def add_comment_to_db(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        subject = get_object_or_404(Subject, pk=pk)
        author = request.user
        comment = request.POST.get('comment')
        new_comment = Comment.objects.create()
        new_comment.author = author
        new_comment.subject = subject
        new_comment.text = comment
        new_comment.save()
        return JsonResponse({'message': 'ok'})
    

def add_template(request,pk):
    return render(request, 'main/add_template.html', {'pk': pk})


def gps_devices(request):
    company = request.user.company
    devices = GpsDevice.objects.filter(company=company)
    # print(devices)
    return render(request, 'main/gps_devices.html', {'devices': devices})


def add_gps_device(request):
    if request.method == 'POST':
        form = EditGpsDeviceForm(request.POST or None)
        company = request.user.company
        if form.is_valid():
            new_device = form.save(commit=False)
            new_device.company = company
            new_device.save()
            return redirect('main:gps-devices')
    else:
        form = EditGpsDeviceForm()
        return render(request, 'main/add_gps_device.html', {'form': form})
    

def edit_gps_device(request, id):
    instance = get_object_or_404(GpsDevice, pk=id)
    if request.method == 'POST':
        form = EditGpsDeviceForm(request.POST or None, instance=instance)
        if form.is_valid():
            device = form.save(commit=False)
            device.company = request.user.company
            device.save()
            return redirect('main:gps-devices')
    else:
        form = EditGpsDeviceForm(instance=instance)
        return render(request, 'main/add_gps_device.html', {'form': form})
    

# upload root file
def upload_file_to_bucket(request):
    s3 = boto3.client('s3')
    companyId = request.user.company.id
    if request.method == 'POST':
        uploaded_file = request.FILES["file"]
        id = request.POST.get("pk")
        # AWS S3 bucket details
        bucket_name = f"autopilot-kancelarija-{companyId}"
        key = f"Predmet-{id}/{uploaded_file}"

        # Upload the file to AWS S3from botocore.exceptions import ClientError
        s3.upload_fileobj(uploaded_file, bucket_name, key)
        return JsonResponse({'ok': 'ok'})
    else:
        return JsonResponse({'error': 'File name not provided'}, status=400)


# upload elaborat root file
def upload_elaborat_root_file(request):
    s3 = boto3.client('s3')
    companyId = request.user.company.id
    if request.method == 'POST':
        uploaded_file = request.FILES["file"]
        id = request.POST.get("pk")
        link_name = request.POST.get("linkName")
        print(uploaded_file, id, link_name)
        # AWS S3 bucket details
        bucket_name = f"autopilot-kancelarija-{companyId}"
        key = link_name

        # Upload the file to AWS S3from botocore.exceptions import ClientError
        s3.upload_fileobj(uploaded_file, bucket_name, key)
        return JsonResponse({'ok': 'ok'})
    else:
        return JsonResponse({'error': 'File name not provided'}, status=400)


def upload_pdf_to_subject(request):
    s3 = boto3.client('s3')
    companyId = request.user.company.id
    if request.method == 'POST':
        uploaded_file = request.FILES["pdf"]
        id = request.POST.get("subjectID")
        templateId = request.POST.get("elaboratID")
        faktura = request.POST.get("faktura")
        if faktura:
            aws_name = 'faktura.pdf'
        else:
            template = ElaboratDocument.objects.get(template_number=templateId)
            aws_name = template.aws_name
        # AWS S3 bucket details
        bucket_name = f"autopilot-kancelarija-{companyId}"
        key = f"Predmet-{id}/{aws_name}"
        # Upload the file to AWS S3from botocore.exceptions import ClientError
        s3.upload_fileobj(uploaded_file, bucket_name, key)
        return JsonResponse({'ok': 'ok'})
    else:
        return JsonResponse({'error': 'File name not provided'}, status=400)
    

def upload_grider_file_to_bucket(request):
    s3 = boto3.client('s3')
    companyId = request.user.company.id
    if request.method == 'POST':            
        uploaded_file = request.FILES["file"]
        id = request.POST.get("pk")
        # AWS S3 bucket details
        try:
            s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{id}/Grider/')
            print('folder Grider exists')
        except ClientError as e:
            create_empty_folder(f"autopilot-kancelarija-{companyId}", f'Predmet-{id}/Grider')
        bucket_name = f"autopilot-kancelarija-{companyId}"
        key = f"Predmet-{id}/Grider/ulaz.txt"

        # Upload the file to AWS S3
        s3.upload_fileobj(uploaded_file, bucket_name, key)
    
        return JsonResponse({'ok': 'ok'})
    else:
        return JsonResponse({'error': 'File name not provided'}, status=400)
    

def e_salter(request, pk):
    return render(request, 'main/e_salter.html', {"pk":pk})


def cad(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    files = read_files_in_folder(f'autopilot-kancelarija-{subject.company.id}', f'Predmet-{pk}/CAD')
    return render(request, 'main/cad.html', {'subject': subject, 'files': files})


def grider(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    files = read_files_in_folder(f'autopilot-kancelarija-{subject.company.id}', f'Predmet-{pk}/Grider')
    return render(request, 'main/grider.html', {'subject': subject, 'files': files})


def upload_grider_osr_file_to_bucket(request):
    s3 = boto3.client('s3')
    companyId = request.user.company.id
    if request.method == 'POST':
        uploaded_file = request.FILES["file"]
        id = request.POST.get("pk")
        # AWS S3 bucket details
        bucket_name = f"autopilot-kancelarija-{companyId}"
        key = f"Predmet-{id}/Grider/ulaz-osr.txt"

        # Upload the file to AWS S3
        s3.upload_fileobj(uploaded_file, bucket_name, key)
    
        return JsonResponse({'ok': 'ok'})
    else:
        return JsonResponse({'error': 'File name not provided'}, status=400)
    

def upload_grider_osr_pdf_to_bucket(request):
    s3 = boto3.client('s3')
    companyId = request.user.company.id
    if request.method == 'POST':
        uploaded_file = request.FILES["pdf"]
        id = request.POST.get("pk")
        # AWS S3 bucket details
        bucket_name = f"autopilot-kancelarija-{companyId}"
        key = f"Predmet-{id}/Grider/ulaz-osr.pdf"
        # Upload the file to AWS S3
        s3.upload_fileobj(uploaded_file, bucket_name, key)
    
        return JsonResponse({'ok': 'ok'})
    else:
        return JsonResponse({'error': 'File name not provided'}, status=400)
    

def delete_grider_file(request):
    companyId = request.user.company.id
    if request.method == "POST":
        data = request.POST.get("data")
        bucket_name = f"autopilot-kancelarija-{companyId}"
        delete_object(bucket_name, data)
        response_data = {"message": "Data received and processed"}
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "Invalid request method"})


def elaborat(request, pk, end=None):
    s3 = boto3.client('s3')
    companyId = request.user.company.id
    subject = get_object_or_404(Subject, pk=pk)
    try:
        # check if folder Elaborati exists
        s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{subject.id}/Elaborati/')
    except ClientError as e:
        # create folders
        create_empty_folder(f"autopilot-kancelarija-{companyId}", f'Predmet-{subject.id}/Elaborati')
        create_empty_folder(f"autopilot-kancelarija-{companyId}", f'Predmet-{subject.id}/Elaborati/Elaborat1')
    # check if elaborat for subject exists
    if Elaborat.objects.filter(subject=subject):
        print('ima elaborat')
    # get elaborat documents for subject type
    docs = ElaboratType.objects.filter(type=subject.service_type).all()
    # get subject elaborat
    elaborat = Elaborat.objects.get(subject=subject, name="Elaborat1")
    # get documents for subject elaborat
    dokumenti = elaborat.elaboratsubjectdocument_set.all().order_by('order')
    try:
        elaborat_pdf = read_files_in_folder(f'autopilot-kancelarija-{subject.company.id}', f'Predmet-{pk}/Elaborati/Elaborat1/elaborat.pdf')
        print(f'elaborat on aws {elaborat_pdf}')
    except:
        print('nema elaborat')
    # root documents
    root_docs = [doc for doc in dokumenti if doc.document.root]
    print('root', root_docs)
    root_docs_done = []
    if root_docs:
        for rd in root_docs:
            try:
                s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{subject.id}/{rd.document.aws_name}')
                root_docs_done.append(rd)
                print('root docs done', root_docs_done)
            except:
                pass
    # cad dokumenti
    cad_docs = [doc for doc in dokumenti if doc.document.cad]
    cad_docs_done = []
    if cad_docs:
        for cd in cad_docs:
            try:
                s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{subject.id}/CAD/{cd.document.aws_name}')
                cad_docs_done.append(cd)
                print('cad docs done', cad_docs_done)
            except:
                pass

    # grider dokumenti
    grider_docs = [doc for doc in dokumenti if doc.document.grider]
    grider_docs_done = []
    if grider_docs:
        for gd in grider_docs:
            try:
                s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{subject.id}/Grider/{gd.document.aws_name}')
                #print(gd.document.aws_name)
                grider_docs_done.append(gd)
            except:
                pass

    licenced_worker = subject.responsible_worker
    if dokumenti:
        for dok in dokumenti:
            try:
                s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{subject.id}/Elaborati/Elaborat1/{dok.document.aws_name}')
                dok.uploaded = True
                dok.save()
            except:
                pass
        try:
            s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{pk}/Elaborati/Elaborat1/APR-resenje.pdf')
        except:
            s3.copy_object(Bucket=f"autopilot-kancelarija-{companyId}", CopySource=f"autopilot-kancelarija-{companyId}/OpstiDokumenti/APR-resenje.pdf", Key=f'Predmet-{subject.id}/Elaborati/Elaborat1/APR-resenje.pdf')
        try:
            s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{pk}/Elaborati/Elaborat1/RGZ-resenje.pdf')
        except:
            s3.copy_object(Bucket=f"autopilot-kancelarija-{companyId}", CopySource=f"autopilot-kancelarija-{companyId}/OpstiDokumenti/RGZ-resenje.pdf", Key=f'Predmet-{subject.id}/Elaborati/Elaborat1/RGZ-resenje.pdf')
        try:
            s3.head_object(Bucket=f"autopilot-kancelarija-{companyId}", Key=f'Predmet-{pk}/Elaborati/Elaborat1/licenca.pdf')
        except:
            s3.copy_object(Bucket=f"autopilot-kancelarija-{companyId}", CopySource=f"autopilot-kancelarija-{companyId}/zaposleni-{licenced_worker.id}/licenca.pdf", Key=f'Predmet-{subject.id}/Elaborati/Elaborat1/licenca.pdf')
        if end is not None:
            return render(request, 'main/elaborat.html', {'subject': subject,
                                                        'dokumenti': dokumenti,
                                                        'root_docs_done': root_docs_done,
                                                        'grider_docs_done': grider_docs_done,
                                                        'cad_docs_done': cad_docs_done,
                                                        'elaborat_pdf': elaborat_pdf,
                                                        'end': end })
        else:        
            return render(request, 'main/elaborat.html', {'subject': subject,
                                                        'dokumenti': dokumenti,
                                                        'root_docs_done': root_docs_done,
                                                        'grider_docs_done': grider_docs_done,
                                                        'cad_docs_done': cad_docs_done,
                                                        'elaborat_pdf': elaborat_pdf })
    else:
        for doc in docs:
            new_esd = ElaboratSubjectDocument.objects.create()
            new_esd.elaborat = elaborat
            new_esd.document = doc.document
            new_esd.order = doc.order
            new_esd.save()
        grider_docs_done = []
        cad_docs_done = []
        dokumenti = elaborat.elaboratsubjectdocument_set.all().order_by('order')
    return render(request, 'main/elaborat.html', {'subject': subject,
                                                'dokumenti': dokumenti,
                                                'root_docs_done': root_docs_done,
                                                'grider_docs_done': grider_docs_done,
                                                'cad_docs_done': cad_docs_done })


def pdf_editor(request, pk, aws, folder, assemble=None):
    if assemble is not None:
        subject = get_object_or_404(Subject, pk=pk)
        company_id = subject.company.id
        return render(request, 'main/pdf-editor.html', {'pk': pk, 'aws': aws, 'company_id': company_id, 'subject': subject, 'folder': folder, 'assemble': assemble})
    else:
        subject = get_object_or_404(Subject, pk=pk)
        company_id = subject.company.id
        return render(request, 'main/pdf-editor.html', {'pk': pk, 'aws': aws, 'company_id': company_id, 'subject': subject, 'folder': folder})


def upload_elaborat_document(request):
    if request.method == 'POST':
        s3 = boto3.client('s3')
        elaboratID = request.POST.get("elaboratID")     
        subjectID = request.POST.get("subjectID")
        pdf = request.FILES["pdf"]

        subject = get_object_or_404(Subject, pk=subjectID)
        elaborat = ElaboratDocument.objects.get(template_number=elaboratID)

        bucket_name = f"autopilot-kancelarija-{subject.company.id}"
        key = f"Predmet-{subjectID}/Elaborati/Elaborat1/{elaborat.aws_name}"

        # Upload the file to AWS S3
        s3.upload_fileobj(pdf, bucket_name, key)
        return JsonResponse({"ok": "uploaded"})
    

def upload_grider_elaborat_document(request):
    if request.method == 'POST':
    
        subjectID = request.POST.get("subjectID")
        aws_name = request.POST.get("aws_name")
        pdf = request.FILES["file"]

        subject = get_object_or_404(Subject, pk=subjectID)
        elaborat = Elaborat.objects.get(subject=subject)

        print(elaborat.id, subjectID, pdf, aws_name)


        s3 = boto3.client('s3')


        bucket_name = f"autopilot-kancelarija-{subject.company.id}"
        key = f"Predmet-{subjectID}/Elaborati/Elaborat1/{aws_name}"

        # Upload the file to AWS S3
        s3.upload_fileobj(pdf, bucket_name, key)
        return JsonResponse({"ok": "uploaded"})


def upload_cad_file_aws(request):
    if request.method == 'POST':

        pdf = request.FILES["file"]
        pk = request.POST.get("pk")
        file_name = request.POST.get("fileName")

        subject = get_object_or_404(Subject, pk=pk)

        print(pdf, pk, file_name)

        s3 = boto3.client('s3')
        bucket_name = f"autopilot-kancelarija-{subject.company.id}"
        key = f"Predmet-{subject.id}/CAD/{file_name}.pdf"

        # Upload the file to AWS S3
        s3.upload_fileobj(pdf, bucket_name, key)

        return JsonResponse({'ok': 'uploaded'})
    

def upload_completed_elaborat(request):
    if request.method == 'POST':

        pdf = request.FILES["file"]
        pk = request.POST.get("pk")

        subject = get_object_or_404(Subject, pk=pk)

        print(pdf, pk)

        s3 = boto3.client('s3')
        bucket_name = f"autopilot-kancelarija-{subject.company.id}"
        key = f"Predmet-{subject.id}/Elaborati/Elaborat1/elaborat.pdf"

        # Upload the file to AWS S3
        s3.upload_fileobj(pdf, bucket_name, key)

        return JsonResponse({'ok': 'uploaded'})


def reset_elaborat(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    s3 = boto3.client('s3')
    try:
        objects = s3.list_objects_v2(Bucket=f'autopilot-kancelarija-{subject.company.id}', Prefix=f'Predmet-{subject.id}/Elaborati/')
        for obj in objects.get('Contents', []):
            s3.delete_object(Bucket=f'autopilot-kancelarija-{subject.company.id}', Key=obj['Key'])
        s3.delete_object(Bucket=f'autopilot-kancelarija-{subject.company.id}', Key=f'Predmet-{subject.id}/Elaborati/')
    except:
        print('folder not found')
    elaborat = get_object_or_404(Elaborat, subject=subject)
    elaborat_docs = ElaboratSubjectDocument.objects.filter(elaborat=elaborat)
    for doc in elaborat_docs:
        if doc.document.name != 'APR-rešenje' and doc.document.name != 'RGZ-rešenje' and doc.document.name != 'Geodetska licenca':
            doc.uploaded = False
            doc.save()
    return redirect('main:elaborat', pk=pk)


def elaborat_full_preview(request):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        subject = get_object_or_404(Subject, pk=pk)
        print(subject)
        s3 = boto3.client('s3')
        try:
            s3_file = s3.get_object(Bucket=f'autopilot-kancelarija-{subject.company.id}', Key=f'Predmet-{subject.id}/Elaborati/Elaborat1/elaborat.pdf')
        except Exception as e:
            return HttpResponseNotFound("File doesn't exist")
        
        # Wrap the BytesIO object with FileResponse to serve the PDF
        return FileResponse(io.BytesIO(s3_file['Body'].read()), content_type='application/pdf')


def edit_elaborat(request):
    if request.method == 'POST':
        pdf = request.FILES["pdf"]
        elaboratID = request.POST.get("elaboratID")
        subjectID = request.POST.get("subjectID")
        assemble = request.POST.get("assemble")
        subject = get_object_or_404(Subject, pk=subjectID)
        elaborat = Elaborat.objects.get(subject=subject)
        elaborat_document = ElaboratSubjectDocument.objects.get(elaborat=elaborat, order=assemble)
        len = ElaboratSubjectDocument.objects.filter(elaborat=elaborat).all().count()
        print(elaborat_document.document.aws_name)
        print(elaborat_document.uploaded)
        print('duzina liste', len)
        elaborat_document.uploaded = True
        elaborat_document.save()
        #send to aws
        s3 = boto3.client('s3')
        bucket_name = f"autopilot-kancelarija-{subject.company.id}"
        key = f"Predmet-{subject.id}/Elaborati/Elaborat1/{elaborat_document.document.aws_name}"
        s3.upload_fileobj(pdf, bucket_name, key)
        #find next document
        next_assemble = int(assemble) + 1
        if next_assemble > len:
            data = {
                'end': 'true'
            }
            return JsonResponse(data)
        next_document = ElaboratSubjectDocument.objects.get(elaborat=elaborat, order=next_assemble)


        if next_document.document.name == 'APR-rešenje':
            next_assemble += 1
            next_document = ElaboratSubjectDocument.objects.get(elaborat=elaborat, order=next_assemble)

        if next_document.document.name == 'RGZ-rešenje':
            next_assemble += 1
            next_document = ElaboratSubjectDocument.objects.get(elaborat=elaborat, order=next_assemble)

        if next_document.document.name == 'Geodetska licenca':
            next_assemble += 1
            next_document = ElaboratSubjectDocument.objects.get(elaborat=elaborat, order=next_assemble)

        if next_document.document.cad:
            folder = 'CAD'
        elif next_document.document.grider:
            folder = 'Grider'
        elif next_document.document.root:
            folder = 'Root'
        if next_document.document.template_number:
            data = {
                'pk': subjectID,
                'template_number': next_document.document.template_number,
                'assemble': next_assemble
            }
        elif next_document.document.grider or next_document.document.cad:
            data = {
                'pk': subjectID,
                'aws_name': next_document.document.aws_name,
                'folder': folder,
                'assemble': next_assemble
            }
        return JsonResponse(data)