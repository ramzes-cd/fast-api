"""Репозиторий для работы с пользователями"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.user import User
from src.schemas.users import UserCreate, UserUpdate
from src.core.exceptions.database_exceptions import (
    UserNotFoundException,
    UserByNicknameAlreadyExistsException,
    UserByEmailAlreadyExistsException
)


class UserRepository:
    """
    Репозиторий для операций с пользователями в БД
    """

    def __init__(self):
        """Инициализация репозитория"""
        pass

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получить список всех пользователей с пагинацией
        """
        return db.query(User).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, user_id: int) -> User:
        """
        Получить пользователя по ID.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException(f"User with id {user_id} not found")
        return user

    def get_by_nickname(self, db: Session, nickname: str) -> User:
        """
        Получить пользователя по никнейму
        """
        user = db.query(User).filter(User.nickname == nickname).first()
        if not user:
            raise UserNotFoundException(f"User with nickname {nickname} not found")
        return user

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Получить пользователя по email (без исключения)
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, user_data: UserCreate) -> User:
        """
        Создать нового пользователя
        """
        # Проверяем уникальность email перед созданием
        if self.get_by_email(db, user_data.email):
            raise UserByEmailAlreadyExistsException()

        db_user = User(
            nickname=user_data.nickname,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            bio_info=user_data.bio_info,
            email=user_data.email,
            password=user_data.password  # Пароль уже захэширован в use_case
        )

        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        except IntegrityError as e:
            db.rollback()
            # Анализируем какое именно ограничение нарушено
            if 'nickname' in str(e.orig):
                raise UserByNicknameAlreadyExistsException()
            elif 'email' in str(e.orig):
                raise UserByEmailAlreadyExistsException()
            raise

        return db_user

    def update(self, db: Session, nickname: str, user_data: UserUpdate) -> User:
        """
        Обновить данные пользователя
        """
        user = self.get_by_nickname(db, nickname)

        # Обновляем только переданные поля
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError as e:
            db.rollback()
            if 'email' in str(e.orig):
                raise UserByEmailAlreadyExistsException()
            raise

        return user

    def delete(self, db: Session, nickname: str) -> None:
        """
        Удалить пользователя
        """
        user = self.get_by_nickname(db, nickname)
        db.delete(user)
        db.commit()

    def exists_by_nickname(self, db: Session, nickname: str) -> bool:
        """
        Проверить существование пользователя по никнейму
        """
        return db.query(User).filter(User.nickname == nickname).first() is not None

    def exists_by_email(self, db: Session, email: str) -> bool:
        """
        Проверить существование пользователя по email
        """
        return db.query(User).filter(User.email == email).first() is not None
