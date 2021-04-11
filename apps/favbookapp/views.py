from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
import bcrypt

# Create your views here.
def index(request):
    if 'id' in request.session.keys():
        return redirect ('/books')
    return render(request, "index.html")

def register(request):
    if request.method == 'POST':
        errors = User.objects.reg_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            password = request.POST['password']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  
            print(pw_hash)   

            new_user = User.objects.create(
                name=request.POST['name'], 
                alias=request.POST['alias'], 
                email=request.POST['email'], 
                password=pw_hash)
            print(new_user)
            request.session['user_id'] = new_user.id
            request.session['user_name'] = f"{new_user.name} {new_user.alias}"
            request.session['status'] = "registered"
            request.session['isloggedin'] = True

        return redirect("/books") # nunca renderizar en una publicación, ¡siempre redirigir!
    return redirect("/")

def login(request):
    if request.method == 'POST':
        errors = User.objects.log_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            user = User.objects.filter(alias=request.POST['alias'])
            if user:
                logged_user = user[0] #solo hay un usuario con ese alias, por lo que se usa [0]
                if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                    request.session['user_id'] = logged_user.id
                    request.session['user_name'] = f"{logged_user.name} {logged_user.alias}"
                    request.session['status'] = "Logged in"
                    request.session['isloggedin'] = True
            
                    return redirect('/books')
                else: 
                    messages.error(request, "password invalid")
        return redirect("/")

def logout(request):
    request.session.clear()
    request.session['isloggedin'] = False
    return redirect('/')
# **************************************

def books(request):
    if not request.session['isloggedin']:
        return redirect('/')
    else:
        context = {
            'all_books': Book.objects.all(),
        }
        return render (request, 'add_books.html', context)

def add_books(request):
    errors = Book.objects.book_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
            return redirect('/books')
    else:
        title = request.POST['form_add_title']
        desc = request.POST['form_add_desc']
        uploaded_by_id = request.session['user_id']
        uploaded_by = User.objects.get(id= uploaded_by_id)
        new_book = Book.objects.create(
            title = title,
            desc = desc,
            uploaded_by = uploaded_by
        )
        new_book.users_who_like.add(uploaded_by)
        return redirect('/books')

def edit_book(request, bookid):
    errors = Book.objects.book_validator_edit(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
            return redirect('/books/'+str(bookid))
    else:
        current_book = Book.objects.get(id=bookid)
        new_title = request.POST['form_edit_title']
        new_desc = request.POST['form_edit_desc']
        current_book.title = new_title
        current_book.desc = new_desc
        current_book.save()

        return redirect('/books/'+str(bookid))

def delete_book(request, bookid):
    current_book = Book.objects.get(id= bookid)
    book_creator_id = current_book.uploaded_by_id
    if (request.session['user_id']) == book_creator_id:
        current_book.delete()
        return redirect('/books')
    else: 
        return redirect('/')

def book_click(request, bookid):
    current_book = Book.objects.get(id= bookid)
    book_creator_id = current_book.uploaded_by_id
    if (request.session['user_id'] == book_creator_id):
        context = {
            'book': current_book,
            'users': current_book.users_who_like.all()
        }
        return render(request, 'edit_books.html', context)
    else:
        context = {
            'book': current_book,
            'users': current_book.users_who_like.all()
        }
        return render(request, 'view_books.html', context)

# ********************************** like and unlike

def like_book(request, bookid):
    current_book = Book.objects.get(id= bookid)
    current_user = User.objects.get(id = request.session['user_id'])
    current_book.users_who_like.add(current_user)
    request.session['liked_book'] = current_book.users_who_like.add

    return redirect('/books/'+str(bookid))


def unlike_book(request, bookid):
    current_book = Book.objects.get(id= bookid)
    current_user = User.objects.get(id= request.session['user_id'])
    current_book.users_who_like.remove(current_user)
    return redirect('/books/'+str(bookid))
