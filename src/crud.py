from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src import schemas
from src.core.exceptions.database_exceptions import BaseDatabaseException
from src.models.category import Category
from src.models.comment import Comment
from src.models.location import Location
from src.models.post import Post
from src.models.user import User


class RepositoryException(BaseDatabaseException):
    """Техническая ошибка уровня инфраструктуры."""

    def __init__(self, entity: str, operation: str, detail: str | None = None) -> None:
        error_detail = detail or f"DB error during {operation} for {entity}"
        super().__init__(error_detail)
        self.entity = entity
        self.operation = operation


class BaseRepository:
    entity = "entity"

    def _commit(self, db: Session, operation: str) -> None:
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise RepositoryException(self.entity, operation, str(exc.orig)) from exc
        except SQLAlchemyError as exc:
            db.rollback()
            raise RepositoryException(self.entity, operation, str(exc)) from exc


class UserRepository(BaseRepository):
    entity = "user"

    def get_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_nickname(self, db: Session, nickname: str):
        return db.query(User).filter(User.nickname == nickname).first()

    def get_many(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, user: schemas.users.UserCreate):
        db_user = User(**user.model_dump())
        db.add(db_user)
        self._commit(db, "create")
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, user_id: int, user_update: schemas.users.UserUpdate):
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(db_user, field, value)
        self._commit(db, "update")
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, user_id: int):
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        db.delete(db_user)
        self._commit(db, "delete")
        return db_user


class CategoryRepository(BaseRepository):
    entity = "category"

    def get_by_id(self, db: Session, category_id: int):
        return db.query(Category).filter(Category.id == category_id).first()

    def get_by_slug(self, db: Session, slug: str):
        return db.query(Category).filter(Category.slug == slug).first()

    def get_many(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Category).offset(skip).limit(limit).all()

    def create(self, db: Session, category: schemas.categories.CategoryCreate):
        db_category = Category(**category.model_dump())
        db.add(db_category)
        self._commit(db, "create")
        db.refresh(db_category)
        return db_category

    def update(self, db: Session, category_id: int, category_update: schemas.categories.CategoryUpdate):
        db_category = self.get_by_id(db, category_id)
        if not db_category:
            return None
        for field, value in category_update.model_dump(exclude_unset=True).items():
            setattr(db_category, field, value)
        self._commit(db, "update")
        db.refresh(db_category)
        return db_category

    def delete(self, db: Session, category_id: int):
        db_category = self.get_by_id(db, category_id)
        if not db_category:
            return None
        db.delete(db_category)
        self._commit(db, "delete")
        return db_category


class LocationRepository(BaseRepository):
    entity = "location"

    def get_by_id(self, db: Session, location_id: int):
        return db.query(Location).filter(Location.id == location_id).first()

    def get_many(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Location).offset(skip).limit(limit).all()

    def create(self, db: Session, location: schemas.locations.LocationCreate):
        db_location = Location(**location.model_dump())
        db.add(db_location)
        self._commit(db, "create")
        db.refresh(db_location)
        return db_location

    def update(self, db: Session, location_id: int, location_update: schemas.locations.LocationUpdate):
        db_location = self.get_by_id(db, location_id)
        if not db_location:
            return None
        for field, value in location_update.model_dump(exclude_unset=True).items():
            setattr(db_location, field, value)
        self._commit(db, "update")
        db.refresh(db_location)
        return db_location

    def delete(self, db: Session, location_id: int):
        db_location = self.get_by_id(db, location_id)
        if not db_location:
            return None
        db.delete(db_location)
        self._commit(db, "delete")
        return db_location


class PostRepository(BaseRepository):
    entity = "post"

    def get_by_id(self, db: Session, post_id: int):
        return db.query(Post).filter(Post.id == post_id).first()

    def get_many(self, db: Session, skip: int = 0, limit: int = 100, published_only: bool = True):
        query = db.query(Post)
        if published_only:
            query = query.filter(Post.is_published.is_(True))
        return query.order_by(desc(Post.pub_date)).offset(skip).limit(limit).all()

    def create(self, db: Session, post: schemas.posts.PostCreate, author_id: int):
        post_data = post.model_dump()
        post_data["author_id"] = author_id
        db_post = Post(**post_data)
        db.add(db_post)
        self._commit(db, "create")
        db.refresh(db_post)
        return db_post

    def update(self, db: Session, post_id: int, post_update: schemas.posts.PostUpdate):
        db_post = self.get_by_id(db, post_id)
        if not db_post:
            return None
        for field, value in post_update.model_dump(exclude_unset=True).items():
            setattr(db_post, field, value)
        self._commit(db, "update")
        db.refresh(db_post)
        return db_post

    def delete(self, db: Session, post_id: int):
        db_post = self.get_by_id(db, post_id)
        if not db_post:
            return None
        db.delete(db_post)
        self._commit(db, "delete")
        return db_post


class CommentRepository(BaseRepository):
    entity = "comment"

    def get_by_id(self, db: Session, comment_id: int):
        return db.query(Comment).filter(Comment.id == comment_id).first()

    def get_by_post(self, db: Session, post_id: int, skip: int = 0, limit: int = 100):
        return (
            db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, comment: schemas.comments.CommentCreate, author_id: int):
        comment_data = comment.model_dump()
        comment_data["author_id"] = author_id
        db_comment = Comment(**comment_data)
        db.add(db_comment)
        self._commit(db, "create")
        db.refresh(db_comment)
        return db_comment

    def update(self, db: Session, comment_id: int, comment_update: schemas.comments.CommentUpdate):
        db_comment = self.get_by_id(db, comment_id)
        if not db_comment:
            return None
        for field, value in comment_update.model_dump(exclude_unset=True).items():
            setattr(db_comment, field, value)
        self._commit(db, "update")
        db.refresh(db_comment)
        return db_comment

    def delete(self, db: Session, comment_id: int):
        db_comment = self.get_by_id(db, comment_id)
        if not db_comment:
            return None
        db.delete(db_comment)
        self._commit(db, "delete")
        return db_comment


user_repository = UserRepository()
category_repository = CategoryRepository()
location_repository = LocationRepository()
post_repository = PostRepository()
comment_repository = CommentRepository()