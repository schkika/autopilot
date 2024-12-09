from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import boto3
from botocore.exceptions import ClientError
from autopilothome.aws_utils import create_empty_folder, read_files_in_folder
from .forms import LoginForm, SelfEditUserForm
from django.contrib.auth import views as auth_views
from .forms import (RegisterForm,
                    RegisterUserForm,
                    EditCompanyForm,
                    EditUserForm,
                    RegisterAssosiateForm,
                    EditAssosiateForm,
                    RegisterClientForm,
                    EditClientForm,
                    SelfEditClientForm,
                    ChooseClientForm)
from .models import Company, CustomUser, Assosiate, Client
from main.models import Subject
from autopilothome.decorators import (
                                        only_administrators,
                                        work_with_users,
                                        work_with_assosiates,
                                        work_with_clients
                                    )
from django.contrib.auth.decorators import login_required


def register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect("home")
    return render(request, 'accounts/register.html', { "form": form })


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'


@login_required
@work_with_users()
def register_user(request):
    form = RegisterUserForm()
    if request.method == "POST":
        form = RegisterUserForm(request.POST or None)
        if form.is_valid():
            new_user = CustomUser.objects.create()
            new_user.first_name = form.data['first_name']
            new_user.last_name = form.data['last_name']
            new_user.email = form.data['email']
            new_user.type = 'employee'
            new_user.can_open_subject = form.cleaned_data['can_open_subject']
            new_user.can_add_user = form.cleaned_data['can_add_user']
            new_user.can_add_assosiate = form.cleaned_data['can_add_assosiate']
            new_user.can_add_client = form.cleaned_data['can_add_client']
            new_user.set_password('privremena')
            new_user.company = request.user.company
            new_user.save()
            bucket = f'autopilot-kancelarija-{new_user.company.id}'
            folder = f'zaposleni-{new_user.id}'
            create_empty_folder(bucket, folder)
            s3 = boto3.client('s3')
            source_key = f'OpstiDokumenti/profile.png'
            s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': source_key}, Key=f'{folder}/profile.png')
            return redirect("main:users")
    return render(request, 'accounts/register_user.html', { "form": form })


@login_required
@work_with_assosiates()
def register_assosiate(request):
    form = RegisterAssosiateForm()
    if request.method == "POST":
        form = RegisterAssosiateForm(request.POST or None)
        if form.is_valid():
            if check_if_user_exist(form):
                message = 'Korisnik sa ovim email-om vec registrovan'
                return render(request, 'accounts/register_assosiate.html', { 'form': form, 'message': message })
            new_user = CustomUser.objects.create()
            new_user.email = form.data['email']
            new_user.set_password('privremena')
            new_user.type = 'assosiate'
            new_user.can_add_client = True
            new_user.save()
            new_assosiate = Assosiate.objects.create()
            new_assosiate.first_name = form.data['first_name']
            new_assosiate.last_name = form.data['last_name']
            new_assosiate.email = form.data['email']
            new_assosiate.profession = form.data['profession']
            new_assosiate.company.add(request.user.company)
            new_assosiate.user = new_user
            new_assosiate.save()
            return redirect("main:assosiates")
    return render(request, 'accounts/register_assosiate.html', { "form": form })


# User creation
def check_if_client_exist(form):
    if Client.objects.filter(first_name=form.data['first_name'],
                            last_name=form.data['last_name'],
                            contact=form.data['contact']):
        return True
    else:
        return False
    

# User creation
def check_if_user_exist(form):
    if CustomUser.objects.filter(email=form.data['email']):
        return True
    else:
        return False


