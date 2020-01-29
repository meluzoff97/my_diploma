from __future__ import print_function
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from mailmerge import MailMerge
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from django.views.generic import ListView, FormView
from django.contrib import auth
from django.contrib.auth.models import User,Group
from django.contrib.auth.forms import UserCreationForm
from MyGW.InsCompany.forms import *
from .models import *
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
import smtplib


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def login(request):
    args = {}
    args['form'] = Login()
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Добро пожаловать, ' + username + '!')
            return redirect('/')
        else:
            messages.error(request, 'Неверные данные, повторите попытку')
            return render(request, 'user/login.html', args)
    else:
        return render(request, 'user/login.html', args)


def logout(request):
    auth.logout(request)
    return redirect('/')


class MainPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            cursor = connection.cursor()
            query = 'select tde_number,wp_photo, count(*) as my_count ' \
                    'from "InsCompany_contract" ' \
                    'join "InsCompany_contractdealer" ICc on "InsCompany_contract".id = ICc.tcd_tco_id_id ' \
                    'and ICc.tcd_end is null ' \
                    'join "InsCompany_dealer" ICd on ICc.tcd_tde_id_id = ICd.id ' \
                    'join "InsCompany_person" ICp on ICd.tde_tpr_id_id = ICp.id ' \
                    'join auth_user a on ICd.tde_user_id_id = a.id ' \
                    'join "InsCompany_workerphoto" ICw on a.id = ICw.wp_user_id_id ' \
                    'group by tde_number, wp_photo ' \
                    'order by count(*) desc ' \
                    'limit 5'
            print(query)
            cursor.execute(query)
            my_top = dictfetchall(cursor)
            print(my_top)
            user = auth.get_user(request)
            return render(request, 'index.html', {'username': user.username,
                                                  'group': user.groups.get(user=auth.get_user(request)).id,
                                                  'my_top': my_top})


@login_required(login_url='/login/')
def password_edit(request):
    args = {}
    args['form'] = PasswordChangeForm()
    u = User.objects.get(username=auth.get_user(request).username)
    p = u.password
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            if check_password(form.cleaned_data['old_password'], p) is False:
                messages.error(request, 'Неверно введен текущий пароль, повторите попытку')
                return render(request, 'user/password_edit.html', args)
            elif form.cleaned_data['new_password'] != form.cleaned_data['new_password2']:
                messages.error(request, 'Повторное введение нового пароля неверно')
                return render(request, 'user/password_edit.html', args)
            elif form.cleaned_data['new_password'] == form.cleaned_data['old_password']:
                messages.error(request, 'Новый и текущий пароли не должны совпадать')
                return render(request, 'user/password_edit.html', args)
            else:
                u.set_password(form.cleaned_data['new_password'])
                u.save()
                user = auth.authenticate(username=u, password=form.cleaned_data['new_password'])
                auth.login(request, user)
                messages.success(request, 'Ваш пароль успешно обновлен')
                return redirect('/')
        else:
            render(request, 'user/password_edit.html', args)
    else:
        return render(request, 'user/password_edit.html', args)


def password_reset(request):
    args = {}
    args['form'] = ResetForm()
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        if User.objects.filter(username=username).count() == 0:
                messages.error(request, 'Такого пользователя не существует')
                return render(request, 'user/password_reset.html', args)
        elif email != User.objects.get(username=username).email:
                messages.error(request, 'Указана неверная почта')
                return render(request, 'user/password_reset.html', args)
        else:
                passwd = User.objects.make_random_password()
                user = User.objects.get(username=username)
                user.set_password(passwd)
                user.save()
                smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
                smtpObj.starttls()
                smtpObj.login('InsCompany@list.ru', '135246qwe')
                SUBJECT = "New password"
                FROM = "InsCompany@list.ru"
                TO = email
                BODY = "\r\n".join((
                    "From: %s" % FROM,
                    "To: %s" % TO,
                    "Subject: %s" % SUBJECT,
                    "",
                    'Your new password: ' + passwd + '\n'+'Your dear InsCompany'
                ))
                smtpObj.sendmail(FROM, [TO], BODY)
                smtpObj.quit()
                messages.info(request, 'На почту выслан новый пароль')
                return redirect('login')
    else:
        return render(request, 'user/password_reset.html', args)


