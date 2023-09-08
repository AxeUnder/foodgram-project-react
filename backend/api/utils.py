# api/utils.py
from collections import namedtuple
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_authenticated


def generate_shopping_list_pdf(shopping_list, user):

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Arial', 10)

        header_text = 'FoodGram'
        footer_text = 'AxeUnder'
        w, h = doc.pagesize
        canvas.drawString(inch, h - 0.5 * inch, header_text)
        canvas.drawString(inch, 0.5 * inch, footer_text)

        canvas.restoreState()

    pdfmetrics.registerFont(
        TTFont('Arial', 'data/arial.ttf')
    )
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title='Shopping List')

    data = [
        ['Ингредиенты', 'Количество']
    ]
    for ingredient in shopping_list:
        data.append([ingredient[0], f'{ingredient[1]} {ingredient[2]}'])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    doc.build([table], onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)

    return buffer


ShoppingListItem = namedtuple('ShoppingListItem',
                              ['name', 'amount', 'measurement_unit'])


def process_shopping_list(recipe_list):
    ingredients = {}
    for recipe in recipe_list:
        for _ in recipe.recipe_ingredients.select_related('ingredient').all():
            key = (_.ingredient.name, _.ingredient.measurement_unit)
            if key not in ingredients:
                ingredients[key] = 0
            ingredients[key] += _.amount

    return [ShoppingListItem(name, amount, measurement_unit)
            for ((name, measurement_unit), amount) in ingredients.items()]
