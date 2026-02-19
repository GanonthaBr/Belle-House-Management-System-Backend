# Generated manually on 2026-02-19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_invoice_tax_type_alter_invoice_tax_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_type',
            field=models.CharField(
                choices=[
                    ('PROFORMA', 'Facture Proforma'),
                    ('QUOTE', 'Devis'),
                    ('INVOICE', 'Facture')
                ],
                default='PROFORMA',
                help_text='Sélectionnez le type de document',
                max_length=20,
                verbose_name='2️⃣ Type de Document'
            ),
        ),
    ]
