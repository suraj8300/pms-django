from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Drug, Prescription
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages

def home(request):
    return render(request, 'pms/home.html')

@login_required
def add_drug(request):
    if request.method == 'POST':
        name = request.POST['name'].strip()
        try:
            quantity = int(request.POST['quantity'])
            if quantity < 0:
                return render(request, 'pms/add_drug.html', {'drugs': Drug.objects.all(), 'error': 'Quantity cannot be negative.'})
            if not name:
                return render(request, 'pms/add_drug.html', {'drugs': Drug.objects.all(), 'error': 'Name cannot be empty.'})
            # Handle expiration_date (optional, can be empty/null)
            expiration_date_str = request.POST.get('expiration_date', None)
            expiration_date = None
            if expiration_date_str:
                try:
                    expiration_date = timezone.datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return render(request, 'pms/add_drug.html', {'drugs': Drug.objects.all(), 'error': 'Invalid expiration date format. Use YYYY-MM-DD.'})
            drug = Drug.objects.create(name=name, quantity=quantity, expiration_date=expiration_date)
            return redirect('add_drug')
        except ValueError:
            return render(request, 'pms/add_drug.html', {'drugs': Drug.objects.all(), 'error': 'Quantity must be a number.'})
    drugs = Drug.objects.all()
    return render(request, 'pms/add_drug.html', {'drugs': drugs})

@login_required
def add_prescription(request):
    if request.method == 'POST':
        drug_id = request.POST['drug']
        patient_name = request.POST['patient_name'].strip()
        try:
            prescribed_amount = int(request.POST['prescribed_amount'])
            if prescribed_amount <= 0:
                return render(request, 'pms/add_prescription.html', {'drugs': Drug.objects.all(), 'prescriptions': Prescription.objects.all(), 'error': 'Prescribed amount must be greater than 0.'})
            if not patient_name:
                return render(request, 'pms/add_prescription.html', {'drugs': Drug.objects.all(), 'prescriptions': Prescription.objects.all(), 'error': 'Patient name cannot be empty.'})
            
            drug = Drug.objects.get(id=drug_id)
            current_date = timezone.now().date()
            if drug.expiration_date and drug.expiration_date < current_date:
                return render(request, 'pms/add_prescription.html', {'drugs': Drug.objects.all(), 'prescriptions': Prescription.objects.all(), 'error': f'Cannot prescribe {drug.name}—it is expired on {drug.expiration_date}.'})
            if prescribed_amount > drug.quantity:
                return render(request, 'pms/add_prescription.html', {'drugs': Drug.objects.all(), 'prescriptions': Prescription.objects.all(), 'error': 'Prescribed amount exceeds available stock.'})
            
            drug.quantity -= prescribed_amount
            drug.save()
            Prescription.objects.create(drug=drug, patient_name=patient_name, prescribed_amount=prescribed_amount)
            return redirect('add_prescription')
        except ValueError:
            return render(request, 'pms/add_prescription.html', {'drugs': Drug.objects.all(), 'prescriptions': Prescription.objects.all(), 'error': 'Prescribed amount must be a number.'})
        except Drug.DoesNotExist:
            return render(request, 'pms/add_prescription.html', {'drugs': Drug.objects.all(), 'prescriptions': Prescription.objects.all(), 'error': 'Drug not found.'})
    
    drugs = Drug.objects.all()
    prescriptions = Prescription.objects.all()
    return render(request, 'pms/add_prescription.html', {'drugs': drugs, 'prescriptions': prescriptions})

@login_required
@require_POST
def delete_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    drug = prescription.drug
    # Restore the stock (add back the prescribed amount)
    drug.quantity += prescription.prescribed_amount
    drug.save()
    prescription.delete()
    return redirect('add_prescription')

@login_required
@require_POST
def delete_drug(request, drug_id):
    drug = get_object_or_404(Drug, id=drug_id)
    
    # Get the quantity to remove (if provided)
    try:
        remove_quantity = int(request.POST.get('remove_quantity', 0))
        if remove_quantity < 0:
            messages.error(request, "Cannot remove negative quantity.")
            return redirect('add_drug')
        
        # If remove quantity is specified and less than total quantity, just reduce the quantity
        if 0 < remove_quantity < drug.quantity:
            drug.quantity -= remove_quantity
            drug.save()
            messages.success(request, f"Removed {remove_quantity} units of {drug.name}.")
            return redirect('add_drug')
        
        # If remove quantity equals or exceeds total quantity, delete the drug (if possible)
        if remove_quantity >= drug.quantity or remove_quantity == 0:
            # Check if there are any prescriptions for this drug before deleting
            if Prescription.objects.filter(drug=drug).exists():
                messages.error(request, "Cannot delete this drug because it has associated prescriptions.")
                return redirect('add_drug')
            drug_name = drug.name
            drug.delete()
            messages.success(request, f"{drug_name} has been removed from inventory.")
    except ValueError:
        messages.error(request, "Invalid quantity value.")
    
    return redirect('add_drug')

def user_logout(request):
    logout(request)
    return redirect('/')

# New view to update drug quantity (increase/decrease)
@login_required
def update_drug_quantity(request, drug_id):
    drug = get_object_or_404(Drug, id=drug_id)
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            quantity = int(request.POST.get('quantity', 0))
            
            if quantity < 0:
                messages.error(request, "Quantity cannot be negative.")
                return redirect('add_drug')
                
            if action == 'add':
                drug.quantity += quantity
                messages.success(request, f"Added {quantity} units to {drug.name}.")
            elif action == 'subtract':
                if quantity > drug.quantity:
                    messages.error(request, f"Cannot remove {quantity} units. Only {drug.quantity} available.")
                    return redirect('add_drug')
                drug.quantity -= quantity
                messages.success(request, f"Removed {quantity} units from {drug.name}.")
            
            drug.save()
        except ValueError:
            messages.error(request, "Invalid quantity value.")
            
    return redirect('add_drug')