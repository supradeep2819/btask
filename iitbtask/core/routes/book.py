from typing import List
from ninja import Router
from pydantic import Json

from core.models import Book, Role, Status
from core.schemas import BookSchema, BookSchemaIn, DetailSchema
from django.core.exceptions import PermissionDenied


router = Router()

@router.post('/books/add/',response={200: BookSchema, 400: DetailSchema})
def add_book(request,payload:BookSchemaIn):
    data = payload.dict()
    try:
        if request.user.role != Role.LIBRARIAN.value:
            raise PermissionDenied("Only librarians can add books")
        if data['price'] <0:
            raise ValueError("Price cannot be negative")
        if data['status'] not in   [Status.AVAILABLE.value, Status.BORROWED.value]:
            raise ValueError("Book status can only be 'AVAILABLE' or 'BORROWED'.")
        book = Book.objects.create(**data)
        return book      
    except Exception as e:
        return 400, {"detail": str(e)}
    

@router.get('/books/',response={200: List[BookSchema], 400: DetailSchema})
def get_books(request):
    try:
        books = Book.objects.all()
        return books    
    except Exception as e:
        return 400, {"detail": str(e)}
    


@router.get('/books/{book_id}/', response={200: BookSchema, 400: DetailSchema})
def get_book_by_id(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        return book
    except Book.DoesNotExist:
        return 400, {"detail": "Book not found"}
    except Exception as e:
        return 400, {"detail": str(e)}
    
@router.delete('/books/{book_id}/', response={200: Json, 400: DetailSchema})
def delete_book(request, book_id):
    try:
        if request.user.role!= Role.LIBRARIAN.value:
            raise PermissionDenied("Only librarians can delete books")
        book = Book.objects.get(id=book_id)
        book.delete()
        return {"detail": "Book deleted successfully"}
    except Book.DoesNotExist:
        return 400, {"detail": "Book not found"}
    except Exception as e:
        return 400, {"detail": str(e)}
    

@router.put('/books/{book_id}/', response={200: BookSchema, 400: DetailSchema})
def update_book(request, book_id, payload: BookSchemaIn):
    try:
        if request.user.role != Role.LIBRARIAN.value:
            raise PermissionDenied("Only librarians can update books")

        # Fetch the book
        book = Book.objects.get(id=book_id)
        data = payload.dict()

        # Check if the status is valid
        if 'status' in data and data['status'] not in [Status.AVAILABLE.value, Status.BORROWED.value]:
            raise Exception("Book status can only be 'AVAILABLE' or 'BORROWED'.")

        # Update the book attributes
        for key, value in data.items():
            setattr(book, key, value)

        # Save the book instance
        book.save()
        return book

    except Book.DoesNotExist:
        return 400, {"detail": "Book not found"}
    except Exception as e:
        return 400, {"detail": str(e)}
