from django.contrib import admin
from stores.models import Cart, OutdoorCart, OutdoorOrder, Category, Image, Item, Order, OrderItem, Price, ServiceCart, ServiceOrder, SubCategory
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.
class ItemResource(resources.ModelResource):
    class Meta:
        model = Item
        
class ItemAdmin(ImportExportModelAdmin):
   resource_class = ItemResource


@admin.register(Item)
class ItemAdmin(ItemAdmin):
    pass


#####Categoy #######
class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        
class CategoryAdmin(ImportExportModelAdmin):
   resource_class = CategoryResource


@admin.register(Category)
class CategoryAdmin(CategoryAdmin):
    pass
    


######Sub Category ######
class SubCategoryResource(resources.ModelResource):
    class Meta:
        model = SubCategory
        
class SubCategoryAdmin(ImportExportModelAdmin):
   resource_class = SubCategoryResource


@admin.register(SubCategory)
class SubCategoryAdmin(SubCategoryAdmin):
    pass

    
admin.site.register(Image)
admin.site.register(Cart)
admin.site.register(OutdoorCart)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(OutdoorOrder)
admin.site.register(Price)
admin.site.register(ServiceCart)
admin.site.register(ServiceOrder)
