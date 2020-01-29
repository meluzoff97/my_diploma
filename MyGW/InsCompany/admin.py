from django.contrib import admin
from .models import *


class ContractAdmin(admin.ModelAdmin):
    list_display = ('tco_number', 'tco_tcss_id', 'tco_tcs_id', 'tco_tfp_id', 'tco_tpr_id')
    list_filter = ('tco_number', 'tco_tcss_id')
    search_fields = ('tco_number', 'tco_tcss_id')


class PersonAdmin(admin.ModelAdmin):
    list_display = ('tpr_surname', 'tpr_forename', 'tpr_middle', 'tpr_born_date')
    list_filter = ('tpr_surname', 'tpr_forename', 'tpr_middle', 'tpr_born_date')
    search_fields = ('tpr_surname', 'tpr_forename', 'tpr_middle', 'tpr_born_date')


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('wp_user_id', 'wp_photo')
    list_filter = ('wp_user_id', 'wp_photo')
    search_fields = ('wp_user_id', 'wp_photo')


admin.site.register(Contract, ContractAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(WorkerPhoto, WorkerAdmin)


