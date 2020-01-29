from django.db import models
from django import forms
from datetime import date,datetime
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Person(models.Model):
    tpr_surname = models.CharField(max_length=80)
    tpr_forename = models.CharField(max_length=80)
    tpr_middle = models.CharField(max_length=80)
    tpr_born_date = models.DateField()
    tpr_main_doc = models.CharField(max_length=20)
    tpr_unprofit = models.BooleanField(null=True, default=False)
    tpr_psycho = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.tpr_surname + ' ' + self.tpr_forename + ' ' + self.tpr_middle


class ContactType(models.Model):
    tct_val = models.CharField(max_length=50)

    def __str__(self):
        return self.tct_val


class DocumentType(models.Model):
    tdt_val = models.CharField(max_length=50)

    def __str__(self):
        return self.tdt_val


class AddressType(models.Model):
    tat_val = models.CharField(max_length=50)

    def __str__(self):
        return self.tat_val


class FreqPay(models.Model):
    tfp_val = models.CharField(max_length=50)

    def __str__(self):
        return self.tfp_val


class ContractStatus(models.Model):
    tcs_val = models.CharField(max_length=50)

    def __str__(self):
        return self.tcs_val


class ClaimStatus(models.Model):
    tcs_val = models.CharField(max_length=50)

    def __str__(self):
        return self.tcs_val


class ContractSeries(models.Model):
    tcss_val = models.CharField(max_length=50)
    tcss_desc = models.CharField(max_length=50)

    def __str__(self):
        return self.tcss_val


class Contract(models.Model):
    tco_tcss_id = models.ForeignKey(ContractSeries, on_delete=models.CASCADE, default=1)
    tco_tpr_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    tco_tcs_id = models.ForeignKey(ContractStatus, on_delete=models.CASCADE, default=9)
    tco_tfp_id = models.ForeignKey(FreqPay, on_delete=models.CASCADE, default=1)
    tco_number = models.DecimalField(max_digits=10, decimal_places=0)
    tco_length = models.IntegerField(default=1)
    tco_sign_date = models.DateField(null=True)
    tco_start_date = models.DateField(null=True)
    tco_pre_end_date = models.DateField(null=True)
    tco_end_date = models.DateField(null=True)
    tco_app_original = models.FileField(null=True)


class Contact(models.Model):
    con_tpr_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    con_tct_id = models.ForeignKey(ContactType, on_delete=models.CASCADE)
    con_val = models.CharField(max_length=40)


class Address(models.Model):
    addr_tpr_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    addr_tat_id = models.ForeignKey(AddressType, on_delete=models.CASCADE)
    addr_val = models.CharField(max_length=300)


class Document(models.Model):
    doc_tpr_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    doc_tdt_id = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    doc_series = models.CharField(max_length=30, null=True)
    doc_number = models.CharField(max_length=30, null=True)
    doc_issue_date = models.DateField(null=True)
    doc_issue_org = models.CharField(max_length=255, null=True)


class Dealer(models.Model):
    tde_number = models.DecimalField(max_digits=10, decimal_places=0)
    tde_tpr_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    tde_start = models.DateField()
    tde_end = models.DateField(null=True)
    tde_user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=None)


class InsEvent(models.Model):
    tiv_tco_id = models.ForeignKey(Contract, on_delete=models.CASCADE)
    tiv_tcs_id = models.ForeignKey(ClaimStatus, on_delete=models.CASCADE, default=1)
    tiv_date = models.DateField()
    tiv_time = models.TimeField()
    tiv_app_date = models.DateField()
    tiv_desc = models.TextField()


class Risk(models.Model):
    rsk_tcss_id = models.ForeignKey(ContractSeries, on_delete=models.CASCADE)
    rsk_name = models.CharField(max_length=50)
    rsk_proportion = models.IntegerField(default=1)
    rsk_ins_proportion = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    def __str__(self):
        return self.rsk_name


class ElemClaim(models.Model):
    tel_tiv_id = models.ForeignKey(InsEvent, on_delete=models.CASCADE)
    tel_rsk_id = models.ForeignKey(Risk, on_delete=models.CASCADE)
    tel_tcs_id = models.ForeignKey(ClaimStatus, on_delete=models.CASCADE, default=1)
    tel_sum = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    tel_sum_fact = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)


class ContractDealer(models.Model):
    tcd_tde_id = models.ForeignKey(Dealer, on_delete=models.CASCADE)
    tcd_tco_id = models.ForeignKey(Contract, on_delete=models.CASCADE)
    tcd_start = models.DateField(null=True)
    tcd_end = models.DateField(null=True)


class Payout(models.Model):
    tpo_tiv_id = models.ForeignKey(InsEvent, on_delete=models.CASCADE)
    tpo_date = models.DateField(null=True)
    tpo_commentary = models.TextField(null=True)
    tpo_sum = models.DecimalField(max_digits=15, decimal_places=2)


class ContractRisk(models.Model):
    tcr_tco_id = models.ForeignKey(Contract, on_delete=models.CASCADE)
    tcr_rsk_id = models.ForeignKey(Risk, on_delete=models.CASCADE)
    tcr_sum = models.DecimalField(max_digits=15, decimal_places=2)
    tcr_str_sum = models.DecimalField(max_digits=20, decimal_places=2)
    tcr_start = models.DateField(null=True)
    tcr_end = models.DateField(null=True)


class TerrList(models.Model):
    ttl_surname = models.CharField(max_length=80)
    ttl_forename = models.CharField(max_length=80)
    ttl_middle = models.CharField(max_length=80)
    ttl_born_date = models.DateField()
    tpr_main_doc = models.CharField(max_length=20)


class WorkerPhoto(models.Model):
    wp_photo = models.ImageField(upload_to='worker_photos/')
    wp_user_id = models.ForeignKey(User, on_delete=models.CASCADE)


