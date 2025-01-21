import pandas as pd
from django.core.management.base import BaseCommand
from chatbot.models import FoodItem
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Load food items in CSV and save the data"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, "foodsafetykorea_food.csv") 
        data = pd.read_csv(file_path)

        # 숫자형 데이터의 결측치를 모두 0으로 채우기
        numeric_columns = [
            "에너지(kcal)", "단백질(g)", "지방(g)", "탄수화물(g)", "당류(g)", 
            "식이섬유(g)", "나트륨(mg)", "콜레스테롤(mg)", "포화지방산(g)", "트랜스지방산(g)"
        ]
        data[numeric_columns] = data[numeric_columns].fillna(0)

        for _, row in data.iterrows():
            FoodItem.objects.get_or_create(
                food_code=row["식품코드"],
                defaults={
                    "name": row["식품명"],
                    "category": row["식품대분류명"],
                    "main_category": row["대표식품명"],
                    "nutrient_standard": row["영양성분함량기준량"],
                    "energy": row["에너지(kcal)"],
                    "protein": row["단백질(g)"],
                    "fat": row["지방(g)"],
                    "carbs": row["탄수화물(g)"],
                    "sugar": row["당류(g)"],
                    "fiber": row["식이섬유(g)"],
                    "sodium": row["나트륨(mg)"],
                    "cholesterol": row["콜레스테롤(mg)"],
                    "saturated_fat": row["포화지방산(g)"],
                    "trans_fat": row["트랜스지방산(g)"],
                    "weight": row["식품중량"],
                }
            )

        self.stdout.write(self.style.SUCCESS("[ALL FOOD DATA LOADED]"))
