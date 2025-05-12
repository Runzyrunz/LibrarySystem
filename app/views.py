from django.shortcuts import render, redirect
from django.db.models import Count, Q, F
from django.utils import timezone
from .models import Book, Author, BookAuthor, Borrower, BookLoan, Fine
from .forms import BorrowerForm, FinePaymentForm, BorrowerRegistrationForm
from datetime import timedelta
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

@login_required
def search_books(request):
    query = request.GET.get("q", "")
    results = []
    
    if query:
        results = Book.objects.filter(
            Q(title__icontains=query) | Q(isbn__icontains=query) | Q(bookauthor__author__name__icontains=query)
        ).distinct().annotate(
            is_checked_out = Count('bookloan', filter=Q(bookloan__date_in__isnull=True))
        )
        
    return render(request, "search.html", {"books":results, "query":query})

@login_required
def checkout_book(request):
    if request.method == "POST":
        isbn = request.POST.get("isbn")
        card_id = request.POST.get("card_id")
        
        try:
            borrower=Borrower.objects.get(pk=card_id)
            active_loans=BookLoan.objects.filter(card_id=borrower, date_in__isnull=True)
            fines_due=Fine.objects.filter(loan_id__card_id=borrower, paid=False)
            book=Book.objects.get(pk=isbn)
            is_loaned=BookLoan.objects.filter(isbn=book, date_in__isnull=True).exists()
            
            if active_loans.count() >= 3:
                messages.error(request, "Borrower had reached maximum number of loans(3).")
            elif fines_due.exists():
                messages.error(request, "Borrower has unpaid fines. Cannot checkout.")
            elif is_loaned:
                messages.error(request, "Book is already checked out.")
            else:
                due_date=timezone.now().date() + timedelta(days=14)
                BookLoan.objects.create(
                    isbn=book,
                    card_id=borrower,
                    due_date=due_date
                )
                messages.success(request, f"Book {isbn} checked out to Borrower {card_id} until {due_date}")
                return redirect("checkout")
        except Borrower.DoesNotExist:
            messages.error(request, "Borrower not found")
        except Book.DoesNotExist:
            messages.error(request, "Book not found.")
        
    return render(request, "checkout.html")

@login_required
def checkin_book(request):
    loans=[]
    if request.method=="GET":
        query=request.GET.get("q","")
        if query:
            loans=BookLoan.objects.filter(
                Q(isbn__isbn__icontains=query) | Q(card_id__bname__icontains=query) | Q(card_id__card_id__icontains=query), date_in__isnull=True
            ).select_related('isbn', 'card_id')
            
    if request.method=="POST":
        loan_id=request.POST.get("loan_id")
        try:
            loan=BookLoan.objects.get(pk=loan_id)
            loan.date_in=timezone.now().date()
            loan.save()
            messages.success(request, f"Book {loan.isbn} returned by Borrower {loan.card_id}.")
            return redirect("checkin")
        except BookLoan.DoesNotExist:
            messages.error(request, "Loan not found.")
    
    return render(request, "checkin.html", {"loans":loans})

@login_required
def view_fines(request):
    fines_by_borrower = []
    card_id = request.GET.get("card_id")
    name_query = request.GET.get("name")

    borrowers = Borrower.objects.all()
    if card_id:
        borrowers = borrowers.filter(card_id=card_id)
    elif name_query:
        borrowers = borrowers.filter(bname__icontains=name_query)

    for borrower in borrowers:
        total_fine = Fine.objects.filter(loan_id__card_id=borrower, paid=False).aggregate(total=Sum('fine_amt'))['total']
        if total_fine:
            fines_by_borrower.append({"borrower": borrower, "fine_total": total_fine})

    if request.method == "POST":
        form = FinePaymentForm(request.POST)
        if form.is_valid():
            borrower_id = form.cleaned_data['card_id']
            unpaid_fines = Fine.objects.filter(loan_id__card_id=borrower_id, paid=False, loan_id__date_in__isnull=False)
            if unpaid_fines.exists():
                unpaid_fines.update(paid=True)
                messages.success(request, "Fines paid in full.")
            else:
                messages.error(request, "No unpaid fines eligible for payment.")
            return redirect("fines")
    else:
        form = FinePaymentForm()

    return render(request, "fines.html", {"form": form, "fines": fines_by_borrower})

@login_required
def add_borrower(request):
    if request.method=="POST":
        form = BorrowerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Borrower account created.")
            return redirect('add_borrower')
    else:
        form = BorrowerRegistrationForm()
    return render(request, 'borrower.html', {'form': form})

@login_required
def borrower_home(request):
    # Get the logged-in user's borrower profile
    borrower = getattr(request.user, 'borrower', None)

    if not borrower:
        messages.error(request, "No borrower profile linked to your account.")
        return redirect('search')  # or wherever you want to send them

    # List current checkouts
    checkouts = BookLoan.objects.filter(card_id=borrower, date_in__isnull=True)

    # Total unpaid fines (only if returned books)
    total_fines = Fine.objects.filter(
        loan_id__card_id=borrower,
        paid=False,
        loan_id__date_in__isnull=False
    ).aggregate(total=models.Sum('fine_amt'))['total'] or 0.00

    return render(request, 'borrower_home.html', {
        'borrower': borrower,
        'checkouts': checkouts,
        'total_fines': total_fines
    })

@login_required
def batch_checkout(request):
    if request.method == 'POST':
        isbns = request.POST.getlist('isbns')
        borrower = getattr(request.user, 'borrower', None)

        if not borrower:
            messages.error(request, "You must be logged in as a borrower.")
            return redirect('search')

        successful = 0
        skipped = []

        for isbn in isbns:
            book = Book.objects.filter(isbn=isbn).first()
            if not book:
                continue
            if BookLoan.objects.filter(isbn=book, date_in__isnull=True).exists():
                skipped.append(book.title)
                continue
            BookLoan.objects.create(
                isbn=book,
                card_id=borrower,
                due_date=timezone.now() + timezone.timedelta(days=14)
            )
            successful += 1

        if successful:
            messages.success(request, f"{successful} book(s) checked out successfully.")
        if skipped:
            messages.warning(request, f"Some books were skipped because they are not available: {', '.join(skipped)}")

    return redirect('search')
