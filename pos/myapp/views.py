import datetime

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum,Count,F
from django.http import HttpResponse
from django.views.generic import TemplateView, View, CreateView, DetailView,FormView
from django.urls import reverse_lazy

from django.core.paginator import Paginator

from .forms import *
from .models import *

#html2pdf
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.
def test(request):
    return render(request, 'test_slip.html')

# ===================================================User Log In ===============================
class UserRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            pass
        else:
            return redirect('myapp:UserLoginView')
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(FormView):
    template_name = 'login.html'
    form_class = ULoginForm
    success_url = reverse_lazy('myapp:DashboardView')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data['password']
        usr = authenticate(username=username, password=password)

        if usr is not None:
            login(self.request, usr)

        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid user login!'})
        return super().form_valid(form)

class UserLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('myapp:UserLoginView')


# ================================= end user log in ===========================================
class HomeView(UserRequiredMixin,TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_list'] = Items.objects.all().order_by('-id')
        context['queryset']=Order.objects.filter(created_at=datetime.date.today())
        return context


#test for barcode
class testbarcode(View):
    def post(self,request):
        product_idb = request.POST.get('pid')
        message = None
        if not product_idb:
            message = 'barcode is blank'
        if not message:
            product_obj = Items.objects.get(barcode_id=product_idb)
            product_id = product_obj.id
            # print(product_id)
            cart_id = self.request.session.get("cart_id", None)
            if cart_id:
                cart_obj = Cart.objects.get(id=cart_id)
                this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
                # Product already exists in cart
                if this_product_in_cart.exists():
                    cartproduct = this_product_in_cart.last()
                    cartproduct.quantity += 1
                    cartproduct.subtotal += product_obj.sell_price
                    cartproduct.remain_balance -= 1

                    cartproduct.save()
                    cart_obj.total += product_obj.sell_price
                    cart_obj.tax = cart_obj.total * 0.00
                    cart_obj.super_total = cart_obj.tax + cart_obj.total
                    cart_obj.save()
                    cartproduct_balance = cartproduct.remain_balance
                    # print('update')
                    item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)
                # New item added in cart
                else:
                    item_filter = Items.objects.filter(id=product_id)
                    balance_filter = item_filter[0].balance_qty
                    qty_balance = 1
                    cartproduct_balance = int(balance_filter) - int(qty_balance)
                    item_update = Items.objects.filter(id=product_id)
                    item_update.update(balance_qty=cartproduct_balance)
                    # print('success !!!!!!')
                    cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                             rate=product_obj.sell_price, quantity=1,
                                                             subtotal=product_obj.sell_price,
                                                             remain_balance=cartproduct_balance)

                    # item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)

                    cart_obj.total += product_obj.sell_price
                    cart_obj.tax = cart_obj.total * 0.00
                    cart_obj.super_total = cart_obj.tax + cart_obj.total
                    cart_obj.save()
            else:
                cart_obj = Cart.objects.create(total=0, staff=request.user)
                self.request.session['cart_id'] = cart_obj.id
                item_filter = Items.objects.filter(id=product_id)
                balance_filter = item_filter[0].balance_qty
                qty_balance = 1
                cartproduct_balance = int(balance_filter) - int(qty_balance)
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                         rate=product_obj.sell_price,
                                                         quantity=1, subtotal=product_obj.sell_price,
                                                         remain_balance=cartproduct_balance)

                item_update = Items.objects.filter(id=product_id)
                item_update.update(balance_qty=cartproduct_balance)

                cart_obj.total += product_obj.sell_price
                cart_obj.tax = cart_obj.total * 0.00
                # print('succ')
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
            cart_id = self.request.session.get('cart_id', None)
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = None
            context = {'cart': cart, 'message': message}

            return render(request, 'mycartview.html', context)
        else:
            return render(request, 'mycartview.html', {'message':message})