class ContractsPageView(View):
    def get(self, request):
        if auth.get_user(request).groups.get(user=auth.get_user(request)).id == 6:
            dealer = Dealer.objects.get(tde_user_id=auth.get_user(request).id)
            deal_contracts = ContractDealer.objects.filter(tcd_tde_id=dealer, tcd_end=None)
            contracts_list = list()
            for contract in deal_contracts:
                contracts_list.append(contract.tcd_tco_id.id)
            data = Contract.objects.filter(id__in=contracts_list)
        else:
            data = Contract.objects.all()
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return render(request, 'contract/contracts_list.html', {'contracts': data,
                                                                    'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                    'username': auth.get_user(request).username})


class ContractPageView(View):
    def get(self, request, id):
        contract = get_object_or_404(Contract, id=id)
        risks = ContractRisk.objects.filter(tcr_tco_id=contract, tcr_end=None)
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return render(request, 'contract/contract_detail.html', {'contract': contract, 'risks': risks,
                                                                     'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                     'username': auth.get_user(request).username})


@login_required(login_url='/login/')
def contract_edit(request, id):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 5:
        return redirect('/')
    else:
        contract = get_object_or_404(Contract, id=id)
        if contract.tco_tcs_id_id in [8, 11]:
            return redirect('contract_detail', id=contract.id)
        else:
            statuses = []
            now = date.today()
            pre_date = now + relativedelta(years=contract.tco_length)
            if contract.tco_tcs_id_id == 9:
                statuses = ContractStatus.objects.exclude(pk=8)
            elif contract.tco_tcs_id_id == 3:
                statuses = ContractStatus.objects.filter(id__in=[3, 8])
            if request.method == "POST":
                status = request.POST.get('status', '')
                Contract.objects.filter(id=id).update(tco_tcs_id_id=status)
                if Contract.objects.get(id=id).tco_tcs_id_id == 3 and contract.tco_tcs_id_id != 3:
                    ContractDealer.objects.filter(tcd_tco_id=contract).update(tcd_start=now)
                    Contract.objects.filter(id=id).update(tco_start_date=now, tco_pre_end_date=pre_date)
                    ContractRisk.objects.filter(tcr_tco_id_id=contract.id).update(tcr_start=now)
                if Contract.objects.get(id=id).tco_tcs_id_id == 8:
                    ContractDealer.objects.filter(tcd_tco_id=contract, tcd_end=None).update(tcd_end=now)
                    Contract.objects.filter(id=id).update(tco_end_date=now)
                    ContractRisk.objects.filter(tcr_tco_id_id=contract.id, tcr_end=None).update(tcr_end=now)
                return redirect('contract_detail', id=contract.id)
            return render(request, 'contract/contract_edit.html', {'contract': contract,
                                                                   'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                   'username': auth.get_user(request).username,
                                                                   'statuses': statuses})


@login_required(login_url='/login/')
def contract_new(request):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 6:
        return redirect('/')
    else:
        args = {}
        args['form'] = ContractNewForm()
        series = ContractSeries.objects.all()
        freq = FreqPay.objects.all()
        now = date.today()
        dealer = Dealer.objects.get(tde_user_id=auth.get_user(request).id)
        if request.method == "POST":
            form = ContractNewForm(request.POST)
            surname = request.POST.get('surname', '')
            forename = request.POST.get('forename', '')
            middle = request.POST.get('middle', '')
            born_date = request.POST.get('born_date', '')
            main_doc = request.POST.get('main_doc', '')
            tco_length = request.POST.get('tco_length', '')
            contact = request.POST.get('contact', '')
            addr = request.POST.get('addr', '')
            mail = request.POST.get('mail', '')
            contract_series = request.POST.get('serie', '')
            freq_pay = request.POST.get('freq', '')
            if form.is_valid():
                if Person.objects.filter(tpr_main_doc=main_doc).count() == 0:
                    if Person.objects.count() == 0:
                        Person.objects.create(tpr_surname=surname, tpr_forename=forename,
                                              tpr_middle=middle, tpr_born_date=born_date,
                                              tpr_main_doc=main_doc).save()
                    else:
                        Person.objects.create(pk=Person.objects.latest('pk').pk + 1,
                                              tpr_surname=surname, tpr_forename=forename,
                                              tpr_middle=middle, tpr_born_date=born_date,
                                              tpr_main_doc=main_doc).save()
                    person = Person.objects.get(tpr_main_doc=main_doc)
                    serie = ContractSeries.objects.get(pk=contract_series)
                    freq = FreqPay.objects.get(pk=freq_pay)
                    if Contract.objects.count() == 0:
                        contract = Contract.objects.create(tco_tpr_id=person,
                                                           tco_number=1234567890,
                                                           tco_length=tco_length,
                                                           tco_tcss_id=serie,
                                                           tco_tfp_id=freq, tco_sign_date=now)
                    else:
                        contract = Contract.objects.create(pk=Contract.objects.latest('pk').pk + 1,
                                                           tco_tpr_id=person,
                                                           tco_number=Contract.objects.latest('pk').tco_number + 1,
                                                           tco_length=tco_length,
                                                           tco_tcss_id=serie,
                                                           tco_tfp_id=freq, tco_sign_date=now)
                    contract.save()
                    if ContractDealer.objects.count() == 0:
                        contractdeal = ContractDealer.objects.create(tcd_tco_id=contract,
                                                                     tcd_tde_id=dealer)
                    else:
                        contractdeal = ContractDealer.objects.create(pk=ContractDealer.objects.latest('pk').pk + 1,
                                                                     tcd_tco_id=contract,
                                                                     tcd_tde_id=dealer)
                    contractdeal.save()
                    if addr != '':
                        if Address.objects.count() == 0:
                            person_addr = Address.objects.create(addr_val=addr,
                                                                 addr_tat_id_id=1,
                                                                 addr_tpr_id=person)
                        else:
                            Address.objects.filter(addr_tat_id_id=1, addr_tpr_id=person).delete()
                            person_addr = Address.objects.create(pk=Address.objects.latest('pk').pk + 1,
                                                                 addr_val=addr,
                                                                 addr_tat_id_id=1,
                                                                 addr_tpr_id=person)
                        person_addr.save()
                    if contact != '':
                        if Contact.objects.count() == 0:
                            person_contact = Contact.objects.create(con_val=contact,
                                                                    con_tct_id_id=2,
                                                                    con_tpr_id=person)
                        else:
                            Contact.objects.filter(con_tct_id_id=2, con_tpr_id=person).delete()
                            person_contact = Contact.objects.create(pk=Contact.objects.latest('pk').pk + 1,
                                                                    con_val=contact,
                                                                    con_tct_id_id=2,
                                                                    con_tpr_id=person)
                        person_contact.save()
                    if mail != '':
                        if Contact.objects.count() == 0:
                            person_mail = Contact.objects.create(con_val=mail,
                                                                 con_tct_id_id=1,
                                                                 con_tpr_id=person)
                        else:
                            Contact.objects.filter(con_tct_id_id=1, con_tpr_id=person).delete()
                            person_mail = Contact.objects.create(pk=Contact.objects.latest('pk').pk + 1,
                                                                 con_val=mail,
                                                                 con_tct_id_id=1,
                                                                 con_tpr_id=person)
                        person_mail.save()
                    return redirect('contract_risks', id=contract.id)
                elif Person.objects.filter(tpr_main_doc=main_doc, tpr_surname=surname,
                                           tpr_forename=forename, tpr_middle=middle,
                                           tpr_born_date=born_date).count() == 0:
                    args['login_error'] = 'С такими паспортными данными зарегистрирован другой человек'
                    return render(request, 'contract/contract_new.html', {'form': form, 'args': args,
                                                                          'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                          'username': auth.get_user(request).username,
                                                                          'series': series, 'freqs': freq})
                else:
                    person = Person.objects.get(tpr_main_doc=main_doc)
                    if person.tpr_unprofit is True or person.tpr_psycho is True:
                        args['login_error'] = 'Психические отклонения или убыточный'
                        return render(request, 'contract/contract_new.html', {'form': form, 'args': args,
                                                                              'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                              'username': auth.get_user(request).username,
                                                                              'series': series, 'freqs': freq})
                    else:
                        serie = ContractSeries.objects.get(pk=contract_series)
                        freq = FreqPay.objects.get(pk=freq_pay)
                        if Contract.objects.all().count() == 0:
                            contract = Contract.objects.create(tco_tpr_id=person,
                                                               tco_number=1234567890,
                                                               tco_length=tco_length,
                                                               tco_tcss_id=serie,
                                                               tco_tfp_id=freq, tco_sign_date=now)
                        else:
                            contract = Contract.objects.create(pk=Contract.objects.latest('pk').pk + 1,
                                                               tco_tpr_id=person,
                                                               tco_number=Contract.objects.latest('pk').tco_number + 1,
                                                               tco_length=tco_length, tco_tcss_id=serie,
                                                               tco_tfp_id=freq, tco_sign_date=now)
                        contract.save()
                        if ContractDealer.objects.count() == 0:
                            contractdeal = ContractDealer.objects.create(tcd_tco_id=contract,
                                                                         tcd_tde_id=dealer)
                        else:
                            contractdeal = ContractDealer.objects.create(pk=ContractDealer.objects.latest('pk').pk + 1,
                                                                         tcd_tco_id=contract,
                                                                         tcd_tde_id=dealer)
                        contractdeal.save()
                        if addr != '':
                            if Address.objects.count() == 0:
                                person_addr = Address.objects.create(addr_val=addr,
                                                                     addr_tat_id_id=1,
                                                                     addr_tpr_id=person)
                            else:
                                Address.objects.filter(addr_tat_id_id=1, addr_tpr_id=person).delete()
                                person_addr = Address.objects.create(pk=Address.objects.latest('pk').pk + 1,
                                                                     addr_val=addr,
                                                                     addr_tat_id_id=1,
                                                                     addr_tpr_id=person)
                            person_addr.save()
                            if contact != '':
                                if Contact.objects.count() == 0:
                                    person_contact = Contact.objects.create(con_val=contact,
                                                                            con_tct_id_id=2,
                                                                            con_tpr_id=person)
                                else:
                                    Contact.objects.filter(con_tct_id_id=2, con_tpr_id=person).delete()
                                    person_contact = Contact.objects.create(pk=Contact.objects.latest('pk').pk + 1,
                                                                            con_val=contact,
                                                                            con_tct_id_id=2,
                                                                            con_tpr_id=person)
                                person_contact.save()
                            if mail != '':
                                if Contact.objects.count() == 0:
                                    person_mail = Contact.objects.create(con_val=mail,
                                                                         con_tct_id_id=1,
                                                                         con_tpr_id=person)
                                else:
                                    Contact.objects.filter(con_tct_id_id=1, con_tpr_id=person).delete()
                                    person_mail = Contact.objects.create(pk=Contact.objects.latest('pk').pk + 1,
                                                                         con_val=mail,
                                                                         con_tct_id_id=1,
                                                                         con_tpr_id=person)
                                person_mail.save()
                        return redirect('contract_risks', id=contract.id)
        else:
            form = ContractNewForm()
        return render(request, 'contract/contract_new.html', {'form': form, 'args': args,
                                                              'username': auth.get_user(request).username,
                                                              'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                              'series': series, 'freqs': freq})


@login_required(login_url='/login/')
def contract_risks(request, id):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 6:
        return redirect('/')
    else:
        contract = get_object_or_404(Contract, id=id)
        class ContractRisks(forms.Form):
                risks = Risk.objects.filter(rsk_tcss_id=contract.tco_tcss_id)
                risks_choices = list()
                for risk in risks:
                    risks_choices.append((risk.id, risk.rsk_name))
                contract_risks = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=risks_choices)
                contract_sum = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.TextInput(attrs={"size": 40}))
        args = {}
        args['form'] = ContractRisks()
        if ContractRisk.objects.filter(tcr_tco_id=contract).count() != 0:
            return redirect('contract_detail', id=contract.id)
        else:
            if request.method == "POST":
                form = ContractRisks(request.POST)
                my_data = request.POST.getlist('contract_risks', '')
                contract_sum = request.POST.get('contract_sum', '')
                if form.is_valid():
                    sum = 0
                    str_sum = 0
                    prem_sum = 0
                    contr_sum = float(contract_sum)
                    for z in my_data:
                        risk = Risk.objects.get(pk=z)
                        sum += risk.rsk_proportion
                    for i in my_data:
                        risk = Risk.objects.get(pk=i)
                        tcr_sum = contr_sum*risk.rsk_proportion/sum
                        tcr_prem = float(risk.rsk_ins_proportion) * float(contract.tco_length) * tcr_sum
                        if ContractRisk.objects.all().count() == 0:
                            contract_risk = ContractRisk.objects.create(tcr_rsk_id=risk,
                                                                        tcr_tco_id=contract,
                                                                        tcr_sum=tcr_sum,
                                                                        tcr_str_sum=tcr_prem)
                        else:
                            contract_risk = ContractRisk.objects.create(pk=ContractRisk.objects.latest('pk').pk + 1,
                                                                        tcr_rsk_id=risk,
                                                                        tcr_tco_id=contract,
                                                                        tcr_sum=tcr_sum,
                                                                        tcr_str_sum=tcr_prem)
                        contract_risk.save()
                        sum -= risk.rsk_proportion
                        contr_sum -= contract_risk.tcr_sum
                        str_sum += contract_risk.tcr_str_sum
                        prem_sum += contract_risk.tcr_sum
                    template = "MyGW/InsCompany/static/doc/template.docx"
                    document = MailMerge(template)
                    risks = ''
                    for z in my_data:
                        risk = Risk.objects.get(pk=z)
                        risks += risk.rsk_name + ','
                    contacts = ''
                    person_contacts = Contact.objects.filter(con_tpr_id=contract.tco_tpr_id)
                    for z in person_contacts:
                        contacts += z.con_val + ','
                    if Address.objects.filter(addr_tat_id_id=1, addr_tpr_id=contract.tco_tpr_id).count() != 0:
                        person_address = Address.objects.get(addr_tat_id_id=1, addr_tpr_id=contract.tco_tpr_id).addr_val
                    else:
                        person_address = ''
                    contract_dealer = ContractDealer.objects.get(tcd_tco_id=contract, tcd_end=None)
                    document.merge(
                        strax_sum=str(float("{0:.2f}".format(str_sum))),
                        prem_sum=str(float("{0:.2f}".format(prem_sum))),
                        risks=str(risks[0:-1]),
                        length=str(contract.tco_length),
                        contacts=str(contacts[0:-1]),
                        freq_pay=str(contract.tco_tfp_id.tfp_val),
                        address=str(person_address),
                        dealer=str(contract_dealer.tcd_tde_id.tde_tpr_id.tpr_surname + ' ' +
                                   contract_dealer.tcd_tde_id.tde_tpr_id.tpr_forename + ' ' +
                                   contract_dealer.tcd_tde_id.tde_tpr_id.tpr_middle),
                        passport=str(contract.tco_tpr_id.tpr_main_doc),
                        number=str(contract.tco_number),
                        product=str(contract.tco_tcss_id.tcss_val + '-' + contract.tco_tcss_id.tcss_desc),
                        date_sign=str(contract.tco_sign_date),
                        FIO=str(contract.tco_tpr_id.tpr_surname + ' ' + contract.tco_tpr_id.tpr_forename
                                                                + ' ' + contract.tco_tpr_id.tpr_middle),
                        born_date=str(contract.tco_tpr_id.tpr_born_date))
                    doc_name = 'MyGW/InsCompany/media/docs/application_' + str(contract.tco_number) + '.docx'
                    document.write(doc_name)
                    Contract.objects.filter(pk=id).update(tco_app_original='/'+doc_name)
                    return redirect('contract_detail', id=contract.id)
            else:
                form = ContractRisks()
            return render(request, 'contract/contract_risks.html', {'form': form, 'args': args,
                                                                    'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                    'username': auth.get_user(request).username})


class PersonsPageView(View):
    def get(self, request):
        if auth.get_user(request).groups.get(user=auth.get_user(request)).id == 6:
            dealer = Dealer.objects.get(tde_user_id=auth.get_user(request).id)
            deal_contracts = ContractDealer.objects.filter(tcd_tde_id=dealer, tcd_end=None)
            contracts_list = list()
            for contract in deal_contracts:
                contracts_list.append(contract.tcd_tco_id.id)
            contracts = Contract.objects.filter(id__in=contracts_list)
            person_list = list()
            for i in contracts:
                person_list.append(i.tco_tpr_id_id)
            data = Person.objects.filter(id__in=person_list)
        else:
            person_list = list()
            for i in Contract.objects.all():
                person_list.append(i.tco_tpr_id_id)
            data = Person.objects.filter(id__in=person_list)
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return render(request, 'person/persons_list.html', {'persons': data,
                                                                'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                'username': auth.get_user(request).username})


class PersonPageView(View):
    def get(self, request, id):
        person = get_object_or_404(Person, id=id)
        contracts = Contract.objects.filter(tco_tpr_id=person)
        contacts = Contact.objects.filter(con_tpr_id=person)
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return render(request, 'person/person_detail.html', {'person': person, 'contracts': contracts,
                                                                 'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                 'username': auth.get_user(request).username,
                                                                 'contacts': contacts})


@login_required(login_url='/login/')
def person_edit(request, id):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 5:
        return redirect('/')
    else:
        person = get_object_or_404(Person, id=id)
        if request.method == "POST":
            form = PersonForm(request.POST, instance=person)
            if form.is_valid():
                person = form.save(commit=False)
                person.save()
                return redirect('person_detail', id=person.id)
        else:
            form = PersonForm(instance=person)
        return render(request, 'person/person_edit.html', {'form': form, 'person': person,
                                                           'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                           'username': auth.get_user(request).username})


@login_required(login_url='/login/')
def insevent_new(request):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 6:
        return redirect('/')
    else:
        args = {}
        args['form'] = NewInsEvent()
        contracts = Contract.objects.filter(tco_tcs_id_id__in=[3, 8])
        now = date.today()
        if request.method == "POST":
            form = NewInsEvent(request.POST)
            tiv_date = request.POST.get('tiv_date', '')
            tiv_time = request.POST.get('tiv_time', '')
            tiv_desc = request.POST.get('tiv_desc', '')
            tiv_contract = request.POST.get('contract', '')
            if form.is_valid():
                if ContractRisk.objects.filter(Q(tcr_tco_id_id=tiv_contract),
                                               Q(tcr_end__gte=tiv_date) | Q(tcr_end=None),
                                               Q(tcr_start__lte=tiv_date)).count() == 0:
                    args['login_error'] = 'Нет действующих рисков на дату страхового события'
                    return render(request, 'user/worker_new.html', {'form': form, 'args': args,
                                                                    'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                    'username': auth.get_user(request).username,
                                                                    'contracts': contracts})
                else:
                    if InsEvent.objects.count() == 0:
                        event = InsEvent.objects.create(tiv_tco_id_id=tiv_contract,
                                                        tiv_date=tiv_date,
                                                        tiv_time=tiv_time,
                                                        tiv_desc=tiv_desc,
                                                        tiv_app_date=now)
                    else:
                        event = InsEvent.objects.create(pk=InsEvent.objects.latest('pk').pk + 1,
                                                        tiv_tco_id_id=tiv_contract,
                                                        tiv_date=tiv_date,
                                                        tiv_time=tiv_time,
                                                        tiv_desc=tiv_desc,
                                                        tiv_app_date=now)
                    event.save()
                    contract_risks = ContractRisk.objects.filter(Q(tcr_tco_id_id=tiv_contract),
                                                                 Q(tcr_end__gte=tiv_date) | Q(tcr_end=None),
                                                                 Q(tcr_start__lte=tiv_date))
                    for contract_risk in contract_risks:
                        if ElemClaim.objects.count() == 0:
                            elclaim = ElemClaim.objects.create(tel_rsk_id_id=contract_risk.tcr_rsk_id_id,
                                                               tel_sum=contract_risk.tcr_str_sum,
                                                               tel_tiv_id=event)
                        else:
                            elclaim = ElemClaim.objects.create(pk=ElemClaim.objects.latest('pk').pk + 1,
                                                               tel_rsk_id_id=contract_risk.tcr_rsk_id_id,
                                                               tel_sum=contract_risk.tcr_str_sum,
                                                               tel_tiv_id=event)
                        elclaim.save()
                    return redirect('event_detail', id=event.id)
        else:
            form = NewInsEvent()
        return render(request, 'event/event_new.html', {'form': form, 'args': args,
                                                        'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                        'username': auth.get_user(request).username,
                                                        'contracts': contracts})


class EventsPageView(View):
    def get(self, request):
        if auth.get_user(request).groups.get(user=auth.get_user(request)).id == 6:
            dealer = Dealer.objects.get(tde_user_id=auth.get_user(request).id)
            deal_contracts = ContractDealer.objects.filter(tcd_tde_id=dealer, tcd_end=None)
            contracts_list = list()
            for contract in deal_contracts:
                contracts_list.append(contract.tcd_tco_id.id)
            contracts = Contract.objects.filter(id__in=contracts_list)
            data = InsEvent.objects.filter(tiv_tco_id__in=contracts)
        else:
            data = InsEvent.objects.all()
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return render(request, 'event/events_list.html', {'events': data,
                                                              'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                              'username': auth.get_user(request).username})


class EventPageView(View):
    def get(self, request, id):
        event = get_object_or_404(InsEvent, id=id)
        elemclaims = ElemClaim.objects.filter(tel_tiv_id=event)
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return render(request, 'event/event_detail.html', {'event': event,
                                                               'elemclaims': elemclaims,
                                                               'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                               'username': auth.get_user(request).username})


@login_required(login_url='/login/')
def dealer_new(request):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 1:
        return redirect('/')
    else:
        args = {}
        args['form'] = DealerNewForm()
        if request.method == "POST":
            form = DealerNewForm(request.POST, request.FILES)
            surname = request.POST.get('surname', '')
            forename = request.POST.get('forename', '')
            middle = request.POST.get('middle', '')
            born_date = request.POST.get('born_date', '')
            main_doc = request.POST.get('main_doc', '')
            tde_start = request.POST.get('tde_start', '')
            user_login = request.POST.get('user_login', '')
            work_mail = request.POST.get('work_mail', '')
            if form.is_valid():
                if User.objects.filter(username=user_login).count() != 0:
                    args['login_error'] = 'Такой логин занят'
                    return render(request, 'user/dealer_new.html', {'form': form, 'args': args,
                                                                    'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                    'username': auth.get_user(request).username})
                else:
                    if Person.objects.filter(tpr_main_doc=main_doc).count() != 0 and \
                       Person.objects.filter(tpr_main_doc=main_doc, tpr_surname=surname,
                                             tpr_forename=forename, tpr_middle=middle,
                                             tpr_born_date=born_date).count() == 0:
                            args['login_error'] = 'С такими паспортными данными зарегистрирован другой человек'
                            return render(request, 'user/dealer_new.html', {'form': form, 'args': args,
                                                                            'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                            'username': auth.get_user(request).username})
                    else:
                        if Person.objects.filter(tpr_main_doc=main_doc).count() == 0:
                            if Person.objects.count() == 0:
                                Person.objects.create(tpr_surname=surname, tpr_forename=forename,
                                                      tpr_middle=middle, tpr_born_date=born_date,
                                                      tpr_main_doc=main_doc).save()
                            else:
                                Person.objects.create(pk=Person.objects.latest('pk').pk + 1,
                                                      tpr_surname=surname, tpr_forename=forename,
                                                      tpr_middle=middle, tpr_born_date=born_date,
                                                      tpr_main_doc=main_doc).save()
                            person = Person.objects.get(tpr_main_doc=main_doc)
                        else:
                            person = Person.objects.get(tpr_main_doc=main_doc)
                        passwd = User.objects.make_random_password()
                        user = User.objects.create_user(username=user_login, email=work_mail, password=passwd)
                        user.save()
                        if Dealer.objects.count() == 0:
                            dealer = Dealer.objects.create(tde_tpr_id=person,
                                                           tde_number=4561237890,
                                                           tde_start=tde_start,
                                                           tde_user_id=user)
                        else:
                            dealer = Dealer.objects.create(pk=Dealer.objects.latest('pk').pk + 1,
                                                           tde_tpr_id=person,
                                                           tde_number=Dealer.objects.latest('pk').tde_number + 1,
                                                           tde_start=tde_start,
                                                           tde_user_id=user)
                        dealer.save()
                        smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
                        smtpObj.starttls()
                        smtpObj.login('InsCompany@list.ru', '135246qwe')
                        SUBJECT = "Your login and password"
                        FROM = "InsCompany@list.ru"
                        TO = work_mail
                        BODY = "\r\n".join((
                            "From: %s" % FROM,
                            "To: %s" % TO,
                            "Subject: %s" % SUBJECT,
                            "",
                            'Your login: ' + user_login + '\n' +
                            'Your password: ' + passwd + '\n' +
                            'Your dealer number: ' + str(dealer.tde_number) + '\n' +
                            'Your dear InsCompany'
                        ))
                        smtpObj.sendmail(FROM, [TO], BODY)
                        smtpObj.quit()
                        if WorkerPhoto.objects.count() == 0:
                            w_photo = WorkerPhoto.objects.create(wp_user_id=user,
                                                                 wp_photo=request.FILES['photo'])
                        else:
                            w_photo = WorkerPhoto.objects.create(pk=WorkerPhoto.objects.latest('pk').pk + 1,
                                                                 wp_user_id=user,
                                                                 wp_photo=request.FILES['photo'])
                        w_photo.save()
                        Group.objects.get(id=6).user_set.add(user)
                        return redirect('/')
        else:
            form = DealerNewForm()
        return render(request, 'user/dealer_new.html', {'form': form, 'args': args,
                                                        'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                        'username': auth.get_user(request).username})


@login_required(login_url='/login/')
def worker_new(request):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 1:
        return redirect('/')
    else:
        args = {}
        args['form'] = NewWorker()
        group_choices = Group.objects.exclude(pk=6)
        if request.method == "POST":
            form = NewWorker(request.POST, request.FILES)
            user_login = request.POST.get('user_login', '')
            work_mail = request.POST.get('work_mail', '')
            group = request.POST.get('group', '')
            if form.is_valid():
                if User.objects.filter(username=user_login).count() != 0:
                    args['login_error'] = 'Такой логин занят'
                    return render(request, 'user/worker_new.html', {'form': form, 'args': args,
                                                                    'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                    'username': auth.get_user(request).username,
                                                                    'groups': group_choices})
                else:
                    passwd = User.objects.make_random_password()
                    user = User.objects.create_user(username=user_login, email=work_mail, password=passwd)
                    user.save()
                    smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
                    smtpObj.starttls()
                    smtpObj.login('InsCompany@list.ru', '135246qwe')
                    SUBJECT = "Your login and password"
                    FROM = "InsCompany@list.ru"
                    TO = work_mail
                    BODY = "\r\n".join((
                        "From: %s" % FROM,
                        "To: %s" % TO,
                        "Subject: %s" % SUBJECT,
                        "",
                        'Your login: ' + user_login + '\n' +
                        'Your password: ' + passwd + '\n' +
                        'Your dear InsCompany'
                        ))
                    smtpObj.sendmail(FROM, [TO], BODY)
                    smtpObj.quit()
                    if WorkerPhoto.objects.count() == 0:
                        w_photo = WorkerPhoto.objects.create(wp_user_id=user,
                                                             wp_photo=request.FILES['photo'])
                    else:
                        w_photo = WorkerPhoto.objects.create(pk=WorkerPhoto.objects.latest('pk').pk + 1,
                                                             wp_user_id=user,
                                                             wp_photo=request.FILES['photo'])
                    w_photo.save()
                    Group.objects.get(id=group).user_set.add(user)
                    return redirect('/')
        else:
            form = NewWorker()
        return render(request, 'user/worker_new.html', {'form': form, 'args': args,
                                                        'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                        'username': auth.get_user(request).username,
                                                        'groups': group_choices})


class ElemClaimsPageView(View):
    def get(self, request):
        if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 3:
            return redirect('/')
        else:
            data = ElemClaim.objects.all()
            if not request.user.is_authenticated:
                return redirect('login')
            else:
                return render(request, 'elemclaim/elemclaims_list.html', {'elemclaims': data,
                                                                          'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                          'username': auth.get_user(request).username})


class ElemClaimPageView(View):
    def get(self, request, id):
        if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 3:
            return redirect('/')
        else:
            elemclaim = get_object_or_404(ElemClaim, id=id)
            if not request.user.is_authenticated:
                return redirect('login')
            else:
                return render(request, 'elemclaim/elemclaim_detail.html', {'elemclaim': elemclaim,
                                                                           'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                           'username': auth.get_user(request).username})


@login_required(login_url='/login/')
def elemclaim_edit(request, id):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 3:
        return redirect('/')
    else:
        elemclaim = get_object_or_404(ElemClaim, id=id)
        if elemclaim.tel_tcs_id_id in [3, 4]:
            return redirect('elemclaim_detail', id=elemclaim.id)
        else:
            statuses = []
            if elemclaim.tel_tcs_id_id == 1:
                statuses = ClaimStatus.objects.exclude(pk=4)
            elif elemclaim.tel_tcs_id_id == 2:
                statuses = ClaimStatus.objects.exclude(pk=1)
            if request.method == "POST":
                status = request.POST.get('status', '')
                form = ElemClaimForm(request.POST, instance=elemclaim)
                if form.is_valid():
                    elemclaim = form.save(commit=False)
                    elemclaim.save()
                    if elemclaim.tel_tcs_id_id != status:
                        ElemClaim.objects.filter(id=id).update(tel_tcs_id_id=status)
                    insevent = InsEvent.objects.get(pk=elemclaim.tel_tiv_id_id)
                    elclaims_statuses = list()
                    for i in ElemClaim.objects.filter(tel_tiv_id=insevent):
                        elclaims_statuses.append(i.tel_tcs_id_id)
                    el_statuses = {}
                    el_statuses['1'] = elclaims_statuses.count(1)
                    el_statuses['2'] = elclaims_statuses.count(2)
                    el_statuses['3'] = elclaims_statuses.count(3)
                    el_statuses['4'] = elclaims_statuses.count(4)
                    el_statuses['all'] = el_statuses['1'] + el_statuses['2'] + el_statuses['3'] + el_statuses['4']
                    if el_statuses['3'] + el_statuses['4'] == el_statuses['all']:
                        if el_statuses['3'] == el_statuses['all']:
                            InsEvent.objects.filter(pk=elemclaim.tel_tiv_id_id).update(tiv_tcs_id_id=3)
                        else:
                            InsEvent.objects.filter(pk=elemclaim.tel_tiv_id_id).update(tiv_tcs_id_id=4)
                            sum = 0
                            for i in ElemClaim.objects.filter(tel_tiv_id=insevent, tel_tcs_id_id=4):
                                sum += i.tel_sum_fact
                            if Payout.objects.count() == 0:
                                Payout.objects.create(tpo_tiv_id=insevent,
                                                      tpo_sum=sum)
                            else:
                                Payout.objects.create(pk=Payout.objects.latest('pk').pk + 1,
                                                      tpo_tiv_id=insevent,
                                                      tpo_sum=sum)
                    else:
                        if el_statuses['1'] != el_statuses['all']:
                            InsEvent.objects.filter(pk=elemclaim.tel_tiv_id_id).update(tiv_tcs_id_id=2)
                    return redirect('elemclaim_detail', id=elemclaim.id)
            else:
                form = ElemClaimForm(instance=elemclaim)
            return render(request, 'elemclaim/elemclaim_edit.html', {'form': form, 'elemclaim': elemclaim,
                                                                     'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                                     'username': auth.get_user(request).username,
                                                                     'statuses': statuses})


@login_required(login_url='/login/')
def contact_new(request):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 6:
        return redirect('/')
    else:
        contact_types = ContactType.objects.all()
        person_list = list()
        for i in Contract.objects.all():
            person_list.append(i.tco_tpr_id_id)
        persons = Person.objects.filter(id__in=person_list)
        if request.method == "POST":
            contact = request.POST.get('contact', '')
            person = request.POST.get('person', '')
            type = request.POST.get('type', '')
            form = NewContact(request.POST)
            if form.is_valid():
                Contact.objects.filter(con_tpr_id_id=person, con_tct_id_id=type).delete()
                if Contact.objects.count() == 0:
                    person_contact = Contact.objects.create(con_tct_id_id=type,
                                                            con_tpr_id_id=person,
                                                            con_val=contact)
                else:
                    person_contact = Contact.objects.create(pk=Contact.objects.latest('pk').pk + 1,
                                                            con_tct_id_id=type,
                                                            con_tpr_id_id=person,
                                                            con_val=contact)
                person_contact.save()
                return redirect('person_detail', id=person_contact.con_tpr_id_id)
        else:
            form = NewContact()
        return render(request, 'person/person_contact.html', {'form': form,
                                                              'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                              'username': auth.get_user(request).username,
                                                              'contacts_types': contact_types,
                                                              'persons': persons})


@login_required(login_url='/login/')
def document_new(request):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 6:
        return redirect('/')
    else:
        document_types = DocumentType.objects.all()
        person_list = list()
        for i in Contract.objects.all():
            person_list.append(i.tco_tpr_id_id)
        persons = Person.objects.filter(id__in=person_list)
        if request.method == "POST":
            doc = request.POST.get('doc_num', '')
            person = request.POST.get('person', '')
            type = request.POST.get('type', '')
            series = request.POST.get('series', '')
            issue_date = request.POST.get('issue_date', '')
            issue_org = request.POST.get('issue_org', '')
            form = NewDocument(request.POST)
            if form.is_valid():
                Document.objects.filter(doc_tpr_id_id=person, doc_tdt_id_id=type).delete()
                if Document.objects.count() == 0:
                    document = Document.objects.create(doc_tdt_id_id=type,
                                                       doc_tpr_id_id=person,
                                                       doc_series=series,
                                                       doc_number=doc,
                                                       doc_issue_date=issue_date,
                                                       doc_issue_org=issue_org)
                else:
                    document = Document.objects.create(pk=Contact.objects.latest('pk').pk + 1,
                                                       doc_tdt_id_id=type,
                                                       doc_tpr_id_id=person,
                                                       doc_series=series,
                                                       doc_number=doc,
                                                       doc_issue_date=issue_date,
                                                       doc_issue_org=issue_org)
                document.save()
                return redirect('person_detail', id=document.doc_tpr_id_id)
        else:
            form = NewDocument()
        return render(request, 'person/person_document.html', {'form': form,
                                                               'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                               'username': auth.get_user(request).username,
                                                               'document_types': document_types,
                                                               'persons': persons})


@login_required(login_url='/login/')
def address_new(request):
    if auth.get_user(request).groups.get(user=auth.get_user(request)).id != 6:
        return redirect('/')
    else:
        address_types = AddressType.objects.all()
        person_list = list()
        for i in Contract.objects.all():
            person_list.append(i.tco_tpr_id_id)
        persons = Person.objects.filter(id__in=person_list)
        if request.method == "POST":
            addr = request.POST.get('address', '')
            person = request.POST.get('person', '')
            type = request.POST.get('type', '')
            form = NewAddress(request.POST)
            if form.is_valid():
                Address.objects.filter(addr_tpr_id_id=person, addr_tat_id_id=type).delete()
                if Address.objects.count() == 0:
                    address = Address.objects.create(addr_tat_id_id=type,
                                                     addr_tpr_id_id=person,
                                                     addr_val=addr)
                else:
                    address = Address.objects.create(pk=Address.objects.latest('pk').pk + 1,
                                                     addr_tat_id_id=type,
                                                     addr_tpr_id_id=person,
                                                     addr_val=addr)
                address.save()
                return redirect('person_detail', id=address.addr_tpr_id_id)
        else:
            form = NewAddress()
        return render(request, 'person/person_address.html', {'form': form,
                                                              'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                                              'username': auth.get_user(request).username,
                                                              'address_types': address_types,
                                                              'persons': persons})


def searching(request):
    statuses = ContractStatus.objects.all()
    series = ContractSeries.objects.all()
    if request.method == 'POST':
        group_by = request.POST.get('group_by', '')
        status = request.POST.get('status', '')
        serie = request.POST.get('serie', '')
        if serie == '':
            param1 = '0 = 0'
        else:
            param1 = 'tco_tcss_id_id = ' + serie
        if status == '':
            param2 = '0 = 0'
        else:
            param2 = 'tco_tcs_id_id = ' + status
        if int(group_by) == 1:
            query = 'select tcss_val as val, count(*) as tco_count from "InsCompany_contract" ' \
                    'join "InsCompany_contractseries" ICc on "InsCompany_contract".tco_tcss_id_id = ICc.id ' \
                    'where ' + param1 + \
                    ' and ' + param2 + \
                    ' group by tcss_val'
        else:
            query = 'select tcs_val as val, count(*) as tco_count from "InsCompany_contract" ' \
                    'join "InsCompany_contractstatus" ICc on "InsCompany_contract".tco_tcs_id_id = ICc.id ' \
                    'where ' + param1 + \
                    ' and ' + param2 + \
                    ' group by tcs_val'
        print(query)
        cursor = connection.cursor()
        cursor.execute(query)
        data = dictfetchall(cursor)
        return render(request, 'search.html', {'param': group_by,
                                               'statuses': statuses,
                                               'series': series,
                                               'username': auth.get_user(request).username,
                                               'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                               'data': data})

    return render(request, 'search.html', {'statuses': statuses,
                                           'series': series,
                                           'group': auth.get_user(request).groups.get(user=auth.get_user(request)).id,
                                           'username': auth.get_user(request).username})


class ReportPageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            user = auth.get_user(request)
            return render(request, 'reports.html', {'username': user.username,
                                                    'group': user.groups.get(user=auth.get_user(request)).id})
