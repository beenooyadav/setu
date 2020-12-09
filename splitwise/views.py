from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Value, F
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from splitwise.models import TransactionLog


@login_required
@require_GET
def get_all_transactions(request):
    """
    :param request: user must be logged in
    :return: all unsettled transactions of logged in user and summary
    """
    current_contact = request.user
    all_transactions = TransactionLog.objects.filter(Q(contact_a=current_contact) | Q(contact_b=current_contact),
                                                     is_settled=False).order_by('-created_time').values()

    resp = all_transactions_util(all_transactions, current_contact)
    resp.update(current_user_id=current_contact.id)
    return JsonResponse(resp, status=200)


@login_required
@require_GET
def get_transaction_of_contact(request):
    """
    :param request: logged in user, contact_id: id of contact with whom we need all transactions
    :return: all unsettled transactions of logged in user with given contact and summary
    """
    current_contact = request.user
    contact_id = int(request.GET.get('contact_id'))
    all_transactions = TransactionLog.objects.filter(Q(contact_a=current_contact, contact_b_id=contact_id)
                                                     | Q(contact_a_id=contact_id, contact_b=current_contact), is_settled=False).\
        order_by('-created_time').values()
    resp = all_transactions_util(all_transactions, current_contact)
    resp.update(current_user_id=current_contact.id, with_contact_id=contact_id)
    return JsonResponse(resp, status=200)


@login_required
@require_POST
def add_transaction(request):
    """
    :param request: logged in user, contact_id: id of contact with whom this transaction happened
    amount: transaction amount, is_borrowed: True in case of logged in user is borrower
    :return: ok
    """
    contact_id = int(request.POST.get('contact_id'))
    amount = float(request.POST.get('amount'))
    borrowed = request.POST.get('is_borrowed') == 'True'

    contact_b, created = User.objects.get_or_create(id=contact_id)
    contact_a = contact_b if borrowed else request.user
    contact_b = request.user if borrowed else contact_b
    if contact_a.id == contact_b.id:
        pass
    else:
        TransactionLog.objects.create(contact_a=contact_a, contact_b=contact_b, amount=amount)
    return JsonResponse(dict(success='OK'), status=200)


@login_required
@require_POST
def delete_transaction(request):
    """
    :param request: logged in user, transaction_id: transaction_id of transaction which need too be deleted
    :return: ok or error
    """
    transaction_id = int(request.POST.get('transaction_id'))
    TransactionLog.objects.filter(id=transaction_id).update(is_settled=True)
    return JsonResponse(dict(success='OK'), status=200)


@login_required
@require_POST
def settle(request):
    """
    :param request: logged in user, contact_id: id of contact with whom this transactions need to be settled
    :return: ok
    """
    current_contact = request.user
    contact_id = int(request.POST.get('contact_id'))
    TransactionLog.objects.filter(Q(contact_a=current_contact, contact_b_id=contact_id) |
                                  Q(contact_a_id=contact_id, contact_b=current_contact)).update(is_settled=True)
    return JsonResponse(dict(success='OK'), status=200)


def all_transactions_util(all_transactions, current_contact):
    total_borrowed = 0
    total_owed = 0
    for transaction in all_transactions:
        is_borrowed = transaction['contact_b_id'] == current_contact.id
        transaction['is_borrowed'] = is_borrowed
        if is_borrowed:
            total_borrowed += transaction['amount']
        else:
            total_owed += transaction['amount']
    is_overall_borrowed = total_borrowed > total_owed
    resp = dict(borrowed=total_borrowed, owed=total_owed, is_overall_borrowed=is_overall_borrowed,
                borrowed_owed_amount=abs(total_owed - total_borrowed), transactions=list(all_transactions))
    return resp