class AddToCartView(UserRequiredMixin,TemplateView):
    template_name = 'mycartview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

    #     # prouduct id get from request url
        product_id = self.kwargs['pro_id']

        # get product
        product_obj = Items.objects.get(id=product_id)


        # check it cart exist
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
            # Product already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.sell_price
                cartproduct.remain_balance -=1

                cartproduct.save()
                cart_obj.total += product_obj.sell_price
                cart_obj.tax = cart_obj.total * 0.00
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
                cartproduct_balance = cartproduct.remain_balance
                print('update')
                item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)
            # New item added in cart
            else:
                item_filter = Items.objects.filter(id=product_id)
                balance_filter = item_filter[0].balance_qty
                qty_balance = 1
                cartproduct_balance = int(balance_filter) - int(qty_balance)
                item_update = Items.objects.filter(id=product_id)
                item_update.update(balance_qty=cartproduct_balance)
                # print('success !!!!!!')
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                         rate=product_obj.sell_price, quantity=1,
                                                         subtotal=product_obj.sell_price,remain_balance=cartproduct_balance)

                # item_update = Items.objects.filter(id=product_id).update(balance_qty=cartproduct_balance)


                cart_obj.total += product_obj.sell_price
                cart_obj.tax = cart_obj.total * 0.00
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0, staff=self.request.user)
            self.request.session['cart_id'] = cart_obj.id
            item_filter = Items.objects.filter(id=product_id)
            balance_filter = item_filter[0].balance_qty
            qty_balance = 1
            cartproduct_balance = int(balance_filter) - int(qty_balance)
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.sell_price,
                                                     quantity=1, subtotal=product_obj.sell_price,remain_balance=cartproduct_balance)

            item_update = Items.objects.filter(id=product_id)
            item_update.update(balance_qty=cartproduct_balance)

            cart_obj.total += product_obj.sell_price
            cart_obj.tax = cart_obj.total * 0.00
            # print('succ')
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()

    #     # if product already exist
        context['product_list'] = Items.objects.all().order_by('-id')
        # context['cart'] = Cart.objects.get(id=cart_id)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

class MyCartView(UserRequiredMixin,TemplateView):
    template_name = 'mycartview.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        context['product_list'] = Items.objects.all().order_by('-id')
        context['queryset'] = Order.objects.filter(created_at=datetime.date.today()).order_by('-id')
        return context



