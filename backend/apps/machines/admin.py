"""
Configuration de l'admin Django pour les machines BasicFit
"""
from django.contrib import admin
from django import forms
from django.core.files.uploadedfile import UploadedFile
from .models import GroupeMusculaire, CategorieMachine, Machine, VarianteMachine, MachineCategorie
from .services import CloudinaryService


@admin.register(GroupeMusculaire)
class GroupeMusculaireAdmin(admin.ModelAdmin):
    list_display = ['nom', 'couleur', 'ordre_affichage', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['ordre_affichage', 'is_active']
    search_fields = ['nom', 'description']
    ordering = ['ordre_affichage', 'nom']

    fieldsets = (
        (None, {
            'fields': ('nom', 'description', 'couleur', 'icone', 'ordre_affichage', 'is_active')
        }),
    )


@admin.register(CategorieMachine)
class CategorieMachineAdmin(admin.ModelAdmin):
    list_display = ['nom', 'get_nom_display', 'couleur', 'is_active', 'created_at']
    list_filter = ['nom', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['nom', 'description']
    ordering = ['nom']

    fieldsets = (
        (None, {
            'fields': ('nom', 'description', 'couleur', 'icone', 'is_active')
        }),
    )


class VarianteMachineInline(admin.TabularInline):
    model = VarianteMachine
    extra = 0
    fields = ['nom', 'niveau_difficulte', 'is_active']


class MachineCategorieInline(admin.TabularInline):
    model = MachineCategorie
    extra = 1
    fields = ['categorie', 'is_primary', 'ordre']


class MachineAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour uploader les GIFs sur Cloudinary"""

    gif_file = forms.FileField(
        label="Uploader un GIF",
        help_text="Sélectionnez un fichier GIF à uploader sur Cloudinary",
        required=False
    )

    class Meta:
        model = Machine
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Si un nouveau fichier GIF est uploadé
        gif_file = self.cleaned_data.get('gif_file')
        if gif_file:
            try:
                print(f"📤 Tentative d'upload vers Cloudinary: {gif_file.name}")
                # Upload sur Cloudinary
                cloudinary_service = CloudinaryService()
                cloudinary_url = cloudinary_service.upload_image(gif_file)
                instance.image_gif = cloudinary_url
                print(f"✅ Upload réussi: {cloudinary_url}")
            except Exception as e:
                print(f"❌ Erreur upload Cloudinary: {e}")
                # En cas d'erreur, on garde l'ancienne URL
                pass

        if commit:
            instance.save()
        return instance


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    form = MachineAdminForm

    list_display = [
        'nom', 'categorie', 'niveau_difficulte', 'popularite',
        'est_disponible', 'necessite_supervision'
    ]
    list_filter = [
        'categorie', 'niveau_difficulte', 'est_disponible',
        'necessite_supervision', 'created_at'
    ]
    list_editable = ['est_disponible', 'popularite']
    search_fields = [
        'nom', 'nom_anglais', 'description', 'instructions',
        'tags', 'fabricant', 'modele'
    ]
    ordering = ['categorie', 'ordre_affichage', 'nom']
    filter_horizontal = [
        'groupes_musculaires_primaires', 'groupes_musculaires_secondaires'
    ]

    fieldsets = (
        ('Informations générales', {
            'fields': (
                'nom', 'nom_anglais', 'description', 'instructions',
                'categorie', 'type_exercice'
            )
        }),
        ('Groupes musculaires', {
            'fields': (
                'groupes_musculaires_primaires', 'groupes_musculaires_secondaires'
            )
        }),
        ('Caractéristiques techniques', {
            'fields': (
                'increment_poids', 'poids_minimum', 'poids_maximum', 'tempo'
            )
        }),
        ('Métadonnées', {
            'fields': (
                'niveau_difficulte', 'popularite', 'est_disponible',
                'necessite_supervision', 'ordre_affichage', 'tags'
            )
        }),
        ('Médias', {
            'fields': ('gif_file', 'image_gif', 'image_principale', 'video_demonstration'),
            'classes': ('collapse',)
        }),
        ('Informations techniques', {
            'fields': ('fabricant', 'modele', 'numero_serie'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('nombre_utilisations', 'note_moyenne'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['nombre_utilisations', 'note_moyenne']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categorie')


@admin.register(VarianteMachine)
class VarianteMachineAdmin(admin.ModelAdmin):
    list_display = ['nom', 'machine', 'niveau_difficulte', 'is_active', 'created_at']
    list_filter = ['niveau_difficulte', 'is_active', 'machine__categorie', 'created_at']
    list_editable = ['is_active']
    search_fields = ['nom', 'description', 'machine__nom']
    filter_horizontal = ['groupes_musculaires_specifiques']
    ordering = ['machine', 'nom']

    fieldsets = (
        (None, {
            'fields': ('machine', 'nom', 'description', 'niveau_difficulte')
        }),
        ('Configuration spécifique', {
            'fields': ('groupes_musculaires_specifiques', 'instructions_specifiques', 'is_active')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('machine')


@admin.register(MachineCategorie)
class MachineCategorieAdmin(admin.ModelAdmin):
    list_display = ['machine', 'categorie', 'is_primary', 'ordre', 'created_at']
    list_filter = ['is_primary', 'categorie', 'created_at']
    list_editable = ['is_primary', 'ordre']
    search_fields = ['machine__nom', 'categorie__nom']
    ordering = ['machine', 'ordre', 'categorie']

    fieldsets = (
        (None, {
            'fields': ('machine', 'categorie', 'is_primary', 'ordre')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('machine', 'categorie')