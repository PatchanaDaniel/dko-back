from django.core.management.base import BaseCommand
from accounts import models as accounts_models
from waste_management import models as waste_models

# Correction: use getattr(module, attr), not getattr(list, attr)
waste_list = [attr for attr in dir(waste_models) if isinstance(getattr(waste_models, attr), type)]
accounts_list = [attr for attr in dir(accounts_models) if isinstance(getattr(accounts_models, attr), type)]

class Command(BaseCommand):
    help = "Supprime toutes les données du modèle MonModel"

    def handle(self, *args, **kwargs):
        for model_name in waste_list:
            model = getattr(waste_models, model_name)
            if hasattr(model, 'objects'):
                count, _ = model.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f"{count} objets supprimés de {model_name}."))
        for model_name in accounts_list:
            model = getattr(accounts_models, model_name)
            if hasattr(model, 'objects'):
                count, _ = model.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"{count} objets supprimés."))