@login_required
@work_with_clients()
def register_client(request):
    form = RegisterClientForm()
    if request.method == "POST":
        form = RegisterClientForm(request.POST or None)
        print(form.data['email'])
        if form.is_valid():
            if check_if_client_exist(form):
                message = 'Stranka sa ovim imenom, prezimenom i kontaktom je vec registrovana'
                return render(request, 'accounts/register_client.html', { 'form': form, 'message': message })
            if check_if_user_exist(form):
                message = 'Korisnik sa ovim email-om vec registrovan'
                return render(request, 'accounts/register_client.html', { 'form': form, 'message': message })
            new_client = Client.objects.create()
            new_client.first_name = form.data['first_name']
            new_client.last_name = form.data['last_name']
            new_client.city = form.data['city']
            new_client.address = form.data['address']
            new_client.contact = form.data['contact']
            new_client.email = form.data['email']
            if new_client.email != '':
                new_user = CustomUser.objects.create()
                new_user.email = new_client.email
                new_user.set_password('privremena')
                new_user.type = 'client'
                new_user.save()
                new_client.user = new_user
                new_client.save()
                new_client.company.add(request.user.company)
                return redirect("main:clients")
            new_client.save()
            new_client.company.add(request.user.company)
            return redirect("main:clients")
    return render(request, 'accounts/register_client.html', { "form": form })


@login_required
@work_with_clients()
def register_subject_client(request, pk):
    form = RegisterClientForm()
    if request.method == "POST":
        form = RegisterClientForm(request.POST or None)
        if form.is_valid():
            if check_if_client_exist(form):
                message = 'Stranka sa ovim imenom, prezimenom i kontaktom je vec registrovana'
                return render(request, 'accounts/register_client.html', { 'form': form, 'message': message })
            subject = get_object_or_404(Subject, pk=pk)
            new_client = Client.objects.create()
            new_client.first_name = form.data['first_name']
            new_client.last_name = form.data['last_name']
            new_client.city = form.data['city']
            new_client.address = form.data['address']
            new_client.contact = form.data['contact']
            new_client.email = form.data['email']
            new_client.company.add(request.user.company)
            new_client.save()
            subject.clients.add(new_client)
            return redirect("main:edit-subject" , pk=pk)
    return render(request, 'accounts/register_client.html', { "form": form })


@login_required
def self_edit_client(request, pk):
    if not hasattr(request.user, 'client') or request.user.client.id != pk:
        return HttpResponse("Vi nemate ovlaštenje da pristupite ovoj strani!")
    instance = get_object_or_404(Client, pk=pk)
    old_mail = instance.email
    if request.method == "POST":
        form = SelfEditClientForm(request.POST or None, instance=instance)
        if form.is_valid():
            if Client.objects.filter(first_name=form.data['first_name'],
                                         last_name=form.data['last_name'],
                                         city=form.data['city'],
                                         address=form.data['address'],
                                         contact=form.data['contact']).exclude(pk=pk):
                    message = 'Stranka sa ovim podacima vec registrovana'
                    return render(request, 'accounts/edit_client.html', { 'form': form, 'message': message })
            if old_mail != form.data['email']:
                if CustomUser.objects.filter(email=form.data['email']).first():
                    message = 'Korisnik sa ovim email-om vec registrovan'
                    return render(request, 'accounts/edit_client.html', { 'form': form, 'message': message })
            user = CustomUser.objects.filter(email=old_mail).first()
            user.email = form.data['email']
            user.save()
            form.save()
            return redirect("main:index")
    else:
        form = SelfEditClientForm(instance=instance)
    return render(request, 'accounts/edit_client.html', { "form": form })


@login_required
def edit_assosiate(request, pk):
    if not hasattr(request.user, 'assosiate') or request.user.assosiate.id != pk:
        return HttpResponse("Vi nemate ovlaštenje da pristupite ovoj strani!")
    instance = get_object_or_404(Assosiate, pk=pk)
    old_email = instance.email
    if request.method == "POST":
        form = EditAssosiateForm(request.POST, instance=instance)
        if form.is_valid():
            if Assosiate.objects.filter(first_name=form.data['first_name'],
                                       last_name=form.data['last_name'],
                                       profession=form.data['profession']).exclude(pk=pk):
                message = 'Saradnik sa ovim imenom, prezimenom i profesijom vec registrovan'
                return render(request, 'accounts/edit_assosiate.html', { 'form': form, 'message': message })
            if form.data['email'] != old_email:
                if CustomUser.objects.filter(email=form.data['email']).first():
                    message = 'Korisnik sa ovim email-om vec registrovan'
                    return render(request, 'accounts/edit_assosiate.html', { 'form': form, 'message': message })
            user = CustomUser.objects.filter(email=old_email).first()
            user.email = form.data['email']
            user.save()
            form.save()
            return redirect("main:index")
    else:
        form = EditAssosiateForm(instance=instance)
    return render(request, 'accounts/edit_assosiate.html', { 'form': form })


