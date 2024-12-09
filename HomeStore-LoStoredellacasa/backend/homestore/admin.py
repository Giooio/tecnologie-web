# admin.py
from django.contrib import admin
from .models import Product, Color, Cart, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Aggiungi colori al database
colors = [
    {'name': 'Rosso', 'code': '#FF0000'},
    {'name': 'Blu', 'code': '#0000FF'},
    {'name': 'Verde', 'code': '#008000'},
    {'name': 'Nero', 'code': '#000000'},
    {'name': 'Bianco', 'code': '#FFFFFF'},
    {'name': 'Grigio', 'code': '#808080'},
    {'name': 'Beige', 'code': '#F5F5DC'},
]

for color in colors:
    Color.objects.get_or_create(name=color['name'], code=color['code'])

# Registrazione modello Cart
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)

# Registrazione modello Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'total')
    list_filter = ('status', 'created_at')

# Registrazione modello OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')

# Personalizzazione dell'amministrazione per l'utente
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    actions = ['make_active', 'make_inactive', 'delete_users']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Attiva selezionati"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Disattiva selezionati"

    def delete_users(self, request, queryset):
        queryset.delete()
    delete_users.short_description = "Elimina selezionati"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registrazione di Product con Personalizzazione Admin
class ProductAdmin(admin.ModelAdmin):
    search_fields = ('nome',)
    filter_horizontal = ('colori',)  # Aggiungi questa riga per selezionare più colori

admin.site.register(Product, ProductAdmin)  # Qui registriamo il modello Product con ProductAdmin
admin.site.register(Color)  # Assicurati che anche Color sia registrato per la gestione
