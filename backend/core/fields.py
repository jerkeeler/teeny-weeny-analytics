from typing import Any, Optional, Tuple

from django.db.models import SlugField

from core.utils import gen_slug


class AutoSlugField(SlugField):
    description = 'A field that autogenerates a unique slug based on another field'

    def __init__(self, populated_from: Optional[bool] = None, *args: Any, **kwargs: Any):
        if populated_from is None:
            raise ValueError('populated_from has to be provided')
        self.populated_from = populated_from

        if 'null' not in kwargs:
            kwargs['null'] = True

        if 'blank' not in kwargs:
            kwargs['blank'] = True

        if 'unique' not in kwargs:
            kwargs['unique'] = True

        if 'db_index' not in kwargs:
            kwargs['db_index'] = True

        super().__init__(*args, **kwargs)

    def deconstruct(self) -> Tuple[str, str, Any, Any]:
        name, path, args, kwargs = super().deconstruct()
        if self.populated_from is not None:
            kwargs['populated_from'] = self.populated_from
        return name, path, args, kwargs

    def pre_save(self, model_instance: Any, add: Any) -> str:
        value = self.value_from_object(model_instance)

        if value:
            return value

        if hasattr(self, 'manager') and self.manager is not None:
            manager = self.manager
        else:
            manager = self.model._default_manager

        if self.populated_from is not None:
            attr_value = getattr(model_instance, self.populated_from)
        else:
            attr_value = ''

        # NOTE: There is a slight race condition here where another object is saved with the same slug just after the
        # filter. However, given in this instance we are appending a random token to the end of the slug the chances
        # are very very slim at the moment.
        while True:
            slug = gen_slug(attr_value)
            others = manager.filter(**{self.name: slug})
            if not others:
                # make the updated slug available as instance attribute
                setattr(model_instance, self.name, slug)
                return slug