@login_required
@work_with_clients()
def edit_client(request, pk):
    instance = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = RegisterClientForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            print(form.data['email'])
            return redirect("main:clients")
    else:
        form = EditClientForm(instance=instance)
    return render(request, 'accounts/edit_client.html', { "form": form })


@login_required
@work_with_clients()
def edit_subject_client(request, cpk, pk):
    instance = get_object_or_404(Client, pk=cpk)
    old_name = instance.name
    old_contact = instance.contact
    if request.method == "POST":
        form = RegisterClientForm(request.POST or None, instance=instance)
        if form.is_valid():
            if old_name == form.data['name'] and old_contact == form.data['contact']:
                form.save()
                return redirect("main:edit-subject", pk=pk)
            existing_clients = Client.objects.filter(name=form.data['name'])
            if existing_clients:
                for client in existing_clients:
                    if client.contact == form.data['contact']:
                        message = 'Stranka postoji u bazi'
                        return render(request, 'accounts/edit_client.html', { 'form': form, 'message': message })
            form.save()
            return redirect("main:edit-subject", pk=pk)
    else:
        form = EditClientForm(instance=instance)
    return render(request, 'accounts/edit_client.html', { "form": form })


@login_required
@work_with_clients()
def choose_client(request, pk):
    instance = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        form = ChooseClientForm(request.POST or None, instance=instance, current_user=request.user)
        if form.is_valid():
            print(form.cleaned_data['clients'])
            form.save()
            return redirect("main:edit-subject", pk=pk)
    else:
        form = ChooseClientForm(instance=instance, current_user=request.user)
    return render(request, 'accounts/choose_client.html', { 'form': form })


@login_required
@only_administrators()
def edit_company(request):
    pk = request.user.company.id
    instance = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        form = EditCompanyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("main:index")
    else:
        form = EditCompanyForm(instance=instance)
    return render(request, 'accounts/edit_company.html', { 'form': form })


@login_required
@work_with_users()
def edit_user(request, pk):
    instance = get_object_or_404(CustomUser, pk=pk)
    # check if request user and instance has same company
    if request.user.company != instance.company:
        return HttpResponse("Vi nemate ovlaštenje da pristupite ovoj strani!")
    old_email = instance.email
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=instance)
        if form.is_valid():
            if form.data['email'] != old_email:
                if CustomUser.objects.filter(email=form.data['email']):
                    message = 'Email postoji'
                    return render(request, 'accounts/edit_user.html', { 'form': form, 'message': message })
            form.save()
            return redirect("main:users")
    else:
        form = EditUserForm(instance=instance)
    return render(request, 'accounts/edit_user.html', { 'form': form, 'instance': instance })


@login_required
def self_edit_user(request, pk):
    instance = get_object_or_404(CustomUser, pk=pk)
    # check if request user and instance has same company
    if request.user.company != instance.company:
        return HttpResponse("Vi nemate ovlaštenje da pristupite ovoj strani!")
    old_email = instance.email
    if request.method == "POST":
        form = SelfEditUserForm(request.POST, instance=instance)
        if form.is_valid():
            if form.data['email'] != old_email:
                if CustomUser.objects.filter(email=form.data['email']):
                    message = 'Email postoji'
                    return render(request, 'accounts/self_edit_user.html', { 'form': form, 'message': message })
            form.save()
            return redirect("main:index")
    else:
        form = SelfEditUserForm(instance=instance)
    return render(request, 'accounts/self_edit_user.html', { 'form': form, 'instance': instance })


