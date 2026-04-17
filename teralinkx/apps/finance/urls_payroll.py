# apps/finance/urls_payroll.py
from django.urls import path
from .views_credit_note import CreditNoteListView, CreditNoteDetailView
from .views_payroll import (
    EmployeeListView, EmployeeDetailView,
    PayrollRunView, PayrollRunDetailView, PayrollCalculatorView
)

urlpatterns = [
    # Credit Notes
    path('credit-notes/',              CreditNoteListView.as_view(),    name='credit-note-list'),
    path('credit-notes/<int:cn_id>/',  CreditNoteDetailView.as_view(),  name='credit-note-detail'),

    # Employees
    path('employees/',                 EmployeeListView.as_view(),      name='employee-list'),
    path('employees/<int:emp_id>/',    EmployeeDetailView.as_view(),    name='employee-detail'),

    # Payroll
    path('payroll/',                   PayrollRunView.as_view(),        name='payroll-list'),
    path('payroll/<int:run_id>/',      PayrollRunDetailView.as_view(),  name='payroll-detail'),
    path('payroll/calculator/',        PayrollCalculatorView.as_view(), name='payroll-calculator'),
]
