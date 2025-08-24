
import os

import backend.crud as crud
import backend.models as models


def test_create_book_calls_session_and_returns(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.added = None
            self.committed = False
            self.refreshed = False

        def add(self, obj):
            self.added = obj

        def commit(self):
            self.committed = True

        def refresh(self, obj):
            self.refreshed = True

    db = FakeSession()
    book = crud.create_book(
        db=db,
        title="T",
        author="A",
        category="C",
        cover_image_url="U",
        file_path="/tmp/f.pdf",
    )
    assert isinstance(book, models.Book)
    assert (book.title, book.author, book.category, book.cover_image_url, book.file_path) == (
        "T",
        "A",
        "C",
        "U",
        "/tmp/f.pdf",
    )
    assert db.added is book and db.committed and db.refreshed


def test_delete_book_removes_files_and_commits(monkeypatch):
    class DummyBook:
        def __init__(self):
            self.id = 1
            self.title = "T"
            self.file_path = "/tmp/x.pdf"
            self.cover_image_url = "/tmp/c.png"

    class FakeQuery:
        def __init__(self, book):
            self._book = book

        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return self._book

    class FakeSession:
        def __init__(self, book):
            self._book = book
            self.deleted = None
            self.committed = False

        def query(self, _model):
            return FakeQuery(self._book)

        def delete(self, obj):
            self.deleted = obj

        def commit(self):
            self.committed = True

    removed = []

    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr(os, "remove", lambda p: removed.append(p))

    db = FakeSession(DummyBook())
    book = crud.delete_book(db, book_id=1)
    assert book is db.deleted
    assert db.committed
    # Se intentó borrar ambos archivos
    assert "/tmp/x.pdf" in removed and "/tmp/c.png" in removed


def test_delete_book_when_missing_returns_none(monkeypatch):
    class FakeQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return None

    class FakeSession:
        def __init__(self):
            self.committed = False

        def query(self, _model):
            return FakeQuery()

        def commit(self):
            self.committed = True

    db = FakeSession()
    book = crud.delete_book(db, book_id=999)
    assert book is None
    # commit no debe ser llamado
    assert db.committed is False

