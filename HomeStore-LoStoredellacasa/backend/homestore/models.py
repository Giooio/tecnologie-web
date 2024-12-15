from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.conf import settings


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=7, unique=True, help_text="Codice colore HEX, ad esempio: #FF5733")

    def __str__(self):
        return self.name

class Product(models.Model):
    categoria = models.CharField(max_length=200) 
    nome = models.CharField(max_length=200)
    descrizione = models.TextField()
    immagine = models.ImageField(upload_to='media/', blank=True, null=True)
    prezzo = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sold_count = models.PositiveIntegerField(default=0)
    colori = models.ManyToManyField(Color, blank=True)
    
    def save(self, *args, **kwargs):
        if self.stock is None:
            self.stock = 0 
        self.available = self.stock > 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nome

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,  
        default=1  
    )
    created_at = models.DateTimeField(default=timezone.now)
    products = models.ManyToManyField('Product', through='CartItem')

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def __str__(self):
        return f"Carrello di {self.user.username} - {self.created_at}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Product deve essere definito
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=7, null=True, blank=True)

    def get_total_price(self):
        return self.product.prezzo * self.quantity  # Calcola il totale per questo prodotto

    def __str__(self):
        return f'{self.product.nome} - {self.quantity} pcs - Colore: {self.color}'
    
class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    answer_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text
    
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"
    

    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'In attesa'),
        ('completed', 'Ritirato'),
        ('cancelled', 'Annullato')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cart_items = models.ManyToManyField(CartItem)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    ready_for_pickup = models.BooleanField(default=False)
    pickup_deadline = models.DateTimeField(null=True, blank=True)
    
    def days_left_for_pickup(self):
        if self.ready_for_pickup:
            # Se l'ordine è pronto per il ritiro, calcola la scadenza dei 10 giorni a partire da quel momento
            deadline = self.pickup_deadline
            if not deadline:  # Se la deadline non è stata impostata, impostala ora
                deadline = timezone.now() + timedelta(days=10)
                self.pickup_deadline = deadline
                self.save()

            remaining_days = (deadline - timezone.now()).days
            return max(remaining_days, 0)
        else:
            # Se non è pronto per il ritiro, ritorna 0
            return 0
    
    def __str__(self):
        return f"Ordine #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return f"{self.product.nome} (x{self.quantity})"
    

    