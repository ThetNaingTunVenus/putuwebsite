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

class EcommerceOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
admin.site.register(EcommerceOrder,EcommerceOrderAdmin)

class EcommerceCartProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
admin.site.register(EcommerceCartProduct,EcommerceCartProductAdmin)

class messengerbotadmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'status_id', 'created_at')
admin.site.register(messengerbot,messengerbotadmin)



admin.site.register(Category)
admin.site.register(Order)
admin.site.register(ExpenseLedger)
admin.site.register(ExpenseReport)
admin.site.register(DamageItems)
admin.site.register(PurchaseList)
admin.site.register(Supplier)
admin.site.register(DeliverySystem)
admin.site.register(EcommerceBanner)
admin.site.register(EcommerceCart)
admin.site.register(messengerid)
admin.site.register(ItmColor)
admin.site.register(ItmSize)
admin.site.register(BestSellers)
admin.site.register(newestitem)
