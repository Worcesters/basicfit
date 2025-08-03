from django.contrib.auth import get_user_model

User = get_user_model()

# Supprimer l'admin existant s'il existe
User.objects.filter(username='admin').delete()

# Créer le nouvel admin
admin_user = User.objects.create_superuser('admin', 'admin@basicfit.com', 'admin')

print('✅ Superuser admin créé avec succès')
print(f'Username: {admin_user.username}')
print(f'Email: {admin_user.email}')
print(f'Is superuser: {admin_user.is_superuser}')