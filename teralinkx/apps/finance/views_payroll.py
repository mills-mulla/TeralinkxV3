# apps/finance/views_payroll.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from finance.models_payroll import Employee, PayrollRun, PayslipItem, PayrollCalculator


def _emp(e):
    return {
        'id': e.id,
        'employee_number': e.employee_number,
        'full_name': e.full_name,
        'job_title': e.job_title,
        'department': e.department.name if e.department else None,
        'employment_type': e.employment_type,
        'gross_salary': float(e.gross_salary),
        'is_active': e.is_active,
        'start_date': e.start_date.isoformat(),
        'kra_pin': e.kra_pin,
        'nhif_number': e.nhif_number,
        'nssf_number': e.nssf_number,
        'bank_name': e.bank_name,
        'bank_account': e.bank_account,
    }


def _run(r):
    return {
        'id': r.id,
        'period_label': r.period_label,
        'period_month': r.period_month,
        'period_year': r.period_year,
        'total_gross': float(r.total_gross),
        'total_paye': float(r.total_paye),
        'total_nhif': float(r.total_nhif),
        'total_nssf_employee': float(r.total_nssf_employee),
        'total_nssf_employer': float(r.total_nssf_employer),
        'total_net': float(r.total_net),
        'total_cost': float(r.total_cost),
        'status': r.status,
        'status_display': r.get_status_display(),
        'employee_count': r.payslips.count(),
    }


class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employees = Employee.objects.select_related('department').filter(is_active=True)
        return Response({'count': employees.count(), 'results': [_emp(e) for e in employees]})

    def post(self, request):
        try:
            from finance.models import Department
            dept = Department.objects.filter(id=request.data.get('department_id')).first()
            emp = Employee.objects.create(
                employee_number = Employee.generate_number(),
                first_name      = request.data['first_name'],
                last_name       = request.data['last_name'],
                id_number       = request.data['id_number'],
                kra_pin         = request.data.get('kra_pin', ''),
                nhif_number     = request.data.get('nhif_number', ''),
                nssf_number     = request.data.get('nssf_number', ''),
                job_title       = request.data.get('job_title', ''),
                employment_type = request.data.get('employment_type', 'full_time'),
                gross_salary    = request.data['gross_salary'],
                start_date      = request.data['start_date'],
                bank_name       = request.data.get('bank_name', ''),
                bank_account    = request.data.get('bank_account', ''),
                phone_number    = request.data.get('phone_number', ''),
                email           = request.data.get('email', ''),
                department      = dept,
            )
            return Response(_emp(emp), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, emp_id):
        try:
            e = Employee.objects.get(id=emp_id)
            data = _emp(e)
            # Include payslip preview
            data['payslip_preview'] = PayrollCalculator.calculate_payslip(e)['breakdown']
            return Response(data)
        except Employee.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, emp_id):
        try:
            e = Employee.objects.get(id=emp_id)
            for field in ['first_name', 'last_name', 'job_title', 'gross_salary',
                          'bank_name', 'bank_account', 'kra_pin', 'nhif_number',
                          'nssf_number', 'phone_number', 'email', 'employment_type']:
                if field in request.data:
                    setattr(e, field, request.data[field])
            e.save()
            return Response(_emp(e))
        except Employee.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, emp_id):
        try:
            e = Employee.objects.get(id=emp_id)
            e.is_active = False
            e.end_date = timezone.now().date()
            e.save()
            return Response({'message': 'Employee deactivated'})
        except Employee.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class PayrollRunView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        runs = PayrollRun.objects.all()
        return Response({'count': runs.count(), 'results': [_run(r) for r in runs]})

    def post(self, request):
        year  = int(request.data.get('year',  timezone.now().year))
        month = int(request.data.get('month', timezone.now().month))
        try:
            run = PayrollCalculator.run_payroll(year, month, processed_by=request.user)
            return Response(_run(run), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PayrollRunDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        try:
            run = PayrollRun.objects.get(id=run_id)
            data = _run(run)
            data['payslips'] = [{
                'employee': p.employee.full_name,
                'employee_number': p.employee.employee_number,
                'gross': float(p.gross_salary),
                'paye': float(p.paye),
                'nhif': float(p.nhif),
                'nssf_employee': float(p.nssf_employee),
                'total_deductions': float(p.total_deductions),
                'net_pay': float(p.net_pay),
                'bank_account': p.employee.bank_account,
            } for p in run.payslips.select_related('employee').all()]
            return Response(data)
        except PayrollRun.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, run_id):
        try:
            run = PayrollRun.objects.get(id=run_id)
            action = request.data.get('action')
            if action == 'approve':
                run.approve(request.user)
                return Response({'message': 'Payroll approved', 'status': run.status})
            elif action == 'mark_paid':
                run.mark_paid()
                return Response({'message': 'Payroll marked as paid', 'status': run.status})
            return Response({'error': 'action must be approve or mark_paid'}, status=status.HTTP_400_BAD_REQUEST)
        except PayrollRun.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class PayrollCalculatorView(APIView):
    """Preview payslip calculation for a salary amount without saving."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from decimal import Decimal
            gross = Decimal(str(request.data['gross_salary']))
            paye = PayrollCalculator.calculate_paye(gross)
            nhif = PayrollCalculator.calculate_nhif(gross)
            nssf_emp, nssf_er = PayrollCalculator.calculate_nssf(gross)
            total_deductions = paye + nhif + nssf_emp
            net = gross - total_deductions

            return Response({
                'gross_salary': float(gross),
                'paye': float(paye),
                'nhif': float(nhif),
                'nssf_employee': float(nssf_emp),
                'nssf_employer': float(nssf_er),
                'total_deductions': float(total_deductions),
                'net_pay': float(net),
                'employer_total_cost': float(gross + nssf_er),
                'effective_tax_rate': round(float(paye) / float(gross) * 100, 1) if gross > 0 else 0,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