@login_required
def add_user_files_aws(request, pk):
    instance = get_object_or_404(CustomUser, pk=pk)
    if request.user.company != instance.company:
        return HttpResponse("Vi nemate ovlaštenje da pristupite ovoj strani!")
    if request.method == 'POST':
        s3 = boto3.client('s3')
        uploaded_file = request.FILES["file"]
        id = request.POST.get("pk")
        file_name = request.POST.get("fileName")
        # AWS S3 bucket details
        try:
            s3.head_object(Bucket=f"autopilot-kancelarija-{instance.company.id}", Key=f'zaposleni-{instance.id}/')
            print('user folder exists')
        except ClientError as e:
            create_empty_folder(f"autopilot-kancelarija-{instance.company.id}", f'zaposleni-{instance.id}')
        bucket_name = f"autopilot-kancelarija-{instance.company.id}"
        if uploaded_file.name.endswith('pdf'):
            key = f"zaposleni-{instance.id}/{file_name}.pdf"
        if uploaded_file.name.endswith('png'):
            key = f"zaposleni-{instance.id}/{file_name}.png"

        # Upload the file to AWS S3
        s3.upload_fileobj(uploaded_file, bucket_name, key)
        return JsonResponse({'ok': 'ok'})
    files = read_files_in_folder(f'autopilot-kancelarija-{instance.company.id}', f'zaposleni-{instance.id}')
    return render(request, 'accounts/add_user_files_aws.html', {'files': files})


@login_required
def add_company_files_aws(request, pk):
    instance = get_object_or_404(Company, pk=pk)
    if request.user.company != instance:
        return HttpResponse("Vi nemate ovlaštenje da pristupite ovoj strani!")
    if request.method == 'POST':
        s3 = boto3.client('s3')
        uploaded_file = request.FILES["file"]
        file_name = request.POST.get("fileName")
        # AWS S3 bucket details
        try:
            s3.head_object(Bucket=f"autopilot-kancelarija-{instance.id}", Key='OpstiDokumenti/')
        except ClientError as e:
            create_empty_folder(f"autopilot-kancelarija-{instance.id}", 'OpstiDokumenti')
        bucket_name = f"autopilot-kancelarija-{instance.id}"
        if uploaded_file.name.endswith('pdf'):
            key = f"OpstiDokumenti/{file_name}.pdf"
        if uploaded_file.name.endswith('png'):
            key = f"OpstiDokumenti/{file_name}.png"

        # Upload the file to AWS S3
        s3.upload_fileobj(uploaded_file, bucket_name, key)
    files = read_files_in_folder(f'autopilot-kancelarija-{instance.id}', f'OpstiDokumenti')
    return render(request, 'accounts/add_company_files_aws.html', {'files': files})


def profile_image(request):
    user = request.user
    bucket = f'autopilot-kancelarija-{user.company.id}'
    s3_object_key = f'zaposleni-{user.id}/profile.png'  # Replace with your object key
    s3 = boto3.client('s3', region_name='eu-central-1')
    signed_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket,
            'Key': s3_object_key
        }
    )
    # Redirect to the signed URL
    return HttpResponseRedirect(signed_url)


def profile_images(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    bucket = f'autopilot-kancelarija-{user.company.id}'
    s3_object_key = f'zaposleni-{user.id}/profile.png'  # Replace with your object key
    s3 = boto3.client('s3', region_name='eu-central-1')
    signed_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket,
            'Key': s3_object_key
        }
    )
    # Redirect to the signed URL
    return HttpResponseRedirect(signed_url)


def upload_profile_picture(request):
    if request.method == 'POST':
        uploaded_file = request.FILES["file"]
        user_id = request.POST.get("id")
        user = get_object_or_404(CustomUser, pk=user_id)
        s3 = boto3.client('s3')
        s3.put_object(Body=uploaded_file, Bucket=f'autopilot-kancelarija-{user.company.id}', Key=f'zaposleni-{user.id}/profile.png')
        return JsonResponse({'ok': 'ok'})