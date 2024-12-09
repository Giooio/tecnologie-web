from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', welcome, name='welcome'),
    path('products/', index, name='index'),
    path('register/', register, name='register'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('add/', aggiungi_prodotto, name='admin_add_product'),
    path('delete/', admin_delete_product, name='admin_delete_product'),
    path('delete/<int:product_id>/confirm/', confirm_delete_product, name='confirm_delete_product'),
    path('delete/<int:product_id>/delete/', elimina_prodotto, name='elimina_prodotto'),
    path('edit/', modifica_prodotto, name='admin_edit_product'),
    path('edit/<int:product_id>/', modifica_prodotto_form, name='edit_product_form'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('category-list/', category_list, name='category_list'),
    path('tutti-i-prodotti/', all_products, name='all_products'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('manage_questions/', manage_questions, name='manage_questions'),
    path('submit-question/', submit_question, name='submit_question'),
    path('delete_question/<int:question_id>/', delete_question, name='delete_question'),
    path('manage-users/', manage_users, name='manage_users'),
    path('orders/', manage_orders, name='manage_orders'),
    path('order/<int:order_id>/ready/', mark_ready_for_pickup, name='mark_ready_for_pickup'),
    path('orders/<int:order_id>/', order_details_admin, name='order_details_admin'),
    path('orders/<int:order_id>/update/<str:status>/', update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/toggle-ready/', toggle_ready_for_pickup, name='toggle_ready_for_pickup'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('orders/<int:order_id>/confirm_cancel/', confirm_cancel_order, name='confirm_cancel_order'),
    path('delete_order/<int:order_id>/', delete_order, name='delete_order'),
    path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
    path('toggle-user-status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('user-activity/<int:user_id>/', user_activity, name='user_activity'),
    
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', cart_update, name='cart_update'),
    path('purchase_summary/', purchase_summary, name='purchase_summary'),
    path('view-orders/', view_orders, name='view_orders'),
    path('order-details/<int:order_id>/', order_details, name='order_details'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