class ManageCartView(UserRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        cp_id = kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity +=1
            cp_obj.remain_balance -=1
            item_balance = cp_obj.remain_balance
            item_update = Items.objects.filter(id=cp_obj.product.id).update(balance_qty=item_balance)
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total +=cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.remain_balance += 1
            item_balance = cp_obj.remain_balance
            item_update = Items.objects.filter(id=cp_obj.product.id).update(balance_qty=item_balance)
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            # cp_obj.remain_balance += cp_obj.quantity
            item_balance = cp_obj.remain_balance +cp_obj.quantity

            item_update = Items.objects.filter(id=cp_obj.product.id).update(balance_qty=item_balance)
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('myapp:MyCartView')


class EmptyCartView(UserRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)

            cart.cartproduct_set.all().delete()
            cart.total =0
            cart.tax = 0
            cart.super_total=0
            cart.save()
        return redirect('myapp:MyCartView')



class CheckoutView(UserRequiredMixin,CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('myapp:MyCartView')

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated and request.user.customer:
    #         print('login....')
    #     else:
    #         return redirect('/login/?next=/checkout/')
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        # print(form.instance.delivery_fee)
        deli = form.instance.delivery_fee
        dis = form.instance.discount
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            # form.instance.discount = 0
            form.instance.total = cart_obj.total

            # form.instance.ordered_staus = 'Cash'
            form.instance.tax = cart_obj.tax
            form.instance.all_total = cart_obj.super_total
            total_deli = deli + cart_obj.super_total - dis
            form.instance.all_total_delivery = total_deli

            del self.request.session['cart_id']
        else:
            return redirect('myapp:MyCartView')
        return super().form_valid(form)


#Product Edit
class ProductEditView(UserRequiredMixin,View):
    def get(self,request, pk):
        pi = Items.objects.get(id=pk)
        fm = AdminProductEditForm(instance=pi)
        return render(request,'productedit.html', {'form':fm})

    def post(self, request, pk):
        pi = Items.objects.get(id=pk)
        fm = AdminProductEditForm(request.POST,instance=pi)
        if fm.is_valid():
            fm.save()
        return redirect('myapp:HomeView')

class ProductCreate(View):
    def get(self,request):
        category = Category.objects.all()
        item_list = Items.objects.all()
        message = None
        context = {'item_list':item_list,'category':category,'message':message}
        return render(request, 'productcreate.html', context)
    def post(self,request):
        item_name = request.POST.get('item_name')
        category = request.POST.get('category')
        purchase_price = request.POST.get('purchase_price')
        sale_price = request.POST.get('sale_price')
        barcode_id = request.POST.get('barcode_id')
        photo = request.FILES['photo']
        message = None
        if not item_name:
            message = 'please enter item'
        if not message:
            item = Items(item_name=item_name,category=category,pruchase_price=purchase_price,sell_price=sale_price,barcode_id=barcode_id,photo=photo)
            item.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            category = Category.objects.all()
            item_list = Items.objects.all()
            context = {'message': message,'category':category,'item_list':item_list}
            return render(request, 'productcreate.html', context)

class CategoryCreate(View):
    def get(self,request):
        category = Category.objects.all()
        item_list = Items.objects.all()
        message = None
        context = {'item_list': item_list, 'category': category, 'message': message}
        return render(request, 'categorycreate.html', context)
    def post(self,request):
        category_name = request.POST.get('category_name')
        message = None
        if not category_name:
            message = 'please enter category name'
        if not message:
            cate = Category(category_name=category_name)
            cate.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            category = Category.objects.all()
            message = 'please enter category name'
            return render(request, 'categorycreate.html', {'message':message,'category':category})


# ================== report =============
class SaleInvoiceView(UserRequiredMixin,View):
    def get(self,request):
        # form = StockHistorySearchForm()
        queryset = Order.objects.all().order_by('-id')
        order_status = Order.objects.filter(ordered_staus='Ordering')
        sum = queryset.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']
        context = {
            'order_status': order_status,
            'saleinvoice': queryset,
            'sum_amt': sum_amt,
        }
        return render(request, 'invoicelist.html', context)

class SaleInvoiceReportFilter(View):
    def get(self,request):
        queryset = Order.objects.all()
        deli = DeliverySystem.objects.all()
        sum = queryset.aggregate(Sum('all_total'))['all_total__sum']
        context={'queryset':queryset,'sum':sum,'deli':deli}
        return render(request, 'salereportfilter.html', context)
    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        message = None
        if not fromdate:
            message = 'select from date'
        elif not todate:
            message = 'select to date'
        if not message:
            queryset =Order.objects.filter(created_at__range=[fromdate, todate])
            sum = queryset.aggregate(Sum('all_total'))['all_total__sum']
            context = {'queryset':queryset,'sum':sum}
            return render(request, 'salereportfilter.html', context)

        else:
            message = 'Select From Date and To Date to filter Sale Reports...'
            context = {'message': message}
            return render(request, 'salereportfilter.html', context)


def DeliveryPaymentReportView(request):
    deli_com = DeliverySystem.objects.all()
    deli = request.GET.get('deli')
    if deli == None:
        queryset = Order.objects.all()
        # queryset = Order.objects.filter(delivery_system is None)
        context = {'deli_com': deli_com, 'queryset': queryset}
        return render(request, 'delivered_report.html', context)
    else:
        queryset = Order.objects.filter(delivery_system__delivery_name=deli,deli_payment=False)
        # queryset = Order.objects.filter(delivery_system__delivery_name=deli)
        context = {'deli_com': deli_com, 'queryset': queryset}
        return render(request, 'delivered_report.html', context)

class Deliverpayment(View):
    def get(self,request,pk):
        status = Order.objects.get(id=pk)
        status.deli_payment = True
        # print(status.deli_payment)
        status.save()
        return redirect('myapp:DeliveryPaymentReportView')


class InvoiceDetailView(UserRequiredMixin,DetailView):
    template_name = 'invoicedetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = STATUS

        return context


class InvoiceThermalPrintView(DetailView):
    template_name = 'test_slip.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = STATUS

        return context

# ================= xhtml2pdf ===============
def pdf_invoice_create(request,id):
    ord_obj = Order.objects.get(id=id)
    template_path = 'pdf_invoice.html'
    context = {'ord_obj':ord_obj}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="invoice.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html,dest=response,
    )
    if pisa_status.err:
        return HttpResponse('have a error pdf')
    return response
    

class InvoiceStatusChange(View):
    def get(self, request, pk):
        pi = Order.objects.get(id=pk)
        fm = StatusChangeForm(instance=pi)
        return render(request, 'statuschange.html', {'form': fm})

    def post(self, request, pk):
        pi = Order.objects.get(id=pk)
        fm = StatusChangeForm(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
        return redirect('myapp:SaleInvoiceReportFilter')


class SaleItemReportView(View):
    def get(self,request):
        cart_product = CartProduct.objects.all()
        item = Items.objects.all()
        context = {'cart_product':cart_product,'item':item}
        return render(request, 'sale_item_report.html', context)

    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        item_name = request.POST.get('item_name')
        message = None
        if not fromdate:
            message = 'please select from date'
        elif not todate:
            message = 'please select to date'
        elif not item_name:
            message = 'please item name required'
        if not message:
            # item_id = Items.objects.get(id=)
            cart_product = CartProduct.objects.filter(created_at__range=[fromdate, todate],product=item_name)
            total_qty = cart_product.aggregate(Sum('quantity'))['quantity__sum']
            total_subtotal = cart_product.aggregate(Sum('subtotal'))['subtotal__sum']
            item = Items.objects.all()
            message = 'success filter'
            context = {'cart_product': cart_product, 'item': item, 'message':message,'total_qty':total_qty,'total_subtotal':total_subtotal}
            return render(request, 'sale_item_report.html', context)
        else:
            cart_product = CartProduct.objects.all()
            item = Items.objects.all()
            context = {'cart_product': cart_product, 'item': item, 'message':message}
            return render(request, 'sale_item_report.html', context)

class GPView(View):
    def get(self,request):
        cart_product = CartProduct.objects.all()
        purchase_item = PurchaseList.objects.all()
        item = Items.objects.all()
        context = {
            'item':item,
            'cart_product':cart_product,
            'purchase_item':purchase_item,
        }
        return render(request, 'gp_report.html', context)
    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        item_name = request.POST.get('item_name')
        message = None
        if not fromdate:
            message = 'please select from date'
        elif not todate:
            message = 'please select to date'
        elif not item_name:
            message = 'please item name required'
        if not message:
            cart_product = CartProduct.objects.filter(created_at__range=[fromdate, todate], product=item_name)
            total_qty = cart_product.aggregate(Sum('quantity'))['quantity__sum']
            total_subtotal = cart_product.aggregate(Sum('subtotal'))['subtotal__sum']

            item_id = Items.objects.get(id=item_name)
            purchase_item = PurchaseList.objects.filter(p_date__range=[fromdate, todate], item_name=item_id)
            pur_qty_total = purchase_item.aggregate(Sum('purchase_qty'))['purchase_qty__sum']
            pur_price_total = purchase_item.aggregate(Sum('total_purchase_price'))['total_purchase_price__sum']
            gp_profit = total_subtotal - pur_price_total
            gp_balance = pur_qty_total - total_qty
            item = Items.objects.all()
            context={
                'cart_product':cart_product,
                'total_qty':total_qty,
                'total_subtotal':total_subtotal,
                'purchase_item':purchase_item,
                'pur_qty_total':pur_qty_total,
                'pur_price_total':pur_price_total,
                'gp_profit':gp_profit,
                'gp_balance':gp_balance,
                'item':item,
            }
            return render(request, 'gp_report.html', context)
        else:
            cart_product = CartProduct.objects.all()
            purchase_item = PurchaseList.objects.all()
            item = Items.objects.all()
            context = {
                'item': item,
                'cart_product': cart_product,
                'purchase_item': purchase_item,
                'message':message,
            }
            return render(request, 'gp_report.html', context)

######## Supplier ##############
class SupplierCreate(View):
    def get(self,request):
        supplier = Supplier.objects.all()
        context = {'supplier':supplier}
        return render(request,'supplier.html', context)
    def post(self,request):
        supplier_name = request.POST.get('supplier_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        message = None
        if not supplier_name:
            message = 'Please Enter Supplier Name'
        elif not phone_number:
            message = 'Please Enter Phone Number'
        elif not address:
            message = 'Enter Address'
        if not message:
            supplier_save = Supplier(supplier_name=supplier_name,phone_number=phone_number,address=address)
            supplier_save.save()
            success = 'Supplier Name create successfully'
            supplier = Supplier.objects.all()
            context = {'supplier': supplier,'success':success}
            return render(request, 'supplier.html', context)
        else:
            supplier = Supplier.objects.all()
            context = {'supplier': supplier, 'message': message}
            return render(request, 'supplier.html', context)

class SupplierEdit(UserRequiredMixin,View):
    def get(self,request, pk):
        pi = Supplier.objects.get(id=pk)
        fm = SupplierEditForm(instance=pi)
        return render(request,'supplieredit.html', {'form':fm})

    def post(self, request, pk):
        pi = Supplier.objects.get(id=pk)
        fm = SupplierEditForm(request.POST,instance=pi)
        if fm.is_valid():
            fm.save()
        return redirect('myapp:SupplierCreate')


class PurchaseCreateView(TemplateView):
    template_name = 'purchase_create_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #     # supplier id get from request url
        supplier_id = self.kwargs['id']
        # get car info
        supplier_data = Supplier.objects.get(id=supplier_id)

        context['supplier'] = Supplier.objects.get(id=supplier_id)
        context['item'] = Items.objects.all()
        context['supplier_list'] = PurchaseList.objects.filter(supplier_name=supplier_data.supplier_name)

        return context



class PurchaseData(View):
    def get(self,request):
        supplier = Supplier.objects.all()
        purchasedata = PurchaseList.objects.all()
        sum_purchase_qty = purchasedata.aggregate(Sum('purchase_qty'))['purchase_qty__sum']
        sum_purchase_price = purchasedata.aggregate(Sum('purchase_price'))['purchase_price__sum']
        sum_purchase_total = purchasedata.aggregate(Sum('total_purchase_price'))['total_purchase_price__sum']
        sum_logistic = purchasedata.aggregate(Sum('logistic'))['logistic__sum']
        context = {'supplier': supplier,
                   'purchasedata':purchasedata,
                   'sum_purchase_qty':sum_purchase_qty,
                   'sum_purchase_price':sum_purchase_price,
                   'sum_logistic':sum_logistic,
                   'sum_purchase_total':sum_purchase_total,
                   }
        return render(request, 'purchasedata.html',context)
    def post(self,request):
        suppliername = request.POST.get('suppliername')
        p_date = request.POST.get('p_date')
        item_name = request.POST.get('item_name')
        purchase_qty = request.POST.get('purchase_qty')
        purchase_price = request.POST.get('purchase_price')
        sale_price = request.POST.get('sale_price')
        logistic = request.POST.get('logistic')
        message = None
        if not p_date:
            message = 'please select Date'
        elif not item_name:
            message = 'please select Item'
        elif not purchase_qty:
            message = 'please enter quantity'
        elif not purchase_price:
            message = 'please enter purchase price'
        if not message:
            total_purchase_price =int(purchase_qty)*int(purchase_price)
            purchase_logistic = int(total_purchase_price)+int(logistic)
            purchase_list = PurchaseList(
                supplier_name=suppliername,
                item_name=item_name,
                purchase_qty=purchase_qty,
                purchase_price=purchase_price,
                sale_price=sale_price,
                logistic=logistic,
                p_date=p_date,
                total_purchase_price=purchase_logistic
            )
            purchase_list.save()
            item_balance = Items.objects.filter(item_name=item_name)
            balance_qty = item_balance[0].balance_qty
            total_balance = int(balance_qty)+int(purchase_qty)
            item_update = Items.objects.filter(item_name=item_name).update(pruchase_price=purchase_price,sell_price=sale_price,balance_qty=total_balance)
            return redirect(request.META['HTTP_REFERER'])
        else:
            context = {'message':message}
            # return redirect(request.META['HTTP_REFERER'])
            return render(request,'purchase_create_view.html',context)

class PurchaseReport(View):
    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        message = None
        if not fromdate:
            message='select from date'
        elif not todate:
            message = 'select to date'
        if not message:
            supplier = Supplier.objects.all()
            purchasedata = PurchaseList.objects.filter(p_date__range=[fromdate, todate])
            sum_purchase_qty = purchasedata.aggregate(Sum('purchase_qty'))['purchase_qty__sum']
            sum_purchase_price = purchasedata.aggregate(Sum('purchase_price'))['purchase_price__sum']
            sum_logistic = purchasedata.aggregate(Sum('logistic'))['logistic__sum']
            sum_purchase_total = purchasedata.aggregate(Sum('total_purchase_price'))['total_purchase_price__sum']
            context = {'supplier': supplier,
                       'purchasedata': purchasedata,
                       'sum_purchase_qty': sum_purchase_qty,
                       'sum_purchase_price': sum_purchase_price,
                       'sum_logistic':sum_logistic,
                       'sum_purchase_total':sum_purchase_total,
                       }
            return render(request, 'purchasedata.html', context)
        else:
            supplier = Supplier.objects.all()
            context = {'supplier': supplier, 'message':message}
            return render(request, 'purchasedata.html', context)



class PurchaseDataDelete(View):
    def get(self,request,pk):
        pi = PurchaseList.objects.get(id=pk)
        fm = PurchaseDataDeleteFrom(instance=pi)
        return render(request, 'purchase_data_delete.html', {'form': fm})

    def post(self, request,pk):
        pi = PurchaseList.objects.get(id=pk)
        item = Items.objects.get(item_name=pi.item_name)
        item_n = item.balance_qty
        pur_qty = pi.purchase_qty
        remain_item_qty = int(item_n)-int(pur_qty)
        item_update = Items.objects.filter(item_name=pi.item_name).update(balance_qty=remain_item_qty)
        pi.delete()
        return redirect('myapp:PurchaseData')



# DamageItems
class DamageItemView(View):
    def get(self,request):
        invoice = Order.objects.all()
        context = {'invoice':invoice}
        return render(request, 'damage_invoice_view.html', context)

class DamageInvoiceView(TemplateView):
    template_name = 'damage_item_view.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #     # invoice id get from request url
        inv_id = self.kwargs['id']
        # get invoice info
        context['ord_obj'] = Order.objects.get(id=inv_id)
        return context

class DamageProductView(UserRequiredMixin,View):
    def get(self,request, id):
        pi = CartProduct.objects.get(id=id)
        fm = DamageProductForm(instance=pi)
        return render(request,'damage_product_view.html', {'form':fm})

    def post(self, request,id):
        returnqty =request.POST.get('returnqty')
        return_desc = request.POST.get('return_desc')
        product = request.POST.get('product')
        rate = request.POST.get('rate')
        quantity = request.POST.get('quantity')
        return_date =datetime.date.today()
        item_name = Items.objects.get(id=product)
        message = None
        if not returnqty:
            message='uu'
        elif not return_desc:
            message = 'uu'
        if not message:
            invtentory_date = Items.objects.filter(item_name=item_name)
            qty = invtentory_date[0].balance_qty
            remaing = int(qty) - int(returnqty)
            inv_update = Items.objects.filter(item_name=item_name).update(balance_qty=remaing)

            damage_items = DamageItems(item_name=item_name, quantity=returnqty, description=return_desc,
                                       return_date=return_date)
            damage_items.save()

            damage_rp = DamageItems.objects.all()
            context = {'damage_rp': damage_rp}
            return render(request, 'damage_report_view.html', context)
        else:
            message = 'please enter return qty and description'
            return render(request,'damage_invoice_view.html', {'message':message})


class DamageReportView(View):
    def get(self,request):
        damage_rp = DamageItems.objects.all()
        context = {'damage_rp': damage_rp}
        return render(request, 'damage_report_view.html', context)
    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        message = None
        if not fromdate:
            message = 'select from date'
        elif not todate:
            message = 'select to date'
        if not message:
            damage_rp = DamageItems.objects.filter(return_date__range=[fromdate, todate])
            context = {'damage_rp': damage_rp}
            return render(request, 'damage_report_view.html', context)
        else:
            message = 'Please Select From Date and To Date'
            context = {'message': message}
            return render(request, 'damage_report_view.html', context)




# Expnse
class ExpenseLedgerView(TemplateView):
    template_name = 'expense_ledger.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #     # ledger id get from request url
        ledger_id = self.kwargs['id']
        #get ledger info
        context['ledger'] = ExpenseLedger.objects.get(id=ledger_id)
        return context

class LedgerImport(View):
    def post(self,request):
        category = request.POST.get('category')
        balance = request.POST.get('balance')
        amount = request.POST.get('amount')
        message = None
        if not amount:
            message = 'Enter Amount'
        if not message:
            ledger_balance = int(balance)+int(amount)
            leger = ExpenseLedger.objects.filter(category=category).update(balance=ledger_balance)
            title = 'Input Ledger'
            expense_rep = ExpenseReport(expense_type=title, title=title, category=category, amount=amount,expense_date=datetime.date.today())
            expense_rep.save()
            return redirect(request.META['HTTP_REFERER'])
        else:
            return render(request, 'expense_ledger.html', {'message':message})

class ExpenseReportView(View):
    def get(self,request):
        expense_ledger = ExpenseLedger.objects.all()
        expense_report = ExpenseReport.objects.all()
        grand_total_amount = expense_report.aggregate(Sum('amount'))['amount__sum']
        grand_total_ledger = expense_ledger.aggregate(Sum('balance'))['balance__sum']
        context = {'expense_ledger': expense_ledger,'expense_report':expense_report,'grand_total_amount':grand_total_amount,'grand_total_ledger':grand_total_ledger}
        return render(request, 'expense_report.html', context)
    def post(self,request):
        title = request.POST.get('title')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        expense_date = request.POST.get('expense_date')
        expense_type = 'Expense'
        message = None
        if not title:
            message= 'select title'
        elif not category:
            message = 'select category'
        elif not amount:
            message = 'enter amount'
        elif not expense_date:
            message = 'select date'
        if not message:
            expense_rep = ExpenseReport(expense_type=expense_type, title=title, category=category, amount=amount,
                                        expense_date=expense_date)
            expense_rep.save()

            exp_ledger = ExpenseLedger.objects.filter(category=category)
            ledger_bal = exp_ledger[0].balance
            expense_category_balance = int(ledger_bal) - int(amount)
            ledger_upd = ExpenseLedger.objects.filter(category=category).update(balance=expense_category_balance)
            return redirect('myapp:ExpenseReportView')
        else:
            expense_ledger = ExpenseLedger.objects.all()
            # expense_report = ExpenseReport.objects.all()
            context = {'expense_ledger': expense_ledger,'message':message}
            return render(request, 'expense_report.html', context)

class ExpenseReportFilter(View):
    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        message = None
        if not fromdate:
            message = 'select from date'
        elif not todate:
            message = 'select to date'
        if not message:
            expense_ledger = ExpenseLedger.objects.all()
            expense_report = ExpenseReport.objects.filter(expense_date__range=[fromdate, todate])
            grand_total_amount = expense_report.aggregate(Sum('amount'))['amount__sum']
            grand_total_ledger = expense_ledger.aggregate(Sum('balance'))['balance__sum']
            # sum_purchase_price = purchasedata.aggregate(Sum('purchase_price'))['purchase_price__sum']
            context = {'expense_ledger':expense_ledger,'expense_report':expense_report,'grand_total_amount':grand_total_amount,'grand_total_ledger':grand_total_ledger}
            return render(request, 'expense_report.html', context)
        else:
            expense_ledger = ExpenseLedger.objects.all()
            # expense_report = ExpenseReport.objects.all()
            context = {'expense_ledger': expense_ledger, 'message': message}
            return render(request, 'expense_report.html', context)

    def get(self,request):
        expense_ledger = ExpenseLedger.objects.all()
        expense_report = ExpenseReport.objects.all()
        grand_total_amount = expense_report.aggregate(Sum('amount'))['amount__sum']
        grand_total_ledger = expense_ledger.aggregate(Sum('balance'))['balance__sum']
        context = {'expense_ledger': expense_ledger,'expense_report':expense_report,'grand_total_ledger':grand_total_ledger,'grand_total_amount':grand_total_amount}
        return render(request, 'expense_report.html', context)

class LedgerCreateView(View):
    def get(self,request):
        return render(request, 'ledgercreate.html')
    def post(self,request):
        category = request.POST.get('category')
        message = None
        if not category:
            message='enter name'
        if not message:
            g = ExpenseLedger(category=category)
            g.save()
            return redirect('myapp:ExpenseReportView')
        else:
            return render(request, 'ledgercreate.html', {'message':message})


class DashboardView(UserRequiredMixin,View):
    def get(self,request):
        today = datetime.date.today()
        first_date = today.replace(day=1)
        dashorder = Order.objects.filter(created_at__range=[first_date, today])
        expense_type = 'Expense'
        exp_total = ExpenseReport.objects.filter(expense_date__range=[first_date, today],expense_type=expense_type).aggregate(Sum('amount'))['amount__sum']
        purchase_total = PurchaseList.objects.filter(created_date__range=[first_date, today]).aggregate(Sum('total_purchase_price'))['total_purchase_price__sum']

        # item_list = Items.objects.all()
        # paginator = Paginator(item_list, 3)  # Show 10 contacts per page.
        #
        # page_number = request.GET.get("page")
        # page_obj = paginator.get_page(page_number)
# chart data
        purchasedata = PurchaseList.objects.all()
        c_product = CartProduct.objects.values('product__item_name','product__sell_price','product__balance_qty','product__pruchase_price').annotate(sum=Sum('subtotal'),quantity=Sum('quantity'),pur=(F('product__sell_price')-F('product__pruchase_price'))*F('quantity')).filter(created_at__range=[first_date, today])

        sale_total = Order.objects.filter(created_at__range=[first_date, today]).aggregate(Sum('all_total'))['all_total__sum']
        # profit_b = sale_total-purchase_total
        if sale_total == None:
            sale_total = 0
        if purchase_total == None:
            purchase_total = 0

        profit_b = sale_total - purchase_total

        gp_total = c_product.aggregate(gp=Sum((F('product__sell_price')-F('product__pruchase_price'))*F('quantity')))
        total_sale_amt = c_product.aggregate(Sum('subtotal'))['subtotal__sum']
        total_sale_qty = c_product.aggregate(Sum('quantity'))['quantity__sum']

        # print(total_sale_qty)

        context = {'c_product':c_product,
                   'sale_total':sale_total,
                   'purchase_total':purchase_total,
                   'exp_total':exp_total,
                   'profit_b':profit_b,
                   'purchasedata':purchasedata,
                   'gp_total':gp_total,
                   'total_sale_amt':total_sale_amt,
                   'total_sale_qty':total_sale_qty,
                   'dashorder':dashorder,
                   # 'page_obj':page_obj,
                   }

        return render(request, 'dashboard.html', context)
    def post(self,request):
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        message = None
        if not fromdate:
            message = 'select from date'
        elif not todate:
            message = 'select to date'
        if not message:
            c_product = CartProduct.objects.values('product__item_name',
                                                   'product__sell_price',
                                                   'product__balance_qty',
                                                   'product__pruchase_price').annotate(sum=Sum('subtotal'),
                                                                                       quantity=Sum('quantity'),
                                                                                       pur=(F('product__sell_price') - F('product__pruchase_price')) * F('quantity')).filter(created_at__range=[fromdate, todate])

            gp_total = c_product.aggregate(
                gp=Sum((F('product__sell_price') - F('product__pruchase_price')) * F('quantity')))
            sale_total = c_product.aggregate(Sum('subtotal'))['subtotal__sum']

            # sale_total = Order.objects.filter(created_at__range=[fromdate, todate]).aggregate(Sum('all_total'))['all_total__sum']

            context = {'c_product': c_product,
                       'gp_total': gp_total,
                       'sale_total': sale_total,
                       'message':message,
                    #    'sale_total':sale_total,
                       # 'page_obj':page_obj,
                       }
            return render(request, 'dashboard.html', context)
        else:
            return redirect('myapp:DashboardView')



class DeliveryView(View):
    def get(self,request):
        deli = DeliverySystem.objects.all()
        context ={'deli':deli}
        return render(request, 'delivery_view.html', context)

    def post(self,request):
        delivery_name = request.POST.get('delivery_name')
        message = None
        if not delivery_name:
            message = 'enter name'
        if not message:
            g = DeliverySystem(delivery_name=delivery_name)
            g.save()
            return redirect('myapp:DeliveryView')
        else:
            deli = DeliverySystem.objects.all()
            context = {'deli': deli,'message':message}
            return render(request, 'delivery_view.html', context)

def second_dashboard(request):
    context={

    }
    return render(request, 'second_dashboard.html', context)


class webpage_home(TemplateView):
    template_name = 'web/store.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = EcommerceCart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        context['itm'] = Items.objects.all().order_by('-id')
        context['queryset'] = Order.objects.filter(created_at=datetime.date.today()).order_by('-id')
        context['banner'] = EcommerceBanner.objects.filter(id=1)
        return context


class pro_detail(TemplateView):
    template_name = 'web/product-detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #     # supplier id get from request url
        order_id = self.kwargs['id']
        # get style info
        item_data = Items.objects.get(id=order_id)
        context['order_data']=item_data

        return context


class WebAddtoCart(View):
    def post(self,request):
        pid = request.POST.get('pid')
        product_obj = Items.objects.get(id=pid)
        product_id = product_obj.id
            # print(product_id)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = EcommerceCart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.ecommercecartproduct_set.filter(product=product_obj)
            # Product already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.sell_price
                # cartproduct.remain_balance -= 1
                cartproduct.save()
                cart_obj.total += product_obj.sell_price
                cart_obj.tax = cart_obj.total * 0.00
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
            #new item add in cart
            else:
                item_filter = Items.objects.filter(id=product_id)
                cartproduct = EcommerceCartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                             rate=product_obj.sell_price, quantity=1,
                                                              item_color=1,
                                                             item_size=1,
                                                             subtotal=product_obj.sell_price,
                                                             remain_balance=0)
                cart_obj.total += product_obj.sell_price
                cart_obj.tax = cart_obj.total * 0.00
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
            
        else:
            cart_obj = EcommerceCart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = EcommerceCartProduct.objects.create(cart=cart_obj, product=product_obj,
                                                             rate=product_obj.sell_price,
                                                             quantity=1,
                                                             item_color=1,
                                                             item_size=1,
                                                             subtotal=product_obj.sell_price,
                                                             remain_balance=0)
            cart_obj.total += product_obj.sell_price
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()

        return redirect('myapp:webpage_home')


class WebCartView(TemplateView):
    template_name = 'web/cart.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = EcommerceCart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        context['product_list'] = Items.objects.all().order_by('-id')
        context['queryset'] = Order.objects.filter(created_at=datetime.date.today()).order_by('-id')
        return context



class WebsiteAddtoCart(TemplateView):
    template_name = 'web/store.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

    #     # prouduct id get from request url
        product_id = self.kwargs['pro_id']

        # get product
        product_obj = Items.objects.get(id=product_id)

        # check it cart exist
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            pass
        else:
            cart_obj = Cart.objects.create(total=0)            
            self.request.session['cart_id'] = cart_obj.id
            
class WebCartManage(View):
    def get(self, request, *args, **kwargs):
        cp_id = kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj = EcommerceCartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        if action == "inc":
            cp_obj.quantity +=1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total +=cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
           
            cart_obj.tax = cart_obj.total * 0.00
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('myapp:WebCartView')


class WebCheckOut(TemplateView):
    template_name='web/checkout.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = EcommerceCart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context


class EcommerceBannerView(View):
    def get(self,request):
        p = EcommerceBanner.objects.all()
        context = {'p':p}
        return render(request, 'web/EcommerceBanner.html', context)

    def post(self, request):
        pid = request.POST.get('pid')
        pc = request.POST.get('pcode')

        if pc == '1':
            print(pc)
            photo1 = request.FILES['photo1']
            p = EcommerceBanner.objects.filter(id=1).update(photo1=photo1)
            return redirect('myapp:EcommerceBanner')
        elif pc == '2':
            print(pc)
            photo2 = request.FILES['photo2']
            p = EcommerceBanner.objects.filter(id=1).update(photo2=photo2)

            return redirect('myapp:EcommerceBanner')

        return HttpResponse('hell')
            
        # fil = request.FILES['photo1']
        # product_obj = EcommerceBanner.objects.get(id=pid)

class EcommerceSaleOrder(TemplateView):
    template_name='EcommerceSaleOrder.html'
