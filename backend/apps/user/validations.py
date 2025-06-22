from abc import ABC, abstractmethod
from typing import Optional
from .dao import UserDao


class AbstractValidate(ABC):

    def __init__(self):
        self._next: Optional[AbstractValidate] = None

    def set_next(self, validate: "AbstractValidate"):
        self._next = validate
        return validate

    def validate(self, object):
        if self._next:
             self._next.validate(object)
        


class ValidationException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UserValidation(AbstractValidate):

    def validate(self, object):
        super().validate(object)
        if not isinstance(object, UserDao):
            raise ValidationException(
                "Running validation on a invalid object, this validation belongs to user dao."
            )
            

class UserIdValidation(AbstractValidate):

    def validate(self, object):
        super().validate(object)
        user: UserDao = object  # Casting
        if user.id is None:
            raise ValidationException(
                "Id is requried for user to perform this operation"
            )

