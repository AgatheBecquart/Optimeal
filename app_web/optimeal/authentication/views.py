from django.conf import settings
import logging
from django.shortcuts import redirect, render
import requests
from django.contrib import messages
from .forms import SignUpEmployeeForm, UpdateEmployeeForm, LoginEmployeeForm

# URL pour obtenir un token
TOKEN_URL = 'http://optimeal-data.switzerlandnorth.azurecontainer.io:8000/auth/token'
EMPLOYEES_URL = 'http://optimeal-data.switzerlandnorth.azurecontainer.io:8000/employees'

def generate_employee_unique_id(first_name, last_name):
    # Générez l'ID unique à partir du nom et prénom
    last_name_part = last_name[:3].upper()
    first_name_part = first_name[:2].upper()
    return f"LI{last_name_part}{first_name_part}"

logger = logging.getLogger(__name__)

def get_access_token(username, password):
    logger.info("Demande de token pour l'utilisateur %s", username)
    try:
        auth_data = {
            'username': username,
            'password': password,
            'client_id': 'votre_client_id',
            'client_secret': 'votre_client_secret',
            'scope': 'votre_scope',
            'grant_type': 'password'
        }
        response = requests.post(TOKEN_URL, data=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            logger.error("Échec lors de l'obtention du token : %s - %s", response.status_code, response.text)
            raise Exception(f"Erreur d'authentification : {response.status_code} - {response.text}")
    except Exception as e:
        logger.error("Exception lors de la récupération du token : %s", e)
        raise

logger = logging.getLogger(__name__)

def login_view(request):
    logger.info("Accès à la vue de connexion")
    if request.method == 'POST':
        form = LoginEmployeeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            logger.info("Tentative de connexion pour l'utilisateur : %s", username)
            
            # Print les données envoyées à l'API
            print(f"Sending username: {username}, password: {password} to API")

            # Faire une requête POST à votre API FastAPI pour l'authentification
            try:
                response = requests.post(
                    TOKEN_URL,  # Remplacez par l'URL de votre API
                    data={'username': username, 'password': password},
                    timeout=10  # Optionnel: pour gérer les délais d'attente
                )
                
                # Print les détails de la réponse de l'API
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.content}")

                if response.status_code == 200:
            

                    # Supposons que l'API renvoie un token d'accès
                    data = response.json()
                    access_token = data.get('access_token')
                    
                    # Stocker le token dans la session
                    request.session['access_token'] = access_token
                    
                    logger.info("Utilisateur %s connecté avec succès via API", username)
                    print(f"Response status good")
                    return redirect('home')  # Redirection après connexion réussie
                else:
                    logger.warning("Échec de l'authentification via API pour l'utilisateur : %s", username)
                    messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            
            except requests.RequestException as e:
                print(f"RequestException occurred: {e}")
                logger.error("Erreur lors de la connexion via API pour l'utilisateur %s : %s", username, e)
                messages.error(request, 'Erreur de connexion. Veuillez réessayer plus tard.')

        else:
            messages.error(request, 'Le formulaire contient des erreurs.')
    else:
        form = LoginEmployeeForm()
    
    return render(request, 'authentication/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpEmployeeForm(request.POST)
        if form.is_valid():
            # Générer l'ID unique
            first_name = form.cleaned_data['employee_first_name']
            last_name = form.cleaned_data['employee_last_name']
            employee_unique_id = generate_employee_unique_id(first_name, last_name)

            try:
                # Obtenir le token d'accès
                access_token = get_access_token('camille', 'maison')  # Ou utilisez un formulaire pour capturer ces informations

                # Créer un employé via l'API
                new_user_employee = {
                    "employee_unique_id": employee_unique_id,
                    "employee_username": form.cleaned_data['employee_username'],
                    "employee_password": form.cleaned_data['employee_password'],
                    "employee_email": form.cleaned_data['employee_email'],
                    "employee_first_name": form.cleaned_data['employee_first_name'],
                    "employee_last_name": form.cleaned_data['employee_last_name'],
                    "employee_zip_code_prefix": form.cleaned_data['employee_zip_code_prefix'],
                    "employee_city": form.cleaned_data['employee_city'],
                    "employee_state": form.cleaned_data['employee_state']
                }
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                api_response = requests.post(EMPLOYEES_URL, json=new_user_employee, headers=headers)

                if api_response.status_code == 200:
                    messages.success(request, 'Employé créé avec succès !')
                else:
                    messages.error(request, f"Erreur lors de la création de l'employé: {api_response.status_code}, {api_response.text}")
                return redirect('home')  # Rediriger vers une page d'accueil ou autre

            except Exception as e:
                messages.error(request, str(e))

        else:
            messages.error(request, 'Le formulaire contient des erreurs.')
    else:
        form = SignUpEmployeeForm()
    return render(request, 'authentication/signup.html', {'form': form})


def get_employee_details(employee_id):
    try:
        access_token = get_access_token('camille', 'maison')  # Utiliser les informations de connexion appropriées à revoir
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        employee_response = requests.get(f"{EMPLOYEES_URL}/{employee_id}/", headers=headers)
        if employee_response.status_code == 200:
            return employee_response.json()
        else:
            raise Exception(f"Erreur lors de la récupération des détails de l'employé: {employee_response.status_code}, {employee_response.text}")
    except Exception as e:
        raise Exception(str(e))

def update_employee_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Rediriger vers la page de connexion si l'utilisateur n'est pas authentifié

    if request.method == 'POST':
        form = UpdateEmployeeForm(request.POST)
        if form.is_valid():
            try:
                # Obtenir le token d'accès
                access_token = get_access_token('camille', 'maison')

                # Mettre à jour les informations de l'employé via l'API
                updated_user_employee = {
                    "employee_username": form.cleaned_data['employee_username'],
                    "employee_password": form.cleaned_data['employee_password'],
                    "employee_email": form.cleaned_data['employee_email'],
                    "employee_first_name": form.cleaned_data['employee_first_name'],
                    "employee_last_name": form.cleaned_data['employee_last_name'],
                    "employee_zip_code_prefix": form.cleaned_data['employee_zip_code_prefix'],
                    "employee_city": form.cleaned_data['employee_city'],
                    "employee_state": form.cleaned_data['employee_state']
                }
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                employee_id = request.user.employee_id  # Supposons que l'ID de l'employé est stocké dans l'utilisateur connecté
                api_response = requests.put(f"{EMPLOYEES_URL}/{employee_id}/", json=updated_user_employee, headers=headers)

                if api_response.status_code == 200:
                    messages.success(request, 'Employé mis à jour avec succès !')
                else:
                    messages.error(request, f"Erreur lors de la mise à jour de l'employé: {api_response.status_code}, {api_response.text}")
                return redirect('home')  # Rediriger vers une page d'accueil ou autre

            except Exception as e:
                messages.error(request, str(e))

        else:
            messages.error(request, 'Le formulaire contient des erreurs.')
    else:
        # Pré-remplir le formulaire avec les données actuelles de l'employé
        employee = get_employee_details(request.user.employee_id)  # Fonction pour obtenir les détails actuels de l'employé connecté
        form = UpdateEmployeeForm(initial={
            'employee_username': employee['employee_username'],
            'employee_password': '',  # Ne pas pré-remplir le mot de passe pour des raisons de sécurité
            'employee_email': employee['employee_email'],
            'employee_first_name': employee['employee_first_name'],
            'employee_last_name': employee['employee_last_name'],
            'employee_zip_code_prefix': employee['employee_zip_code_prefix'],
            'employee_city': employee['employee_city'],
            'employee_state': employee['employee_state']
        })
    return render(request, 'authentication/update_employee.html', {'form': form})
