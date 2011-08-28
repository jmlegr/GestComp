from django.db.models import DateTimeField
import datetime

class AddedDateTimeField(DateTimeField):
    def get_internal_type(self):
        return DateTimeField.__name__
    def pre_save(self, model_instance, add):
        if model_instance.id is None:
            return datetime.datetime.now()
        else:
            return getattr(model_instance, self.attname)
           

class ModifiedDateTimeField(DateTimeField):
    def get_internal_type(self):
        return DateTimeField.__name__
    def pre_save(self, model_instance, add):
        return datetime.datetime.now()