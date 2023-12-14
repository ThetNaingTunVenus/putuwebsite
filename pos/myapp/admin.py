from django.contrib import admin
from .models import *
# Register your models here.
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_name','category','pruchase_price','sell_price','balance_qty')
admin.site.register(Items,ItemsAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ('id','total','staff')
admin.site.register(Cart,CartAdmin)

class CartProductAdmin(admin.ModelAdmin):
    list_display = ('id','cart','product','rate','quantity','subtotal','remain_balance')
admin.site.register(CartProduct,CartProductAdmin)

admin.site.register(Category)
admin.site.register(Order)
admin.site.register(ExpenseLedger)
admin.site.register(ExpenseReport)
admin.site.register(DamageItems)
admin.site.register(PurchaseList)
admin.site.register(Supplier)
admin.site.register(DeliverySystem)
